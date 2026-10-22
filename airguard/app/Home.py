"""
AirGuard — Real-Time Air Quality Intelligence & Forecasting Platform.
Executive Command Center & High-Level Overview.
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import init_db, fetch_historical_records
from src.predict import is_model_trained
from src.data_collection import geocode_city, fetch_current_air_quality
from app.components.navbar import render_global_navbar
from app.components.cards import render_aqi_hero_card
from app.components.design_system import (
    render_section_header,
    render_metric_tile,
    render_callout,
    render_badge,
    safe_markdown,
    format_location_label,
    ICONS
)

st.set_page_config(
    page_title="AirGuard — Environmental Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Initialize database
init_db()

# Render Global Nav & get active synchronized city
active_city = render_global_navbar("Home")

# Top Layout: Active Location Hero Card + Primary Action Center
loc = geocode_city(active_city)
if loc:
    curr = fetch_current_air_quality(loc["latitude"], loc["longitude"])
    pm25_val = float(curr.get("pm2_5", 0.0))
    aqi_val = int(curr.get("aqi", 0))
    category = curr.get("aqi_category", "Unknown")
    color = curr.get("aqi_color", "#10B981")
    timestamp_str = curr.get("timestamp", "").replace("T", " ")

    col_hero, col_cta = st.columns([1.8, 1.2])

    with col_hero:
        render_aqi_hero_card(
            aqi=aqi_val,
            category=category,
            color=color,
            city=format_location_label(loc),
            timestamp=timestamp_str,
            pm25_val=pm25_val
        )

    with col_cta:
        with st.container(border=True):
            safe_markdown("""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2);">
                <span style="font-size: var(--text-xs); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--color-sky-400);">
                    ⚡ Command Shortcuts
                </span>
                <span class="badge badge-info">ACTIONS</span>
            </div>
            <div style="font-size: var(--text-lg); font-weight: 800; color: var(--color-slate-100); line-height: 1.3; margin-bottom: var(--space-1);">
                Immediate Safety & Forecasting
            </div>
            <p style="font-size: var(--text-xs); color: var(--color-slate-400); margin: 0 0 var(--space-3) 0; line-height: 1.5;">
                Explore real-time multi-pollutant telemetry, run 72-hour machine learning projections, or configure threshold alerts.
            </p>
            """)

            btn_live = st.button("📡 Open Live Telemetry Dashboard", key="cta_live", use_container_width=True)
            btn_fc = st.button("📈 View 72h Predictive Trajectory", key="cta_fc", use_container_width=True)
            btn_alert = st.button("🚨 Safety Alerts & Health Protocol", key="cta_alert", use_container_width=True)

            if btn_live:
                st.switch_page("pages/1_Live_Air_Quality.py")
            elif btn_fc:
                st.switch_page("pages/2_Forecast.py")
            elif btn_alert:
                st.switch_page("pages/5_Alerts.py")
else:
    render_callout(
        title="Location Unresolved",
        message=f"Could not resolve geographical coordinates for '{active_city}'. Please select a supported location from the navigation switcher.",
        variant="alert",
        icon="alert"
    )

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# Regional Focal Centers Snapshot (Chandigarh, Mohali, Kharar, Delhi)
render_section_header(
    title="Regional Focal Centers (At a Glance)",
    subtitle="Live cross-city monitoring across the Tri-City and National Capital Region.",
    badge="REGIONAL MONITOR"
)

regional_cities = ["Chandigarh", "Mohali", "Kharar", "Delhi"]
rcols = st.columns(4)

@st.cache_data(ttl=600)
def get_city_snapshot(city_name: str):
    # Check local SQLite archive first for instant render
    df = fetch_historical_records(city=city_name)
    if not df.empty:
        latest = df.iloc[-1]
        return {
            "city": city_name,
            "aqi": int(latest.get("aqi", 0)),
            "category": str(latest.get("aqi_category", "Unknown")),
            "pm2_5": float(latest.get("pm2_5", 0.0)),
            "temp": latest.get("temperature", "--"),
            "humidity": latest.get("humidity", "--")
        }
    # Fallback to live API if not yet archived
    l = geocode_city(city_name)
    if l:
        c = fetch_current_air_quality(l["latitude"], l["longitude"])
        return {
            "city": city_name,
            "aqi": c.get("aqi", 0),
            "category": c.get("aqi_category", "Unknown"),
            "pm2_5": c.get("pm2_5", 0.0),
            "temp": c.get("temperature", "--"),
            "humidity": c.get("humidity", "--")
        }
    return None

for idx, city in enumerate(regional_cities):
    with rcols[idx]:
        snap = get_city_snapshot(city)
        if snap:
            is_active = (city.lower() == active_city.lower())
            active_badge = "<span class='badge badge-good' style='font-size: 0.65rem; padding: 2px 6px;'>ACTIVE</span>" if is_active else ""
            
            with st.container(border=True):
                safe_markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 1.05rem; color: #FFFFFF;">{snap['city']}</span>
                    {active_badge}
                </div>
                <div style="display: flex; align-items: baseline; justify-content: space-between;">
                    <div>
                        <div style="font-family: var(--font-mono); font-size: 1.8rem; font-weight: 800; color: #F8FAFC;">
                            {snap['aqi']}
                        </div>
                        <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">US AQI</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-family: var(--font-mono); font-size: 1.05rem; font-weight: 600; color: var(--color-brand-cyan);">
                            {snap['pm2_5']:.1f}
                        </div>
                        <div style="font-size: 0.7rem; color: #64748B;">PM₂.₅ µg/m³</div>
                    </div>
                </div>
                <div style="margin-top: 10px; font-size: 0.75rem; color: #CBD5E1; border-top: 1px solid var(--color-border-subtle); padding-top: 8px;">
                    ● {snap['category']} ({snap['temp']}°C, {snap['humidity']}%)
                </div>
                """)
                
                if not is_active:
                    if st.button(f"Inspect {city}", key=f"btn_switch_{city}", use_container_width=True):
                        st.session_state["selected_city"] = city
                        st.rerun()
                else:
                    st.button("● Currently Active", key=f"btn_switch_{city}", disabled=True, use_container_width=True)

