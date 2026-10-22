"""
Live Atmospheric Tracking & Personal Threshold Alert Center for AirGuard.
Features real-time multi-pollutant telemetry, meteorological dynamics,
personal threshold breach tracking, and advance 24h peak warnings.
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CACHE_TTL_SECONDS, HIGH_POLLUTION_PM25_THRESHOLD
from src.data_collection import geocode_city, fetch_current_air_quality
from src.database import (
    get_or_create_location,
    upsert_air_quality_dataframe,
    get_user_profile,
    save_user_profile,
    save_alert,
    fetch_alerts,
    fetch_alert_logs
)
from src.predict import generate_forecast, is_model_trained
from src.alerts import evaluate_alerts_for_city
from app.components.navbar import render_global_navbar
from app.components.cards import render_aqi_hero_card
from app.components.health_advisory import render_health_advisory_panel
from app.components.design_system import (
    render_section_header,
    render_metric_tile,
    render_callout,
    render_badge,
    format_location_label,
    safe_markdown,
    ICONS
)

st.set_page_config(
    page_title="Live Tracking & Alerts — AirGuard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="auto"
)

# Render Global Navbar
target_city = render_global_navbar("Live Tracking")

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_live_data(city_name: str):
    loc_meta = geocode_city(city_name)
    if not loc_meta:
        return None, None
    curr_data = fetch_current_air_quality(loc_meta["latitude"], loc_meta["longitude"])
    return loc_meta, curr_data

# Header and Top Controls
render_section_header(
    title=f"Atmospheric Telemetry & Live Tracking — {target_city}",
    subtitle="Real-time multi-pollutant concentrations, meteorological parameters, and personal alert defense monitoring.",
    badge="GROUND TELEMETRY & THRESHOLD DEFENSE"
)

col_ctrl1, col_ctrl2 = st.columns([2, 1.2])

with col_ctrl2:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🔄 Refresh Telemetry", key="btn_refresh_live", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with c_btn2:
        if st.button("🛡️ Outdoor Plan →", key="btn_goto_plan", use_container_width=True):
            st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")

# Fetch live atmospheric telemetry
with st.spinner(f"Ingesting real-time atmospheric telemetry for {target_city}..."):
    loc_meta, curr_data = get_live_data(target_city)

if not loc_meta or not curr_data:
    render_callout(
        title="Location Resolution Error",
        message=f"Could not retrieve telemetry for '{target_city}'. Please verify coordinates or select another location.",
        variant="alert",
        icon="alert"
    )
    st.stop()

# Store live point in SQLite
try:
    loc_id = get_or_create_location(
        city=loc_meta["city"],
        latitude=loc_meta["latitude"],
        longitude=loc_meta["longitude"],
        country=loc_meta.get("country", ""),
        state=loc_meta.get("state", "")
    )
    df_live = pd.DataFrame([{
        "timestamp": curr_data.get("timestamp"),
        "aqi": curr_data.get("aqi"),
        "aqi_category": curr_data.get("aqi_category"),
        "pm2_5": curr_data.get("pm2_5"),
        "pm10": curr_data.get("pm10"),
        "no2": curr_data.get("no2"),
        "o3": curr_data.get("o3"),
        "so2": curr_data.get("so2"),
        "co": curr_data.get("co"),
        "temperature": curr_data.get("temperature"),
        "humidity": curr_data.get("humidity"),
        "wind_speed": curr_data.get("wind_speed"),
        "wind_direction": curr_data.get("wind_direction"),
        "pressure": curr_data.get("pressure"),
    }])
    upsert_air_quality_dataframe(df_live, loc_id)
except Exception:
    pass

curr_pm = float(curr_data.get("pm2_5", 0.0))
curr_aqi = int(curr_data.get("aqi", 0))
category = curr_data.get("aqi_category", "Moderate")
color = curr_data.get("aqi_color", "#10B981")
timestamp_str = curr_data.get("timestamp", "").replace("T", " ")

# Retrieve user profile & threshold settings
profile = get_user_profile()
user_threshold = float(profile.get("aqi_alert_threshold", 55.0))

# Forecast projection for early warning calculation
forecast_df = None
if is_model_trained():
    try:
        forecast_df, _ = generate_forecast(target_city, horizon_hours=24)
    except Exception:
        pass

# ----------------- SECTION 1: PERSONAL THRESHOLD STATUS CARD & EARLY WARNINGS -----------------
st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Determine threshold status
pct_threshold = (curr_pm / user_threshold) if user_threshold > 0 else 1.0

if pct_threshold >= 1.0:
    thresh_status = "THRESHOLD CROSSED"
    thresh_badge_color = "#D71921"
    thresh_text_color = "#FFFFFF"
    thresh_desc = f"Current PM₂.₅ ({curr_pm:.1f} µg/m³) has exceeded your personal safety limit ({user_threshold:.1f} µg/m³)."
elif pct_threshold >= 0.80:
    thresh_status = "APPROACHING THRESHOLD"
    thresh_badge_color = "#EAB308"
    thresh_text_color = "#FFFFFF"
    thresh_desc = f"Current PM₂.₅ ({curr_pm:.1f} µg/m³) is within 20% of your threshold ({user_threshold:.1f} µg/m³). Precaution advised."
else:
    thresh_status = "SAFE (BELOW THRESHOLD)"
    thresh_badge_color = "#22C55E"
    thresh_text_color = "#FFFFFF"
    thresh_desc = f"Current PM₂.₅ ({curr_pm:.1f} µg/m³) is comfortably below your limit ({user_threshold:.1f} µg/m³)."

# Early warning analysis across 24h forecast
early_warning_msg = None
avoid_period_msg = None

if forecast_df is not None and not forecast_df.empty:
    exceedances = forecast_df[forecast_df["predicted_pm2_5"] >= user_threshold]
    if not exceedances.empty:
        first_exceed = exceedances.iloc[0]
        h_until = int(first_exceed["horizon_hours"])
        t_time = first_exceed["target_time"]
        if h_until == 0:
            early_warning_msg = f"Threshold currently breached. Expected to peak at {first_exceed['predicted_pm2_5']:.1f} µg/m³."
        else:
            early_warning_msg = f"PM₂.₅ is projected to cross your threshold in {h_until} hour{'s' if h_until > 1 else ''} (~{t_time})."

        # Find continuous avoid window
        peak_hours = exceedances["target_time"].tolist()
        if len(peak_hours) >= 2:
            avoid_period_msg = f"Avoid outdoor exposure between {peak_hours[0][-5:]} and {peak_hours[-1][-5:]} when pollution spikes."
        else:
            avoid_period_msg = f"Avoid outdoor exposure near {peak_hours[0][-5:]} when peak concentration occurs."

# Render Threshold Defense Strip
st.markdown(f"""
<div class="ag-card" style="border: 1px solid #242424; background: #0E0E0E; padding: var(--space-4); margin-bottom: var(--space-4);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-3); flex-wrap: wrap; gap: 8px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span class="ag-pulse-dot" style="background-color: {thresh_badge_color};"></span>
            <span style="font-family: var(--font-dot); font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #FFFFFF;">
                LIVE ALERT DEFENSE STATUS
            </span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #888888;">STATUS:</span>
            <span style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 700; padding: 2px 10px; border-radius: 2px; background: {thresh_badge_color}; color: #000000; text-transform: uppercase; letter-spacing: 0.05em;">
                {thresh_status}
            </span>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: var(--space-3);">
        <div style="padding: 12px; border: 1px solid #1E1E1E; background: #121212;">
            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #888888; text-transform: uppercase;">CURRENT PM₂.₅</div>
            <div style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 700; color: #FFFFFF;">{curr_pm:.1f} <span style="font-size: 0.8rem; font-weight: 400; color: #888888;">µg/m³</span></div>
            <div style="font-family: var(--font-sans); font-size: 0.75rem; color: #AAAAAA;">AQI {curr_aqi} ({category})</div>
        </div>
        <div style="padding: 12px; border: 1px solid #1E1E1E; background: #121212;">
            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #888888; text-transform: uppercase;">PERSONAL THRESHOLD</div>
            <div style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 700; color: #FFFFFF;">{user_threshold:.1f} <span style="font-size: 0.8rem; font-weight: 400; color: #888888;">µg/m³</span></div>
            <div style="font-family: var(--font-sans); font-size: 0.75rem; color: #AAAAAA;">Profile sensitivity limit</div>
        </div>
        <div style="padding: 12px; border: 1px solid #1E1E1E; background: #121212;">
            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #888888; text-transform: uppercase;">EXPOSURE RATIO</div>
            <div style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 700; color: {'#D71921' if pct_threshold >= 1.0 else '#FFFFFF'};">{pct_threshold * 100:.0f}%</div>
            <div style="font-family: var(--font-sans); font-size: 0.75rem; color: #AAAAAA;">{'Exceeded limit' if pct_threshold >= 1.0 else 'Within safety margin'}</div>
        </div>
    </div>
    <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #CCCCCC; line-height: 1.5; border-top: 1px solid #1C1C1C; padding-top: 10px;">
        <strong>Advisory:</strong> {thresh_desc}
        {f"<br><span style='color: #EAB308;'>⚠️ <strong>Early Warning:</strong> {early_warning_msg}</span>" if early_warning_msg else ""}
        {f"<br><span style='color: #F87171;'>⛔ <strong>Avoid Guidance:</strong> {avoid_period_msg}</span>" if avoid_period_msg else ""}
    </div>
