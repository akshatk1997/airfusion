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
from app.components.mode_switcher import (
    get_view_mode,
    is_simple_mode,
    is_technical_mode,
    render_mode_banner,
    SIMPLE_MODE,
    TECHNICAL_MODE
)
from app.components.simple_views import render_simple_home
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

# Render Mode Notification Banner
render_mode_banner()

mode = get_view_mode()

def render_technical_home(active_city: str) -> None:
    """
    Renders Technical Mode executive command center: full pollutant cards,
    real-time weather parameters, regional focal centers, infrastructure telemetry,
    and platform capability modules.
    """
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
                    <span style="font-family: var(--font-heading); font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #FFFFFF;">
                        ⚡ COMMAND SHORTCUTS
                    </span>
                    <span class="ag-badge ag-badge-nothing" style="font-size: 0.65rem; padding: 2px 8px;">ACTIONS</span>
                </div>
                <div style="font-family: var(--font-heading); font-size: 1.25rem; font-weight: 700; color: #FFFFFF; line-height: 1.3; margin-bottom: var(--space-1);">
                    Immediate Safety & Forecasting
                </div>
                <p style="font-family: var(--font-sans); font-size: 0.8rem; color: #888888; margin: 0 0 var(--space-3) 0; line-height: 1.5;">
                    Explore real-time multi-pollutant telemetry, run 72-hour machine learning projections, or configure threshold alerts.
                </p>
                """)

                btn_plan = st.button("🛡️ Open My Safe Outdoor Plan", key="cta_plan", use_container_width=True)
                btn_live = st.button("📡 Live Tracking & Alert Defense", key="cta_live", use_container_width=True)
                btn_fc = st.button("📈 Trends & Timeline Analysis", key="cta_fc", use_container_width=True)

                if btn_plan:
                    st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")
                elif btn_live:
                    st.switch_page("pages/2_Live_Tracking.py")
                elif btn_fc:
                    st.switch_page("pages/3_Trends.py")
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

    regional_base = ["Chandigarh", "Mohali", "Panchkula", "Delhi"]
    if active_city in regional_base:
        regional_cities = regional_base[:4]
    else:
        regional_cities = [active_city] + [c for c in regional_base if c.lower() != active_city.lower()][:3]

    rcols = st.columns(4)

    @st.cache_data(ttl=180)
    def get_city_snapshot(city_name: str):
        loc_meta = geocode_city(city_name)
        label = format_location_label(loc_meta) if loc_meta else city_name
        if loc_meta:
            try:
                c = fetch_current_air_quality(loc_meta["latitude"], loc_meta["longitude"])
                if c and c.get("aqi") is not None:
                    return {
                        "city": city_name,
                        "label": label,
                        "aqi": int(c.get("aqi", 0)),
                        "category": str(c.get("aqi_category", "Unknown")),
                        "pm2_5": float(c.get("pm2_5", 0.0)),
                        "temp": c.get("temperature", "--"),
                        "humidity": c.get("humidity", "--")
                    }
            except Exception:
                pass
        # Fallback to local archive
        df = fetch_historical_records(city=city_name)
        if not df.empty:
            latest = df.iloc[-1]
            return {
                "city": city_name,
                "label": label,
                "aqi": int(latest.get("aqi", 0)),
                "category": str(latest.get("aqi_category", "Unknown")),
                "pm2_5": float(latest.get("pm2_5", 0.0)),
                "temp": latest.get("temperature", "--"),
                "humidity": latest.get("humidity", "--")
            }
        return None

    for idx, city in enumerate(regional_cities):
        with rcols[idx]:
            snap = get_city_snapshot(city)
            if snap:
                is_active = (city.lower() == active_city.lower())
                active_badge = "<span class='ag-badge ag-badge-good' style='font-size: 0.62rem; padding: 2px 6px;'>ACTIVE</span>" if is_active else ""
                
                with st.container(border=True):
                    safe_markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-family: var(--font-sans); font-weight: 700; font-size: 0.95rem; color: #FFFFFF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{snap['label']}">{snap['label']}</span>
                        {active_badge}
                    </div>
                    <div style="display: flex; align-items: baseline; justify-content: space-between;">
                        <div>
                            <div style="font-family: var(--font-mono); font-size: 2.1rem; font-weight: 800; color: #FFFFFF; line-height: 1;">
                                {snap['aqi']}
                            </div>
                            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #777777; text-transform: uppercase; margin-top: 2px;">US AQI</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-family: var(--font-mono); font-size: 1.05rem; font-weight: 600; color: #CCCCCC;">
                                {snap['pm2_5']:.1f}
                            </div>
                            <div style="font-family: var(--font-sans); font-size: 0.68rem; color: #666666;">PM₂.₅ µg/m³</div>
                        </div>
                    </div>
                    <div style="margin-top: 10px; font-family: var(--font-sans); font-size: 0.75rem; color: #888888; border-top: 1px solid var(--color-border-subtle); padding-top: 8px;">
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

    # System Foundation Status Indicators (Technical Mode Only)
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
            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                🛡️ Safe Outdoor Plan
            </div>
            <p style="color: #888888; font-size: 0.84rem; line-height: 1.5; margin: 0 0 16px 0; min-height: 52px;">
                Personalized environmental decision support: Safe outdoor window finder, risk engine scoring, and cohort guidance.
            </p>
            """)
            if st.button("Generate Outdoor Plan →", key="mod_plan", use_container_width=True):
                st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")

    with mcol2:
        with st.container(border=True):
            safe_markdown("""
            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                📡 Live Tracking & Alerts
            </div>
            <p style="color: #888888; font-size: 0.84rem; line-height: 1.5; margin: 0 0 16px 0; min-height: 52px;">
                Multi-pollutant ground telemetry, meteorology, personal threshold monitor, and advance peak warnings.
            </p>
            """)
            if st.button("Explore Live Tracking →", key="mod_live", use_container_width=True):
                st.switch_page("pages/2_Live_Tracking.py")

    with mcol3:
        with st.container(border=True):
            safe_markdown("""
            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                📊 Atmospheric Trends
            </div>
            <p style="color: #888888; font-size: 0.84rem; line-height: 1.5; margin: 0 0 16px 0; min-height: 52px;">
                24h timeline safety zones, diurnal curves, 7-day patterns, and cross-correlation heatmaps.
            </p>
            """)
            if st.button("Analyze Historical Trends →", key="mod_trends", use_container_width=True):
                st.switch_page("pages/3_Trends.py")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    mcol4, mcol5, mcol6 = st.columns(3)

    with mcol4:
        with st.container(border=True):
            safe_markdown("""
            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                🔍 Model Insights & Governance
            </div>
            <p style="color: #888888; font-size: 0.84rem; line-height: 1.5; margin: 0 0 16px 0; min-height: 52px;">
                Global feature importances (XAI), candidate tournament (Persistence, Ridge, RF, XGBoost), and holdout metrics.
            </p>
            """)
            if st.button("Inspect Model Diagnostics →", key="mod_xai", use_container_width=True):
                st.switch_page("pages/4_Model_Insights.py")

    with mcol5:
        with st.container(border=True):
            safe_markdown("""
            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                🛡️ About & Safety Protocols
            </div>
            <p style="color: #888888; font-size: 0.84rem; line-height: 1.5; margin: 0 0 16px 0; min-height: 52px;">
                N95 mask guidance, indoor air defense, health cohort recommendations, and system documentation.
            </p>
            """)
            if st.button("View Safety Protocols →", key="mod_safety", use_container_width=True):
                st.switch_page("pages/5_About_Safety.py")

    with mcol6:
        with st.container(border=True):
            safe_markdown("""
            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                🏙️ Multi-City Comparison
            </div>
            <p style="color: #888888; font-size: 0.84rem; line-height: 1.5; margin: 0 0 16px 0; min-height: 52px;">
                Simultaneous multi-city benchmarking across custom registered cities, states, and global locations.
            </p>
            """)
            if st.button("Compare Regional Cities →", key="mod_compare", use_container_width=True):
                st.switch_page("pages/6_City_Comparison.py")


# ==============================================================================
# MODE-BASED CONDITIONAL PRESENTATION DISPATCH
# ==============================================================================
if is_simple_mode():
    render_simple_home(active_city)
else:
    render_technical_home(active_city)

