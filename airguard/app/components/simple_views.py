"""
Simple Mode Presentation Views for AirGuard.
Orchestrates clear, non-technical, friendly user experiences.
Reuses the exact same underlying telemetry, ML forecasting, and risk-engine logic.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional

from src.database import get_user_profile, save_user_profile
from src.data_collection import geocode_city, fetch_current_air_quality
from src.predict import generate_forecast
from src.safety_rules import (
    calculate_outdoor_risk_score,
    generate_personalized_advice,
    find_safe_outdoor_windows
)
from app.components.design_system import format_location_label, safe_markdown
from app.components.simple_cards import (
    render_air_safety_card,
    render_simple_timeline,
    render_todays_tip,
    render_simple_alert_setup,
    render_simple_disclaimer
)


def render_simple_home(active_city: str) -> None:
    """
    Renders the dedicated Simple Mode homepage for AirGuard.
    Heading: 'Is it safe for me to go outside today?'
    """
    # Load user profile from SQLite
    user_prof = get_user_profile()
    age_group = user_prof.get("age_group", "adult")
    sensitivity = user_prof.get("health_sensitivity", "none")
    usual_activity = user_prof.get("usual_activities", "walk")
    duration_mins = int(user_prof.get("typical_duration_mins", 30))
    preferred_time = user_prof.get("preferred_time", "now")
    threshold = float(user_prof.get("pm25_threshold", 35.0))

    # Geocode active city
    loc = geocode_city(active_city)
    if not loc:
        st.error(f"Could not find coordinates for '{active_city}'. Please pick a city from the top bar.")
        return

    city_display = format_location_label(loc)

    # 1. Fetch live telemetry (shared pipeline)
    curr = fetch_current_air_quality(loc["latitude"], loc["longitude"])
    pm25_val = float(curr.get("pm2_5", 0.0))
    aqi_val = int(curr.get("aqi", 0))
    temp_val = float(curr.get("temperature", 24.0)) if curr.get("temperature") is not None else 24.0
    humidity_val = float(curr.get("humidity", 50.0)) if curr.get("humidity") is not None else 50.0
    wind_val = float(curr.get("wind_speed", 2.0)) if curr.get("wind_speed") is not None else 2.0

    # 2. Fetch 24-hour forecast
    forecast_df, _ = generate_forecast(active_city, horizon_hours=24)
    if forecast_df is None or forecast_df.empty:
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
        health_sensitivity=sensitivity,
        age_group=age_group,
        activity=usual_activity,
        duration_mins=duration_mins
    )

    advice = generate_personalized_advice(
        risk_score=risk_score,
        risk_category=risk_cat,
        aqi=aqi_val,
        pm25=pm25_val,
        health_sensitivity=sensitivity,
        age_group=age_group,
        activity=usual_activity,
        duration_mins=duration_mins,
        preferred_time=preferred_time
    )

    safe_windows = find_safe_outdoor_windows(
        forecast_df=forecast_df,
        duration_mins=duration_mins,
        preferred_period=preferred_time,
        user_pm25_threshold=threshold,
        health_sensitivity=sensitivity,
        age_group=age_group,
        activity=usual_activity
    )

    # Friendly Direct Answer Translation
    if risk_cat == "Low":
        answer = "Yes! The air is clean and safe to go outside right now."
        status_level = "Safe"
    elif risk_cat == "Moderate":
        if sensitivity != "none" or age_group in ["child", "senior"]:
            answer = "Caution: Air pollution is slightly elevated. Sensitive individuals should take it easy."
            status_level = "Caution"
        else:
            answer = "Mostly Safe: Air quality is acceptable for healthy adults."
            status_level = "Moderate"
    elif risk_cat == "High":
        answer = "Not recommended right now: Air pollution is high. Consider moving activities indoors."
        status_level = "Avoid"
    else:
        answer = "High Risk: Stay indoors. Outdoor air is currently unhealthy for everyone."
        status_level = "High Risk"

    # Friendly Reason Translation
    if pm25_val > 55:
        simple_reason = f"Tiny harmful particles in the air are high right now ({pm25_val:.0f} µg/m³)."
    elif pm25_val > 35:
        simple_reason = "Air pollution is moderately high, especially for children, seniors, and sensitive lungs."
    else:
        simple_reason = "Pollution levels are currently within safe, healthy boundaries."

    if sensitivity != "none":
        simple_reason += f" Your profile is set for {sensitivity.title()} sensitivity."

    # Best safe window and avoid periods
    best_win = safe_windows.get("best_window", "Now")
    avoid_list = safe_windows.get("avoid_periods", [])
    hourly_timeline = safe_windows.get("hourly_timeline", [])

    # Main Homepage Heading
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h1 style="font-family: var(--font-heading); font-size: 2.1rem; font-weight: 800; color: #FFFFFF; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                Is it safe for me to go outside today?
            </h1>
            <p style="font-family: var(--font-sans); font-size: 0.95rem; color: #888888; margin: 0;">
                Personalized, friendly outdoor guidance based on live air quality and 24-hour forecasts.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Large Air Safety Card
    render_air_safety_card(
        city_name=city_display,
        status_level=status_level,
        answer_text=answer,
        best_window=best_win,
        avoid_hours=avoid_list,
        main_reason=simple_reason,
        recommendation=advice.get("action", f"Safe for a {duration_mins}-minute {usual_activity}."),
        mask_tip=advice.get("mask_guidance")
    )

    # 2. Simple 24-Hour Timeline
    render_simple_timeline(hourly_timeline)

    # 3. Two-Column Row: Today's Tip + Simple Alert Setup
    col_tip, col_alert = st.columns([1.1, 1.0])

    with col_tip:
        render_todays_tip(aqi=aqi_val, wind_speed=wind_val, humidity=humidity_val)

        # Friendly quick navigation shortcuts
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 8px;">
                    🎯 What would you like to do?
                </div>
                """,
                unsafe_allow_html=True
            )
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🛡️ Customize Safe Plan", key="simple_btn_plan", use_container_width=True):
                    st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")
            with col_b2:
                if st.button("📡 View Weather & Air Details", key="simple_btn_live", use_container_width=True):
                    st.switch_page("pages/2_Live_Tracking.py")

    with col_alert:
        def _handle_alert_save(new_threshold_val: float):
            prof = get_user_profile()
            prof["pm25_threshold"] = new_threshold_val
            prof["aqi_threshold"] = int(new_threshold_val * 2.8)
            save_user_profile(prof)

        render_simple_alert_setup(
            current_threshold=threshold,
            on_save_callback=_handle_alert_save
        )

    # 4. Prominent Safety Disclaimer
    render_simple_disclaimer()