</div>
""", unsafe_allow_html=True)

# Personal Threshold Quick Adjuster Modal / Expander
with st.expander("⚙️ Configure Personal PM₂.₅ Alert Threshold", expanded=False):
    st.markdown("""
    <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #888888; margin-bottom: 12px;">
        Adjust your personal air quality threshold below. Alerts and early warnings across all tracking screens adapt instantly to this preference.
    </div>
    """, unsafe_allow_html=True)
    th_col1, th_col2 = st.columns([3, 1])
    with th_col1:
        new_th = st.slider(
            "PM₂.₅ Safety Trigger Threshold (µg/m³)",
            min_value=10.0,
            max_value=250.0,
            value=float(user_threshold),
            step=5.0,
            help="WHO standard is 15 µg/m³ 24h mean. Typical sensitive threshold: 35–55 µg/m³."
        )
    with th_col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("💾 Save Threshold", use_container_width=True):
            profile["aqi_alert_threshold"] = new_th
            save_user_profile(profile)
            save_alert(target_city, "pm2_5", new_th, condition="greater_than")
            st.success(f"Threshold updated to {new_th:.0f} µg/m³.")
            st.rerun()

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ----------------- SECTION 2: LIVE AQI HERO & METEOROLOGY -----------------
col_hero, col_met = st.columns([1.8, 1.2])

with col_hero:
    render_aqi_hero_card(
        aqi=curr_aqi,
        category=category,
        color=color,
        city=format_location_label(loc_meta),
        timestamp=timestamp_str,
        pm25_val=curr_pm
    )

with col_met:
    with st.container(border=True):
        safe_markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2);">
            <span style="font-family: var(--font-dot); font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #FFFFFF;">
                METEOROLOGICAL TELEMETRY
            </span>
            <span class="ag-badge ag-badge-nothing" style="font-size: 0.65rem; padding: 2px 8px;">ATMOSPHERE</span>
        </div>
        """)

        temp = curr_data.get("temperature")
        hum = curr_data.get("humidity")
        ws = curr_data.get("wind_speed")
        wd = curr_data.get("wind_direction")
        press = curr_data.get("pressure")

        m_col1, m_col2 = st.columns(2)
        with m_col1:
            render_metric_tile(
                label="Temperature",
                value=f"{temp:.1f}" if temp is not None else "--",
                unit="°C",
                subtext="Dry-bulb ambient",
                icon="sun"
            )
            render_metric_tile(
                label="Wind Speed",
                value=f"{ws:.1f}" if ws is not None else "--",
                unit="km/h",
                subtext=f"Direction: {wd:.0f}°" if wd is not None else "Unknown",
                icon="wind"
            )
        with m_col2:
            render_metric_tile(
                label="Relative Humidity",
                value=f"{hum:.0f}" if hum is not None else "--",
                unit="%",
                subtext="Moisture saturation",
                icon="cloud"
            )
            render_metric_tile(
                label="Atmospheric Pressure",
                value=f"{press:.0f}" if press is not None else "--",
                unit="hPa",
                subtext="Mean sea level",
                icon="gauge"
            )

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ----------------- SECTION 3: MULTI-POLLUTANT TELEMETRY -----------------
render_section_header(
    title="Multi-Pollutant Spectrum & WHO Safety Benchmarks",
    subtitle=f"Mass concentrations observed in {target_city} benchmarked against World Health Organization 24-hour guidelines.",
    badge="POLLUTANT CONCENTRATIONS"
)

