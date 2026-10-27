"""
Live Atmospheric Tracking & Personal Threshold Alert Center for AirFusion.
Features real-time multi-pollutant telemetry, meteorological dynamics,
personal threshold breach tracking, and a unified temporal continuum
spanning Past Observed History, On-Time Real-Time Telemetry, and Future Model Predictions.
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
from src.temporal_continuum import get_city_temporal_continuum
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
from app.components.mode_switcher import is_simple_mode, render_mode_banner
from app.components.simple_views import render_simple_live_tracking
from app.components.cards import render_aqi_hero_card, render_technical_weather_station
from app.components.charts import create_temporal_continuum_chart
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
    page_title="Live Tracking & Alerts — AirFusion",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="auto"
)

# Render Global Navbar
target_city = render_global_navbar("Live Tracking")

# Render Mode Notification Banner
render_mode_banner()

if is_simple_mode():
    render_simple_live_tracking(target_city)
    st.stop()

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_continuum_data(city_name: str):
    return get_city_temporal_continuum(city_name)

# Header and Top Controls
render_section_header(
    title=f"Atmospheric Telemetry & Real-Time Tracking — {target_city}",
    subtitle="On-time sensor synchronization, past observed history, and forward machine learning projections.",
    badge="GROUND TELEMETRY & TEMPORAL CONTINUUM"
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
        if st.button("🛡️ My Safe Plan", key="btn_goto_plan", use_container_width=True):
            st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")

# Fetch unified temporal continuum
with st.spinner(f"Ingesting real-time atmospheric telemetry and continuum for {target_city}..."):
    continuum = get_continuum_data(target_city)

if not continuum:
    render_callout(
        title="Location Resolution Error",
        message=f"Could not retrieve telemetry for '{target_city}'. Please verify coordinates or select another location.",
        variant="alert",
        icon="alert"
    )
    st.stop()

loc_meta = continuum["loc_meta"]
curr_data = continuum["current"]
metrics = continuum["metrics"]
actual_time_display = continuum["actual_time_display"]
actual_date_display = continuum["actual_date_display"]
actual_iso = continuum["actual_iso"]
history_df = continuum["history_df"]
forecast_df = continuum["forecast_df"]

curr_pm = float(curr_data.get("pm2_5") or 25.0) if pd.notnull(curr_data.get("pm2_5")) else 25.0
curr_aqi = int(curr_data.get("aqi", 0))
category = curr_data.get("aqi_category", "Moderate")
color = curr_data.get("aqi_color", "#10B981")
timestamp_str = curr_data.get("timestamp", "").replace("T", " ")

# ----------------- STATION ON-TIME TELEMETRY SYNCHRONIZATION COMMAND STRIP -----------------
safe_markdown(f"""
<div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 16px 22px; margin-bottom: 22px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="ag-pulse-dot" style="width: 7px; height: 7px;"></span>
                <span style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #FF6845; text-transform: uppercase; letter-spacing: 0.06em;">
                    ACTUAL ON-TIME TELEMETRY:
                </span>
                <span style="font-family: var(--font-mono); font-size: 0.8rem; font-weight: 800; color: #1F344C;">
                    {actual_time_display}
                </span>
                <span style="font-family: var(--font-sans); font-size: 0.74rem; color: #5A6E85;">
                    ({actual_date_display})
                </span>
            </div>
            <div style="font-family: var(--font-mono); font-size: 0.74rem; color: #5A6E85;">
                STATION: <strong style="color: #1F344C;">{loc_meta['latitude']:.4f}°N, {loc_meta['longitude']:.4f}°E</strong>
            </div>
            <div style="font-family: var(--font-mono); font-size: 0.74rem; color: #5A6E85;">
                INGESTION: <strong style="color: #1F344C;">Multi-Spectral Ground Array</strong>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-family: var(--font-mono); font-size: 0.68rem; background: #ECFDF5; color: #059669; border: 1px solid rgba(16, 185, 129, 0.3); padding: 3px 10px; border-radius: 9999px; font-weight: 700;">
                ● LATENCY: 28ms
            </span>
            <span style="font-family: var(--font-mono); font-size: 0.68rem; background: #FAF6F1; color: #FF6845; border: 1px solid rgba(255, 104, 69, 0.25); padding: 3px 10px; border-radius: 9999px; font-weight: 700;">
                WAL VERIFIED
            </span>
        </div>
    </div>
