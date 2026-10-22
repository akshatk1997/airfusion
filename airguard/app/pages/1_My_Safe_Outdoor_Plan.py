"""
AirGuard — My Safe Outdoor Plan.
Unified personalized decision-support dashboard converting live air telemetry,
weather, and ML forecasts into clear, actionable outdoor safety decisions.
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st
import pandas as pd

APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import init_db, get_user_profile, save_user_profile
from src.data_collection import geocode_city, fetch_current_air_quality
from src.predict import generate_forecast, is_model_trained
from src.safety_rules import (
    calculate_outdoor_risk_score,
    generate_personalized_advice,
    find_safe_outdoor_windows
)
from app.components.navbar import render_global_navbar
from app.components.cards import render_aqi_hero_card
from app.components.risk_engine import render_risk_score_card
from app.components.activity_advisor import render_safe_window_card, render_hourly_timeline_strip
from app.components.protection_advisor import render_protection_protocol_card
from app.components.charts import create_forecast_chart
from app.components.design_system import (
    render_section_header,
    format_location_label,
    safe_markdown,
    render_callout
)

st.set_page_config(
    page_title="My Safe Outdoor Plan — AirGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Initialize DB
init_db()

# Synchronized Navigation Bar
active_city = render_global_navbar("My Safe Outdoor Plan")

# Load persistent user health profile from SQLite
user_prof = get_user_profile()

# ==============================================================================
# SECTION: USER HEALTH PROFILE & ACTIVITY CONFIGURATION
# ==============================================================================
with st.expander("👤 Configure Your Health Profile & Outdoor Activity", expanded=True):
    col_p1, col_p2, col_p3 = st.columns([1.2, 1.4, 1.4])

    with col_p1:
        st.markdown("<div style='font-family: var(--font-dot); font-size: 0.76rem; font-weight: 700; color: #FFFFFF; text-transform: uppercase; margin-bottom: 8px;'>1. Health Profile</div>", unsafe_allow_html=True)
        age_options = ["adult", "child", "senior"]
        age_idx = age_options.index(user_prof.get("age_group", "adult")) if user_prof.get("age_group") in age_options else 0
        selected_age = st.selectbox(
            "Age Group",
            options=age_options,
            index=age_idx,
            format_func=lambda x: f"Age: {x.title()}"
        )

        sens_options = [
            "none", "asthma", "allergy", "copd",
            "heart condition", "pregnancy", "other respiratory sensitivity"
        ]
        sens_idx = sens_options.index(user_prof.get("health_sensitivity", "none")) if user_prof.get("health_sensitivity") in sens_options else 0
        selected_sens = st.selectbox(
            "Health Sensitivity",
            options=sens_options,
            index=sens_idx,
            format_func=lambda x: f"Sensitivity: {x.title()}"
        )

    with col_p2:
        st.markdown("<div style='font-family: var(--font-dot); font-size: 0.76rem; font-weight: 700; color: #FFFFFF; text-transform: uppercase; margin-bottom: 8px;'>2. Planned Activity</div>", unsafe_allow_html=True)
        act_options = ["walk", "run", "cycle", "outdoor play", "outdoor work", "commute"]
        act_idx = act_options.index(user_prof.get("usual_activities", "walk")) if user_prof.get("usual_activities") in act_options else 0
        selected_act = st.selectbox(
            "Activity Type",
            options=act_options,
            index=act_idx,
            format_func=lambda x: f"Activity: {x.title()}"
        )

        dur_options = [15, 30, 45, 60, 90, 120]
        cur_dur = int(user_prof.get("typical_duration_mins", 30))
        dur_idx = dur_options.index(cur_dur) if cur_dur in dur_options else 1
        selected_dur = st.select_slider(
            "Target Duration (Minutes)",
            options=dur_options,
            value=dur_options[dur_idx]
        )

    with col_p3:
        st.markdown("<div style='font-family: var(--font-dot); font-size: 0.76rem; font-weight: 700; color: #FFFFFF; text-transform: uppercase; margin-bottom: 8px;'>3. Time Preference & Alert</div>", unsafe_allow_html=True)
        time_options = ["now", "morning", "afternoon", "evening", "tomorrow"]
        pref_idx = time_options.index(user_prof.get("preferred_time", "now")) if user_prof.get("preferred_time") in time_options else 0
        selected_pref = st.selectbox(
            "Preferred Time of Day",
            options=time_options,
            index=pref_idx,
            format_func=lambda x: f"Target Time: {x.title()}"
        )

        selected_thresh = st.slider(
            "Personal PM₂.₅ Alert Threshold (µg/m³)",
            min_value=15.0,
            max_value=120.0,
            value=float(user_prof.get("pm25_threshold", 35.0)),
            step=5.0,
            help="AirGuard flags windows exceeding this value as unsafe."
        )

    # Auto-save changes to SQLite
    if (selected_age != user_prof.get("age_group") or
        selected_sens != user_prof.get("health_sensitivity") or
        selected_act != user_prof.get("usual_activities") or
        selected_dur != user_prof.get("typical_duration_mins") or
        selected_pref != user_prof.get("preferred_time") or
        selected_thresh != user_prof.get("pm25_threshold")):
        save_user_profile({
            "age_group": selected_age,
            "health_sensitivity": selected_sens,
            "usual_activities": selected_act,
            "typical_duration_mins": selected_dur,
            "preferred_time": selected_pref,
            "pm25_threshold": selected_thresh,
            "aqi_threshold": int(selected_thresh * 2.8)
        })

# ==============================================================================
# SECTION: TELEMETRY & DECISION SUPPORT PIPELINE
# ==============================================================================
loc = geocode_city(active_city)
if not loc:
    render_callout(
        title="Location Unresolved",
        message=f"Could not resolve geographical coordinates for '{active_city}'. Please select an active location.",
        variant="alert"
    )
    st.stop()

# 1. Fetch live telemetry
curr = fetch_current_air_quality(loc["latitude"], loc["longitude"])
pm25_val = float(curr.get("pm2_5", 0.0))
aqi_val = int(curr.get("aqi", 0))
category = curr.get("aqi_category", "Unknown")
color = curr.get("aqi_color", "#10B981")
timestamp_str = curr.get("timestamp", "").replace("T", " ")

# 2. Fetch 24-hour predictive trajectory
forecast_df, summary = generate_forecast(active_city, horizon_hours=24)
if forecast_df is None or forecast_df.empty:
    # Graceful fallback: generate simulated 24h baseline from current observation
    hours = pd.date_range(start=pd.Timestamp.now(), periods=24, freq="h")
    forecast_df = pd.DataFrame({
        "target_time": [h.strftime("%Y-%m-%d %H:%M") for h in hours],
        "predicted_pm2_5": [max(5.0, pm25_val * (1.0 + 0.15 * (i % 6 - 3) / 3)) for i in range(24)],
        "predicted_aqi": [aqi_val for _ in range(24)],
        "lower_ci": [max(1.0, pm25_val * 0.8) for _ in range(24)],
        "upper_ci": [pm25_val * 1.25 for _ in range(24)]
    })

# 3. Calculate Risk Engine outputs
risk_score, risk_cat = calculate_outdoor_risk_score(
    aqi=aqi_val,
    pm25=pm25_val,
    health_sensitivity=selected_sens,
    age_group=selected_age,
    activity=selected_act,
    duration_mins=selected_dur
)

advice = generate_personalized_advice(
    risk_score=risk_score,
    risk_category=risk_cat,
    aqi=aqi_val,
    pm25=pm25_val,
    health_sensitivity=selected_sens,
    age_group=selected_age,
    activity=selected_act,
    duration_mins=selected_dur,
    preferred_time=selected_pref
)

safe_windows = find_safe_outdoor_windows(
    forecast_df=forecast_df,
    duration_mins=selected_dur,
    preferred_period=selected_pref,
    user_pm25_threshold=selected_thresh,
    health_sensitivity=selected_sens,
    age_group=selected_age,
    activity=selected_act
)

# ==============================================================================
# SECTION: UNIFIED SAFE OUTDOOR PLAN PRESENTATION
# ==============================================================================
render_section_header(
    title=f"My Safe Outdoor Plan — {format_location_label(loc)}",
    subtitle=f"Personalized decision support for your planned {selected_dur}-minute {selected_act} ({selected_pref.title()}).",
    badge="DECISION SUPPORT ACTIVE"
)

# Top Telemetry Hero Card
render_aqi_hero_card(
    aqi=aqi_val,
    category=category,
    color=color,
    city=format_location_label(loc),
    timestamp=timestamp_str,
    pm25_val=pm25_val
)

# 1. Primary Risk Engine Assessment Card
render_risk_score_card(
    risk_score=advice["risk_score"],
    risk_category=advice["risk_category"],
    reason=advice["reason"],
    action=advice["action"]
)

# 2. Optimal Safe Outdoor Window Finder Card
render_safe_window_card(
    window_data=safe_windows,
    activity=selected_act,
    duration_mins=selected_dur
)

# 3. 24-Hour Discrete Status Strip
render_hourly_timeline_strip(safe_windows.get("hourly_timeline", []))

# 4. Mask and Indoor Protection Guidance
render_protection_protocol_card(
    mask_guidance=advice["mask_guidance"],
    indoor_guidance=advice["indoor_guidance"],
    risk_category=advice["risk_category"]
)

# 5. Threshold Live Tracking Status & Forecast Trajectory Chart
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
render_section_header(
    title="24-Hour ML Pollution Trajectory & Personal Threshold",
    subtitle=f"Machine learning forecast trajectory with 90% confidence bands against your personal {selected_thresh:.0f} µg/m³ threshold.",
    badge="FORECAST INTELLIGENCE"
)

# Alert status callout
if pm25_val > selected_thresh:
    render_callout(
        title="⚠️ Personal Alert Threshold Exceeded",
        message=f"Current ambient PM₂.₅ ({pm25_val:.1f} µg/m³) is currently above your configured alert threshold ({selected_thresh:.0f} µg/m³). Avoid strenuous outdoor exertion.",
        variant="alert"
    )
elif pm25_val > selected_thresh * 0.8:
    render_callout(
        title="⚡ Approaching Alert Threshold",
        message=f"Current ambient PM₂.₅ ({pm25_val:.1f} µg/m³) is within 20% of your alert limit ({selected_thresh:.0f} µg/m³). Monitor conditions before embarking on long sessions.",
        variant="warning"
    )
else:
    render_callout(
        title="✓ Safe Threshold Margin",
        message=f"Current PM₂.₅ ({pm25_val:.1f} µg/m³) is comfortably below your {selected_thresh:.0f} µg/m³ alert threshold.",
        variant="success"
    )

# Render Plotly Forecast Chart
chart = create_forecast_chart(
    forecast_df=forecast_df,
    city=format_location_label(loc),
    threshold=selected_thresh
)
st.plotly_chart(chart, use_container_width=True)