p_col1, p_col2, p_col3, p_col4, p_col5, p_col6 = st.columns(6)

def fmt_val(val: Any) -> str:
    return f"{float(val):.1f}" if val is not None else "--"

with p_col1:
    render_metric_tile(label="PM₂.₅", value=fmt_val(curr_data.get("pm2_5")), unit="µg/m³", subtext="WHO: 15 µg/m³", icon="pulse")
with p_col2:
    render_metric_tile(label="PM₁₀", value=fmt_val(curr_data.get("pm10")), unit="µg/m³", subtext="WHO: 45 µg/m³", icon="gauge")
with p_col3:
    render_metric_tile(label="Nitrogen Dioxide (NO₂)", value=fmt_val(curr_data.get("no2")), unit="µg/m³", subtext="WHO: 25 µg/m³", icon="alert")
with p_col4:
    render_metric_tile(label="Ozone (O₃)", value=fmt_val(curr_data.get("o3")), unit="µg/m³", subtext="WHO: 100 µg/m³", icon="sun")
with p_col5:
    render_metric_tile(label="Carbon Monoxide (CO)", value=fmt_val(curr_data.get("co")), unit="µg/m³", subtext="WHO: 4 mg/m³", icon="pulse")
with p_col6:
    render_metric_tile(label="Sulfur Dioxide (SO₂)", value=fmt_val(curr_data.get("so2")), unit="µg/m³", subtext="WHO: 40 µg/m³", icon="cloud")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ----------------- SECTION 4: ACTIVE THREAT MONITOR & AUDIT LOG -----------------