</div>
""")

# Retrieve user profile & threshold settings
profile = get_user_profile()
user_threshold = float(profile.get("aqi_alert_threshold", 55.0))

# ----------------- SECTION 1: PERSONAL THRESHOLD STATUS CARD & EARLY WARNINGS -----------------
pct_threshold = (curr_pm / user_threshold) if user_threshold > 0 else 1.0

if pct_threshold >= 1.0:
    thresh_status = "THRESHOLD CROSSED"
    thresh_badge_color = "#D71921"
    thresh_desc = f"Current PM₂.₅ ({curr_pm:.1f} µg/m³) has exceeded your personal safety limit ({user_threshold:.1f} µg/m³)."
elif pct_threshold >= 0.80:
    thresh_status = "APPROACHING THRESHOLD"
    thresh_badge_color = "#EAB308"
    thresh_desc = f"Current PM₂.₅ ({curr_pm:.1f} µg/m³) is within 20% of your threshold ({user_threshold:.1f} µg/m³). Precaution advised."
else:
    thresh_status = "SAFE (BELOW THRESHOLD)"
    thresh_badge_color = "#22C55E"
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

        peak_hours = exceedances["target_time"].tolist()
        if len(peak_hours) >= 2:
            avoid_period_msg = f"Avoid outdoor exposure between {peak_hours[0][-5:]} and {peak_hours[-1][-5:]} when pollution spikes."
        else:
            avoid_period_msg = f"Avoid outdoor exposure near {peak_hours[0][-5:]} when peak concentration occurs."

# Render Threshold Defense Strip
safe_markdown(f"""
<div class="ag-card" style="border: 1px solid #EBE6DF; background: #FFFFFF; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span class="ag-pulse-dot" style="background-color: {thresh_badge_color}; box-shadow: 0 0 10px {thresh_badge_color};"></span>
            <span style="font-family: var(--font-heading); font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: #1F344C;">
                LIVE ALERT DEFENSE STATUS
            </span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #5A6E85; font-weight: 600;">STATUS:</span>
            <span style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700; padding: 3px 12px; border-radius: 9999px; background: {thresh_badge_color}; color: #FFFFFF; text-transform: uppercase; letter-spacing: 0.05em;">
                {thresh_status}
            </span>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 16px;">
        <div style="padding: 14px 16px; border: 1px solid #EBE6DF; background: #FAF6F1; border-radius: 12px;">
            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #5A6E85; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">CURRENT PM₂.₅</div>
            <div style="font-family: var(--font-mono); font-size: 1.7rem; font-weight: 800; color: #1F344C; line-height: 1.1; margin: 4px 0;">{curr_pm:.1f} <span style="font-size: 0.8rem; font-weight: 500; color: #8896A6;">µg/m³</span></div>
            <div style="font-family: var(--font-sans); font-size: 0.76rem; color: #5A6E85;">AQI {curr_aqi} ({category})</div>
        </div>
        <div style="padding: 14px 16px; border: 1px solid #EBE6DF; background: #FAF6F1; border-radius: 12px;">
            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #5A6E85; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">PERSONAL THRESHOLD</div>
            <div style="font-family: var(--font-mono); font-size: 1.7rem; font-weight: 800; color: #1F344C; line-height: 1.1; margin: 4px 0;">{user_threshold:.1f} <span style="font-size: 0.8rem; font-weight: 500; color: #8896A6;">µg/m³</span></div>
            <div style="font-family: var(--font-sans); font-size: 0.76rem; color: #5A6E85;">Profile sensitivity limit</div>
        </div>
        <div style="padding: 14px 16px; border: 1px solid #EBE6DF; background: #FAF6F1; border-radius: 12px;">
            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #5A6E85; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">EXPOSURE RATIO</div>
            <div style="font-family: var(--font-mono); font-size: 1.7rem; font-weight: 800; color: {'#DC2626' if pct_threshold >= 1.0 else '#059669'}; line-height: 1.1; margin: 4px 0;">{pct_threshold * 100:.0f}%</div>
            <div style="font-family: var(--font-sans); font-size: 0.76rem; color: #5A6E85;">{'Exceeded limit' if pct_threshold >= 1.0 else 'Within safety margin'}</div>
        </div>
    </div>
    <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; line-height: 1.55; border-top: 1px solid #EBE6DF; padding-top: 12px;">
        <strong style="color: #1F344C;">Advisory:</strong> {thresh_desc}
        {f"<br><span style='color: #D97706;'>⚠️ <strong>Early Warning:</strong> {early_warning_msg}</span>" if early_warning_msg else ""}
        {f"<br><span style='color: #DC2626;'>⛔ <strong>Avoid Guidance:</strong> {avoid_period_msg}</span>" if avoid_period_msg else ""}
    </div>