st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

# System Foundation Status Indicators
render_section_header(
    title="Platform Infrastructure & Model Status",
    subtitle="Continuous health checks across data streams, inference engines, and storage.",
    badge="SYSTEM STATUS"
)

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
model_ready = is_model_trained()

with col_s1:
    status_label = "Active (XGBoost)" if model_ready else "Needs Training"
    render_metric_tile(
        label="Predictive Engine",
        value=status_label,
        unit="",
        subtext="Champion multi-step regressor",
        icon="shield"
    )

with col_s2:
    render_metric_tile(
        label="Data Telemetry",
        value="Open-Meteo",
        unit="API",
        subtext="Zero-key open atmospheric stream",
        icon="pulse"
    )

with col_s3:
    render_metric_tile(
        label="Forecasting Scope",
        value="24h / 72h",
        unit="horizons",
        subtext="90% confidence uncertainty ribbon",
        icon="chart"
    )

with col_s4:
    render_metric_tile(
        label="Local Storage",
        value="SQLite WAL",
        unit="db",
        subtext="Thread-safe time-series records",
        icon="gauge"
    )

st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

# Platform Intelligence Modules Grid with Interactive Routing
render_section_header(
    title="Environmental Intelligence Modules",
    subtitle="Directly jump into specialized workflows for live telemetry, predictions, historical trends, and governance.",
    badge="CAPABILITIES"
)

mcol1, mcol2, mcol3 = st.columns(3)

with mcol1:
    with st.container(border=True):
        safe_markdown("""
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--color-slate-100); margin-bottom: 6px;">
            📡 Live Telemetry
        </div>
        <p style="color: var(--color-slate-400); font-size: 0.85rem; line-height: 1.5; margin: 0 0 12px 0;">
            Continuous multi-pollutant telemetry (PM2.5, PM10, NO2, O3, CO, SO2) alongside
            ambient meteorology with US EPA standardized classifications.
        </p>
        """)
        if st.button("Explore Live Telemetry →", key="mod_live", use_container_width=True):
            st.switch_page("pages/1_Live_Air_Quality.py")

with mcol2:
    with st.container(border=True):
        safe_markdown("""
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--color-slate-100); margin-bottom: 6px;">
            📈 Predictive Forecasting
        </div>
        <p style="color: var(--color-slate-400); font-size: 0.85rem; line-height: 1.5; margin: 0 0 12px 0;">
            Multi-step time-series regression with dynamic 90% confidence bands,
            stagnation dispersion indices, and natural-language AI insights.
        </p>
        """)
        if st.button("View Predictive Horizons →", key="mod_fc", use_container_width=True):
            st.switch_page("pages/2_Forecast.py")

with mcol3:
    with st.container(border=True):
        safe_markdown("""
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--color-slate-100); margin-bottom: 6px;">
            📊 Historical Trends
        </div>
        <p style="color: var(--color-slate-400); font-size: 0.85rem; line-height: 1.5; margin: 0 0 12px 0;">
            Diurnal rush-hour curves, weekday/weekend traffic deviations,
            seasonal variations, and atmospheric cross-correlation heatmaps.
        </p>
        """)
        if st.button("Analyze Historical Trends →", key="mod_trends", use_container_width=True):
            st.switch_page("pages/3_Trends_Analytics.py")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
mcol4, mcol5, mcol6 = st.columns(3)

with mcol4:
    with st.container(border=True):
        safe_markdown("""
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--color-slate-100); margin-bottom: 6px;">
            🏙️ City Comparison
        </div>
        <p style="color: var(--color-slate-400); font-size: 0.85rem; line-height: 1.5; margin: 0 0 12px 0;">
            Benchmark air quality across 2 to 5 target locations simultaneously (e.g. Kharar,
            Mohali, Chandigarh, Delhi) with cleanest vs most polluted rankings.
        </p>
        """)
        if st.button("Compare Regional Cities →", key="mod_compare", use_container_width=True):
            st.switch_page("pages/4_City_Comparison.py")

with mcol5:
    with st.container(border=True):
        safe_markdown("""
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--color-slate-100); margin-bottom: 6px;">
            🚨 Alerts & Safety Protocol
        </div>
        <p style="color: var(--color-slate-400); font-size: 0.85rem; line-height: 1.5; margin: 0 0 12px 0;">
            Customizable particulate thresholds with proactive advance warnings before
            forecast peaks, plus clinical mask and ventilation advisories.
        </p>
        """)
        if st.button("Configure Safety Alerts →", key="mod_alerts", use_container_width=True):
            st.switch_page("pages/5_Alerts.py")

with mcol6:
    with st.container(border=True):
        safe_markdown("""
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--color-slate-100); margin-bottom: 6px;">
            🔍 Model Insights (XAI)
        </div>
        <p style="color: var(--color-slate-400); font-size: 0.85rem; line-height: 1.5; margin: 0 0 12px 0;">
            Global feature importances, TreeSHAP attributions, chronological test benchmarking
            (MAE, RMSE, R², F1), and one-click model retraining.
        </p>
        """)
        if st.button("Inspect Model Diagnostics →", key="mod_xai", use_container_width=True):
            st.switch_page("pages/6_Model_Insights.py")