render_section_header(
    title="Threshold Breach Audit & Early Warnings",
    subtitle="Automated evaluation of live ground readings and +24h forecasted horizons against your safety criteria.",
    badge="BREACH LOGS"
)

triggered_alerts = evaluate_alerts_for_city(
    city=target_city,
    current_pm25=curr_pm,
    current_aqi=curr_aqi,
    forecast_df=forecast_df
)

if triggered_alerts:
    for t in triggered_alerts:
        is_severe = t.get("severity") == "High"
        b_color = "#D71921" if is_severe else "#EAB308"
        bg_col = "rgba(215, 25, 33, 0.08)" if is_severe else "rgba(234, 179, 8, 0.08)"
        action_tag = "🔴 IMMEDIATE ACTION REQUIRED" if t["type"] == "current" else "🟠 ADVANCE PEAK WARNING (+24H)"

        safe_markdown(f"""
        <div style="border: 1px solid #242424; border-left: 4px solid {b_color}; background: {bg_col}; padding: var(--space-4); margin-bottom: var(--space-3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-family: var(--font-dot); font-size: 0.74rem; font-weight: 700; color: {b_color};">{action_tag}</span>
                <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #888888;">Severity: {t.get('severity', 'Moderate').upper()}</span>
            </div>
            <div style="font-family: var(--font-sans); color: #FFFFFF; font-size: 0.88rem; line-height: 1.5;">
                {t['message']}
            </div>
        </div>
        """)
else:
    render_callout(
        title="Atmospheric Safety Verified — All Thresholds Clear",
        message=f"No threshold breaches detected for {target_city}. Current PM₂.₅ ({curr_pm:.1f} µg/m³) and 24-hour forecast trajectory both comply with configured alert thresholds.",
        variant="success",
        icon="check"
    )

# Historical incident audit log
recent_logs = fetch_alert_logs(limit=10)
if recent_logs:
    with st.expander("📜 Recent Triggered Alert History (Audit Log)", expanded=False):
        log_records = []
        for r in recent_logs:
            log_records.append({
                "Timestamp": r.get("triggered_at", "").replace("T", " "),
                "City": r.get("city"),
                "Metric": str(r.get("metric")).upper(),
                "Observed Value": f"{float(r.get('value', 0)):.1f}",
                "Threshold": f"{float(r.get('threshold_value', 0)):.1f}",
                "Message": r.get("message")
            })
        st.dataframe(pd.DataFrame(log_records), use_container_width=True, hide_index=True)