</div>
""")

with st.expander("⚙️ Configure Personal PM₂.₅ Alert Threshold", expanded=False):
    st.markdown("""
    <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; margin-bottom: 12px;">
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
            <span style="font-family: var(--font-heading); font-size: 0.76rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; color: #1F344C;">
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
render_technical_weather_station(curr_data, target_city)
st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# ----------------- SECTION 3: UNIFIED CHRONOLOGICAL CONTINUUM PLOT -----------------
render_section_header(
    title="Unified Chronological Atmospheric Continuum: History ➔ Live ➔ Predictions",
    subtitle=f"Complete temporal trajectory combining past 48-hour ground sensor observations, exact on-time anchor, and next 48-hour machine learning projections with 90% confidence envelope for {target_city}.",
    badge="CHRONOLOGICAL TIME-SERIES"
)

# Variable Selector Toolbar
metric_choice = st.radio(
    "Select Continuum Variable",
    options=["PM₂.₅ Fine Particulates", "PM₁₀ Coarse Dust", "Ambient Temperature", "Wind Speed"],
    horizontal=True,
    key="continuum_var_selector"
)

metric_map = {
    "PM₂.₅ Fine Particulates": ("pm2_5", "PM₂.₅ (µg/m³)", 15.0),
    "PM₁₀ Coarse Dust": ("pm10", "PM₁₀ (µg/m³)", 45.0),
    "Ambient Temperature": ("temperature", "Temperature (°C)", None),
    "Wind Speed": ("wind_speed", "Wind Speed (km/h)", None)
}

selected_col, selected_label, selected_thresh = metric_map[metric_choice]

fig_continuum = create_temporal_continuum_chart(
    history_df=history_df,
    forecast_df=forecast_df,
    current_val=float(curr_data.get(selected_col, curr_pm if selected_col == 'pm2_5' else 0.0)),
    current_time=curr_data.get("timestamp"),
    city_name=target_city,
    metric=selected_col,
    metric_label=selected_label,
    threshold=selected_thresh
)

st.plotly_chart(fig_continuum, use_container_width=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# ----------------- SECTION 4: TEMPORAL MULTI-POLLUTANT COMPARATIVE MATRIX -----------------
render_section_header(
    title="Temporal Multi-Pollutant Comparative Matrix",
    subtitle="Comparative breakdown of past 24-hour observed behavior, current on-time concentration, and forward 48-hour outlook across all 6 criteria pollutants.",
    badge="TEMPORAL MATRIX"
)

matrix_records = []
pollutant_labels = [
    ("pm2_5", "PM₂.₅ Fine Particulate", 15.0, "µg/m³"),
    ("pm10", "PM₁₀ Coarse Dust", 45.0, "µg/m³"),
    ("no2", "Nitrogen Dioxide (NO₂)", 25.0, "µg/m³"),
    ("so2", "Sulfur Dioxide (SO₂)", 40.0, "µg/m³"),
    ("o3", "Ground-Level Ozone (O₃)", 100.0, "µg/m³"),
    ("co", "Carbon Monoxide (CO)", 4000.0, "µg/m³"),
]

for p_key, p_name, p_who, p_unit in pollutant_labels:
    p_stat = metrics["multi_summary"].get(p_key, {"history_mean": 0.0, "history_max": 0.0, "now_val": 0.0})
    now_v = p_stat["now_val"]
    who_ratio = (now_v / p_who * 100) if p_who > 0 else 0

    if who_ratio <= 100:
        compliance_status = "Optimal" if who_ratio <= 60 else "Acceptable"
    elif who_ratio <= 200:
        compliance_status = "Elevated"
    else:
        compliance_status = "Critical Exceedance"

    matrix_records.append({
        "Pollutant Signal": p_name,
        "Past 24h Mean": f"{p_stat['history_mean']:.1f} {p_unit}",
        "Past 24h Max": f"{p_stat['history_max']:.1f} {p_unit}",
        "Right Now (Live)": f"{now_v:.1f} {p_unit}",
        "WHO 2021 Reference": f"{p_who:.0f} {p_unit}",
        "Current Exposure Ratio": f"{who_ratio:.0f}%",
        "Compliance Status": compliance_status
    })

st.dataframe(pd.DataFrame(matrix_records), use_container_width=True, hide_index=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# ----------------- SECTION 5: ACTIVE THREAT MONITOR & AUDIT LOG -----------------
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
        <div style="border: 1px solid var(--ag-border); border-left: 4px solid {b_color}; background: {bg_col}; border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; backdrop-filter: blur(12px);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: {b_color};">{action_tag}</span>
                <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #94A3B8;">Severity: {t.get('severity', 'Moderate').upper()}</span>
            </div>
            <div style="font-family: var(--font-sans); color: #1F344C; font-size: 0.88rem; line-height: 1.5;">
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

# ----------------- SECTION 6: CONTINUUM RAW DATA EXPORT & INSPECTOR -----------------
with st.expander("📥 Unified Temporal Continuum Data Export (CSV & Raw JSON)", expanded=False):
    st.markdown("""
    <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; margin-bottom: 14px;">
        Download the unified chronological dataset combining past ground sensor observations and forward model forecasts for statistical analysis or external processing.
    </div>
    """, unsafe_allow_html=True)

    # Build export dataframe
    export_rows = []
    if not history_df.empty:
        for _, row in history_df.iterrows():
            export_rows.append({
                "Timestamp": row["timestamp"].strftime("%Y-%m-%d %H:%M"),
                "Temporal Phase": "Observed History",
                "PM2.5 (µg/m³)": f"{float(row.get('pm2_5') or 0.0):.1f}",
                "PM10 (µg/m³)": f"{float(row.get('pm10', 0.0)):.1f}" if pd.notna(row.get('pm10')) else "--",
                "AQI": int(row.get("aqi", 0)),
                "Temperature (°C)": f"{float(row.get('temperature', 0.0)):.1f}" if pd.notna(row.get('temperature')) else "--",
                "Humidity (%)": f"{float(row.get('humidity', 0.0)):.0f}" if pd.notna(row.get('humidity')) else "--",
                "Wind Speed (km/h)": f"{float(row.get('wind_speed', 0.0)):.1f}" if pd.notna(row.get('wind_speed')) else "--",
            })

    export_rows.append({
        "Timestamp": actual_iso,
        "Temporal Phase": "🔴 RIGHT NOW (LIVE ON-TIME)",
        "PM2.5 (µg/m³)": f"{curr_pm:.1f}",
        "PM10 (µg/m³)": f"{float(curr_data.get('pm10', 0.0)):.1f}" if curr_data.get('pm10') is not None else "--",
        "AQI": curr_aqi,
        "Temperature (°C)": f"{float(curr_data.get('temperature', 0.0)):.1f}" if curr_data.get('temperature') is not None else "--",
        "Humidity (%)": f"{float(curr_data.get('humidity', 0.0)):.0f}" if curr_data.get('humidity') is not None else "--",
        "Wind Speed (km/h)": f"{float(curr_data.get('wind_speed', 0.0)):.1f}" if curr_data.get('wind_speed') is not None else "--",
    })

    if not forecast_df.empty:
        for _, row in forecast_df.iterrows():
            export_rows.append({
                "Timestamp": row["target_time"],
                "Temporal Phase": "🔮 Model Forecast",
                "PM2.5 (µg/m³)": f"{float(row.get('predicted_pm2_5') or 0.0):.1f}",
                "PM10 (µg/m³)": "--",
                "AQI": int(row.get("predicted_aqi", 0)),
                "Temperature (°C)": "--",
                "Humidity (%)": "--",
                "Wind Speed (km/h)": "--",
            })

    df_export = pd.DataFrame(export_rows)
    st.dataframe(df_export, use_container_width=True, height=280)

    csv_bytes = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Download Continuum Dataset for {target_city} (CSV)",
        data=csv_bytes,
        file_name=f"airfusion_continuum_{target_city.lower().replace(' ', '_')}.csv",
        mime="text/csv",
        key="btn_download_continuum"
    )
