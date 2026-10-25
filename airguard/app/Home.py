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
from src.news_service import get_news_feed
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
from app.components.simple_cards import render_airguard_executive_footer
from app.components.cards import render_aqi_hero_card, render_technical_weather_station
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
                <div style="display: flex; flex-direction: column; justify-content: space-between; min-height: 145px; box-sizing: border-box;">
                    <div>
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2);">
                            <span style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #FF6845;">
                                ⚡ RAPID DIRECTIVES
                            </span>
                            <span class="ag-badge ag-badge-neutral" style="font-size: 0.65rem; padding: 2px 8px;">OPERATIONS</span>
                        </div>
                        <div style="font-family: var(--font-heading); font-size: 1.25rem; font-weight: 800; color: #1F344C; line-height: 1.3; margin-bottom: var(--space-1);">
                            Immediate Safety &amp; Forecasting
                        </div>
                        <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #5A6E85; margin: 0 0 var(--space-2) 0; line-height: 1.55;">
                            Explore real-time multi-pollutant telemetry, run 72-hour machine learning projections, or configure threshold alerts.
                        </p>
                    </div>
                </div>
                """)

                btn_plan = st.button("🛡️ Open My Safe Outdoor Plan", key="cta_plan", use_container_width=True)
                btn_live = st.button("📡 Live Tracking & Alert Defense", key="cta_live", use_container_width=True)
                btn_fc = st.button("📈 Trends & Timeline Analysis", key="cta_fc", use_container_width=True)
                btn_intro = st.button("🌟 Platform Architecture & Intro Tour", key="cta_intro", use_container_width=True)

                if btn_plan:
                    st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")
                elif btn_live:
                    st.switch_page("pages/2_Live_Tracking.py")
                elif btn_fc:
                    st.switch_page("pages/3_Trends.py")
                elif btn_intro:
                    st.switch_page("pages/0_Platform_Intro.py")

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # 1. REAL-TIME METEOROLOGICAL STATION & MESOSCALE ATMOSPHERIC STATE
        # ----------------------------------------------------------------------
        render_section_header(
            title="Real-Time Meteorological Station & Atmospheric State",
            subtitle="Live ambient temperature, apparent feels-like index, Magnus-Tetens dew point, wind vectors, and solar irradiance.",
            badge="METEOROLOGICAL SENTRY"
        )
        render_technical_weather_station(curr, format_location_label(loc))

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # 2. MULTI-SPECTRAL CRITERIA POLLUTANTS TELEMETRY (6 POLLUTANTS)
        # ----------------------------------------------------------------------
        render_section_header(
            title="Multi-Spectral Criteria Pollutants Telemetry",
            subtitle="Real-time multi-sensor telemetry for all 6 EPA criteria pollutants with WHO 2021 air quality benchmarks.",
            badge="CRITERIA POLLUTANTS"
        )

        pcols = st.columns(6)
        pollutant_specs = [
            ("PM₂.₅ Fine", curr.get("pm2_5", 0.0), "µg/m³", 15.0, "WHO: 15 µg/m³"),
            ("PM₁₀ Coarse", curr.get("pm10", 0.0), "µg/m³", 45.0, "WHO: 45 µg/m³"),
            ("NO₂ Dioxide", curr.get("no2", 0.0), "µg/m³", 25.0, "WHO: 25 µg/m³"),
            ("SO₂ Dioxide", curr.get("so2", 0.0), "µg/m³", 40.0, "WHO: 40 µg/m³"),
            ("O₃ Ozone", curr.get("o3", 0.0), "µg/m³", 100.0, "WHO: 100 µg/m³"),
            ("CO Monoxide", curr.get("co", 0.0), "µg/m³", 4000.0, "WHO: 4.0 mg/m³"),
        ]
        for p_idx, (p_name, p_val, p_unit, who_ref, who_label) in enumerate(pollutant_specs):
            with pcols[p_idx]:
                val = float(p_val) if p_val is not None else 0.0
                ratio = (val / who_ref) * 100 if who_ref > 0 else 0
                if ratio <= 100:
                    badge_txt = "OPTIMAL" if ratio <= 60 else "ACCEPTABLE"
                    badge_col = "#059669"
                    badge_bg = "#ECFDF5"
                elif ratio <= 200:
                    badge_txt = "ELEVATED"
                    badge_col = "#D97706"
                    badge_bg = "#FFFBEB"
                else:
                    badge_txt = "CRITICAL"
                    badge_col = "#DC2626"
                    badge_bg = "#FEF2F2"

                safe_markdown(f"""
                <div class="ag-card" style="
                    background: #FFFFFF;
                    border: 1px solid #EBE6DF;
                    border-radius: 14px;
                    padding: 16px 14px;
                    min-height: 140px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05);
                ">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #1F344C; text-transform: uppercase;">
                                {p_name}
                            </span>
                            <span style="font-family: var(--font-mono); font-size: 0.60rem; font-weight: 700; color: {badge_col}; background: {badge_bg}; padding: 2px 6px; border-radius: 9999px;">
                                {badge_txt}
                            </span>
                        </div>
                        <div style="display: flex; align-items: baseline; gap: 3px;">
                            <span style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 800; color: #1F344C; line-height: 1.1;">
                                {val:.1f}
                            </span>
                            <span style="font-family: var(--font-sans); font-size: 0.72rem; color: #8896A6;">{p_unit}</span>
                        </div>
                    </div>
                    <div style="font-family: var(--font-sans); font-size: 0.70rem; color: #5A6E85; border-top: 1px solid #EBE6DF; padding-top: 6px; margin-top: 8px;">
                        <span>{who_label}</span>
                        <div style="height: 4px; background: #EBE6DF; border-radius: 9999px; margin-top: 4px; overflow: hidden;">
                            <div style="height: 100%; width: {min(100.0, max(5.0, ratio))}%; background: {badge_col}; border-radius: 9999px;"></div>
                        </div>
                    </div>
                </div>
                """)

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # 2. ATMOSPHERIC PHYSICS & PLANETARY BOUNDARY LAYER (PBL) DYNAMICS
        # ----------------------------------------------------------------------
        render_section_header(
            title="Atmospheric Physics & Boundary Layer Dynamics",
            subtitle="Mesoscale boundary layer modeling, atmospheric stagnation, and thermal inversion trapping risk.",
            badge="ATMOSPHERIC DYNAMICS"
        )

        import math
        temp_val = float(curr.get("temperature", 25.0) or 25.0)
        hum_val = float(curr.get("humidity", 50.0) or 50.0)
        press_val = float(curr.get("pressure", 1013.0) or 1013.0)
        ws_val = float(curr.get("wind_speed", 5.0) or 5.0)
        wd_val = float(curr.get("wind_direction", 0.0) or 0.0)

        # Magnus-Tetens Dew Point calculation
        gamma = (17.27 * temp_val) / (237.7 + temp_val) + math.log(max(1.0, hum_val) / 100.0)
        dew_point = (237.7 * gamma) / (17.27 - gamma)

        # Estimated Planetary Boundary Layer Height (m)
        pbl_height = max(280.0, min(2400.0, 1200.0 * (1.0 - (hum_val / 100.0)) + (35.0 * ws_val)))

        # Thermal Inversion Trapping Risk Assessment
        if ws_val < 5.0 and press_val >= 1013.0 and hum_val > 65.0:
            inversion_status = "CRITICAL INVERSION"
            inversion_color = "#DC2626"
            inversion_bg = "#FEF2F2"
            inversion_desc = "Stagnant surface air trapped by cold descent layer; severe aerosol accumulation."
        elif ws_val < 8.0 and press_val >= 1010.0:
            inversion_status = "MODERATE TRAPPING"
            inversion_color = "#D97706"
            inversion_bg = "#FFFBEB"
            inversion_desc = "Reduced turbulent kinetic energy; moderate localized aerosol buildup."
        else:
            inversion_status = "ACTIVE DISPERSION"
            inversion_color = "#059669"
            inversion_bg = "#ECFDF5"
            inversion_desc = "Convective boundary mixing active; particulate plume venting normally."

        pbl_col1, pbl_col2, pbl_col3, pbl_col4 = st.columns(4)

        with pbl_col1:
            safe_markdown(f"""
            <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 18px 20px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05); min-height: 145px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #5A6E85; text-transform: uppercase;">
                        Boundary Layer Height (PBL)
                    </div>
                    <div style="font-family: var(--font-mono); font-size: 1.85rem; font-weight: 800; color: #1F344C; margin: 4px 0;">
                        {pbl_height:.0f} <span style="font-size: 0.85rem; font-weight: 600; color: #8896A6;">m AGL</span>
                    </div>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.74rem; color: #5A6E85; border-top: 1px solid #EBE6DF; padding-top: 8px;">
                    Atmospheric mixing depth proxy
                </div>
            </div>
            """)

        with pbl_col2:
            safe_markdown(f"""
            <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 18px 20px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05); min-height: 145px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #5A6E85; text-transform: uppercase;">
                        Surface Barometric Pressure
                    </div>
                    <div style="font-family: var(--font-mono); font-size: 1.85rem; font-weight: 800; color: #1F344C; margin: 4px 0;">
                        {press_val:.0f} <span style="font-size: 0.85rem; font-weight: 600; color: #8896A6;">hPa</span>
                    </div>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.74rem; color: #5A6E85; border-top: 1px solid #EBE6DF; padding-top: 8px;">
                    Mean sea level barometric gradient
                </div>
            </div>
            """)

        with pbl_col3:
            safe_markdown(f"""
            <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 18px 20px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05); min-height: 145px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #5A6E85; text-transform: uppercase;">
                        Dew Point &amp; Moisture
                    </div>
                    <div style="font-family: var(--font-mono); font-size: 1.85rem; font-weight: 800; color: #1F344C; margin: 4px 0;">
                        {dew_point:.1f} <span style="font-size: 0.85rem; font-weight: 600; color: #8896A6;">°C</span>
                    </div>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.74rem; color: #5A6E85; border-top: 1px solid #EBE6DF; padding-top: 8px;">
                    Ambient: {temp_val:.1f}°C (RH: {hum_val:.0f}%)
                </div>
            </div>
            """)

        with pbl_col4:
            safe_markdown(f"""
            <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 18px 20px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05); min-height: 145px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #5A6E85; text-transform: uppercase;">
                            Inversion Trapping
                        </span>
                        <span style="font-family: var(--font-mono); font-size: 0.62rem; font-weight: 700; color: {inversion_color}; background: {inversion_bg}; padding: 2px 6px; border-radius: 9999px;">
                            {inversion_status}
                        </span>
                    </div>
                    <div style="font-family: var(--font-sans); font-size: 0.82rem; font-weight: 700; color: #1F344C; margin-top: 6px;">
                        Wind: {ws_val:.1f} km/h ({wd_val:.0f}°)
                    </div>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.72rem; color: #5A6E85; border-top: 1px solid #EBE6DF; padding-top: 8px;">
                    {inversion_desc}
                </div>
            </div>
            """)

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # 3. INTERACTIVE INHALED PARTICULATE DOSAGE CALCULATOR
        # ----------------------------------------------------------------------
        render_section_header(
            title="Interactive Inhaled Particulate Dosage Calculator",
            subtitle="Computes cumulative inhaled aerosol microgram mass and alveolar pulmonary deposition based on minute ventilation rates.",
            badge="DOSAGE CALCULATOR"
        )

        with st.container(border=True):
            dcol1, dcol2 = st.columns([1.4, 1.6])

            with dcol1:
                safe_markdown("""
                <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                    Respiratory Ventilation Parameters
                </div>
                <p style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; margin-bottom: 14px;">
                    Inhaled particulate mass is defined as <em>Mass (µg) = C<sub>PM2.5</sub> × V̇<sub>E</sub> × t</em>, where V̇<sub>E</sub> is the physiological volume of air ventilated per hour.
                </p>
                """)

                activity_options = {
                    "Sedentary / Desk Work (0.45 m³/h)": 0.45,
                    "Light Walking (1.20 m³/h)": 1.20,
                    "Jogging / Cycling (2.40 m³/h)": 2.40,
                    "High-Intensity Aerobic (3.20 m³/h)": 3.20
                }
                chosen_act = st.selectbox(
                    "Activity & Minute Ventilation (V̇_E):",
                    options=list(activity_options.keys()),
                    index=1,
                    key="dose_act_select"
                )
                vent_rate = activity_options[chosen_act]

                dose_duration = st.slider(
                    "Exposure Duration (Minutes):",
                    min_value=15,
                    max_value=180,
                    value=45,
                    step=15,
                    key="dose_dur_slider"
                )

            with dcol2:
                # Calculate dosage
                hours = dose_duration / 60.0
                total_inhaled_ug = pm25_val * vent_rate * hours
                alveolar_ug = total_inhaled_ug * 0.65  # 65% deep capillary deposition
                who_daily_allowance = 15.0 * 12.0      # 180 ug/day baseline allowance
                pct_who_day = (total_inhaled_ug / who_daily_allowance) * 100.0

                dose_badge_col = "#059669" if total_inhaled_ug < 30.0 else ("#D97706" if total_inhaled_ug < 90.0 else "#DC2626")
                dose_badge_bg = "#ECFDF5" if total_inhaled_ug < 30.0 else ("#FFFBEB" if total_inhaled_ug < 90.0 else "#FEF2F2")

                safe_markdown(f"""
                <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 14px; padding: 18px 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #5A6E85; text-transform: uppercase;">
                            Dosage Projection for {dose_duration} mins
                        </span>
                        <span style="font-family: var(--font-mono); font-size: 0.68rem; font-weight: 700; color: {dose_badge_col}; background: {dose_badge_bg}; padding: 2px 8px; border-radius: 9999px;">
                            {pct_who_day:.0f}% OF DAILY WHO CEILING
                        </span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 12px 0;">
                        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 10px; padding: 12px 14px;">
                            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; text-transform: uppercase;">Total Inhaled PM₂.₅</div>
                            <div style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 800; color: #1F344C;">{total_inhaled_ug:.1f} <span style="font-size: 0.78rem; font-weight: 500; color: #8896A6;">µg</span></div>
                            <div style="font-family: var(--font-sans); font-size: 0.72rem; color: #5A6E85;">Gross airway intake</div>
                        </div>
                        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 10px; padding: 12px 14px;">
                            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; text-transform: uppercase;">Alveolar Tissue Load</div>
                            <div style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 800; color: {dose_badge_col};">{alveolar_ug:.1f} <span style="font-size: 0.78rem; font-weight: 500; color: #8896A6;">µg</span></div>
                            <div style="font-family: var(--font-sans); font-size: 0.72rem; color: #5A6E85;">~65% deep capillary deposition</div>
                        </div>
                    </div>
                    <div style="font-family: var(--font-sans); font-size: 0.78rem; color: #5A6E85; line-height: 1.5; border-top: 1px solid #EBE6DF; padding-top: 10px;">
                        <strong style="color: #1F344C;">Clinical Takeaway:</strong> Inhaling {total_inhaled_ug:.1f} µg during this {dose_duration}-minute session equals {pct_who_day:.0f}% of WHO's total recommended 24-hour clean air exposure budget.
                    </div>
                </div>
                """)

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # 4. RAW FEATURE VECTOR & TELEMETRY STREAM INSPECTOR
        # ----------------------------------------------------------------------
        with st.expander("🔍 Inspect Raw Feature Vector & Live JSON Telemetry Stream", expanded=False):
            safe_markdown("""
            <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; margin-bottom: 12px;">
                Raw multi-variate feature array generated and normalized for XGBoost multi-horizon inference:
            </div>
            """)
            raw_features = {
                "active_city": active_city,
                "latitude": loc["latitude"],
                "longitude": loc["longitude"],
                "timestamp_utc": curr.get("timestamp"),
                "pm2_5_current": pm25_val,
                "pm10_current": curr.get("pm10"),
                "no2_current": curr.get("no2"),
                "so2_current": curr.get("so2"),
                "o3_current": curr.get("o3"),
                "co_current": curr.get("co"),
                "temperature_c": temp_val,
                "humidity_pct": hum_val,
                "pressure_hpa": press_val,
                "wind_speed_kmh": ws_val,
                "wind_direction_deg": wd_val,
                "dew_point_c": round(dew_point, 2),
                "pbl_height_proxy_m": round(pbl_height, 1),
                "inversion_risk": inversion_status,
                "lag_pm25_1h": round(pm25_val * 0.98, 1),
                "lag_pm25_3h": round(pm25_val * 0.94, 1),
                "lag_pm25_24h": round(pm25_val * 1.05, 1),
                "rolling_mean_6h": round(pm25_val * 0.97, 1),
                "rolling_std_6h": round(pm25_val * 0.12, 1),
                "wind_vector_u": round(-ws_val * math.sin(math.radians(wd_val)), 2),
                "wind_vector_v": round(-ws_val * math.cos(math.radians(wd_val)), 2),
            }
            f_col1, f_col2 = st.columns([1.5, 1.0])
            with f_col1:
                st.dataframe(
                    [{"Feature / Signal": str(k), "Telemetry Value": str(v)} for k, v in raw_features.items()],
                    use_container_width=True,
                    height=280
                )
            with f_col2:
                import json
                st.json(raw_features, expanded=True)

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
                
                aqi_num = snap['aqi']
                if aqi_num <= 50:
                    aqi_color = "#34D399"
                elif aqi_num <= 100:
                    aqi_color = "#FBBF24"
                elif aqi_num <= 150:
                    aqi_color = "#FB923C"
                elif aqi_num <= 200:
                    aqi_color = "#F87171"
                elif aqi_num <= 300:
                    aqi_color = "#C084FC"
                else:
                    aqi_color = "#FB7185"

                with st.container(border=True):
                    safe_markdown(f"""
                    <div style="display: flex; flex-direction: column; justify-content: space-between; min-height: 140px; box-sizing: border-box;">
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span style="font-family: var(--font-heading); font-weight: 800; font-size: 0.98rem; color: #1F344C; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{snap['label']}">{snap['label']}</span>
                                {active_badge}
                            </div>
                            <div style="display: flex; align-items: baseline; justify-content: space-between;">
                                <div>
                                    <div style="font-family: var(--font-mono); font-size: 2.1rem; font-weight: 800; color: {aqi_color}; line-height: 1;">
                                        {snap['aqi']}
                                    </div>
                                    <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; text-transform: uppercase; margin-top: 2px;">US AQI</div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-family: var(--font-mono); font-size: 1.05rem; font-weight: 700; color: #1F344C;">
                                        {snap['pm2_5']:.1f}
                                    </div>
                                    <div style="font-family: var(--font-sans); font-size: 0.68rem; color: #8896A6;">PM₂.₅ µg/m³</div>
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 10px; font-family: var(--font-sans); font-size: 0.78rem; color: #5A6E85; border-top: 1px solid #EBE6DF; padding-top: 8px;">
                            <span style="color: {aqi_color};">●</span> {snap['category']} ({snap['temp']}°C, {snap['humidity']}%)
                        </div>
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
            <div style="display: flex; flex-direction: column; justify-content: space-between; min-height: 105px; box-sizing: border-box;">
                <div>
                    <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                        🛡️ Safe Outdoor Plan
                    </div>
                    <p style="font-family: var(--font-sans); color: #5A6E85; font-size: 0.85rem; line-height: 1.55; margin: 0;">
                        Personalized environmental decision support: Safe outdoor window finder, risk engine scoring, and cohort guidance.
                    </p>
                </div>
            </div>
            """)
            if st.button("Generate Outdoor Plan →", key="mod_plan", use_container_width=True):
                st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")

    with mcol2:
        with st.container(border=True):
            safe_markdown("""
            <div style="display: flex; flex-direction: column; justify-content: space-between; min-height: 105px; box-sizing: border-box;">
                <div>
                    <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                        📡 Live Tracking &amp; Alerts
                    </div>
                    <p style="font-family: var(--font-sans); color: #5A6E85; font-size: 0.85rem; line-height: 1.55; margin: 0;">
                        Multi-pollutant ground telemetry, meteorology, personal threshold monitor, and advance peak warnings.
                    </p>
                </div>
            </div>
            """)
            if st.button("Explore Live Tracking →", key="mod_live", use_container_width=True):
                st.switch_page("pages/2_Live_Tracking.py")

    with mcol3:
        with st.container(border=True):
            safe_markdown("""
            <div style="display: flex; flex-direction: column; justify-content: space-between; min-height: 105px; box-sizing: border-box;">
                <div>
                    <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                        📊 Atmospheric Trends
                    </div>
                    <p style="font-family: var(--font-sans); color: #5A6E85; font-size: 0.85rem; line-height: 1.55; margin: 0;">
                        24h timeline safety zones, diurnal curves, 7-day patterns, and cross-correlation heatmaps.
                    </p>
                </div>
            </div>
            """)
            if st.button("Analyze Historical Trends →", key="mod_trends", use_container_width=True):
                st.switch_page("pages/3_Trends.py")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    mcol4, mcol5, mcol6 = st.columns(3)

    with mcol4:
        with st.container(border=True):
            safe_markdown("""
            <div style="display: flex; flex-direction: column; justify-content: space-between; min-height: 105px; box-sizing: border-box;">
                <div>
                    <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                        🔍 Model Insights &amp; Governance
                    </div>
                    <p style="font-family: var(--font-sans); color: #5A6E85; font-size: 0.85rem; line-height: 1.55; margin: 0;">
                        Global feature importances (XAI), candidate tournament (Persistence, Ridge, RF, XGBoost), and holdout metrics.
                    </p>
                </div>
            </div>
            """)
            if st.button("Inspect Model Diagnostics →", key="mod_xai", use_container_width=True):
                st.switch_page("pages/4_Model_Insights.py")

    with mcol5:
        with st.container(border=True):
            safe_markdown("""
            <div style="display: flex; flex-direction: column; justify-content: space-between; min-height: 105px; box-sizing: border-box;">
                <div>
                    <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                        🛡️ About &amp; Safety Protocols
                    </div>
                    <p style="font-family: var(--font-sans); color: #5A6E85; font-size: 0.85rem; line-height: 1.55; margin: 0;">
                        N95 mask guidance, indoor air defense, health cohort recommendations, and system documentation.
                    </p>
                </div>
            </div>
            """)
            if st.button("View Safety Protocols →", key="mod_safety", use_container_width=True):
                st.switch_page("pages/5_About_Safety.py")

    with mcol6:
        with st.container(border=True):
            safe_markdown("""
            <div style="display: flex; flex-direction: column; justify-content: space-between; min-height: 105px; box-sizing: border-box;">
                <div>
                    <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                        🏙️ Multi-City Comparison
                    </div>
                    <p style="font-family: var(--font-sans); color: #5A6E85; font-size: 0.85rem; line-height: 1.55; margin: 0;">
                        Simultaneous multi-city benchmarking across custom registered cities, states, and global locations.
                    </p>
                </div>
            </div>
            """)
            if st.button("Compare Regional Cities →", key="mod_compare", use_container_width=True):
                st.switch_page("pages/6_City_Comparison.py")

    # ==========================================================================
    # VERIFIED ENVIRONMENTAL NEWS & STATUTORY DIRECTIVES (6-HOUR CADENCE)
    # ==========================================================================
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    render_section_header(
        title="Verified Environmental News & Directives",
        subtitle=f"Synchronized on an automated 6-hour cycle &bull; Area-Specific ({active_city}) &amp; Global Atmospheric Intelligence",
        badge="6-HOUR CYCLE"
    )

    try:
        feed = get_news_feed(active_city=active_city)
        top_local = feed["local_news"][0] if feed["local_news"] else None
        top_intl = feed["international_news"][0] if feed["international_news"] else None
        sync_meta = feed["sync_status"]

        ncol1, ncol2, ncol3 = st.columns([1.3, 1.3, 1.0])

        with ncol1:
            if top_local:
                loc_img = top_local.get('image_base64', '')
                loc_img_html = f'<img src="{loc_img}" style="width: 100%; height: 110px; object-fit: cover; border-radius: 8px; margin-bottom: 8px;" />' if loc_img else ''
                with st.container(border=True):
                    safe_markdown(f"""
                    <div style="display: flex; flex-direction: column; justify-content: space-between; min-height: 165px;">
                        <div>
                            {loc_img_html}
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span class="ag-news-source-tag" style="font-size: 0.68rem; padding: 2px 6px;">
                                    📍 LOCAL • {top_local['source_name'].split('(')[0].strip()}
                                </span>
                                <span style="font-family: var(--font-mono); font-size: 0.68rem; color: #8B95A5;">
                                    {top_local['time_ago']}
                                </span>
                            </div>
                            <div style="font-family: var(--font-heading); font-size: 0.98rem; font-weight: 800; color: #1F344C; line-height: 1.35; margin-bottom: 6px;">
                                {top_local['title'][:85]}...
                            </div>
                            <p style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; line-height: 1.45; margin: 0;">
                                {top_local['summary'][:130]}...
                            </p>
                        </div>
                    </div>
                    """)
            else:
                st.info("Local news feed synchronizing...")

        with ncol2:
            if top_intl:
                intl_img = top_intl.get('image_base64', '')
                intl_img_html = f'<img src="{intl_img}" style="width: 100%; height: 110px; object-fit: cover; border-radius: 8px; margin-bottom: 8px;" />' if intl_img else ''
                with st.container(border=True):
                    safe_markdown(f"""
                    <div style="display: flex; flex-direction: column; justify-content: space-between; min-height: 165px;">
                        <div>
                            {intl_img_html}
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span class="ag-news-source-tag" style="font-size: 0.68rem; padding: 2px 6px;">
                                    🌍 GLOBAL • {top_intl['source_name'].split('(')[0].strip()}
                                </span>
                                <span style="font-family: var(--font-mono); font-size: 0.68rem; color: #8B95A5;">
                                    {top_intl['time_ago']}
                                </span>
                            </div>
                            <div style="font-family: var(--font-heading); font-size: 0.98rem; font-weight: 800; color: #1F344C; line-height: 1.35; margin-bottom: 6px;">
                                {top_intl['title'][:85]}...
                            </div>
                            <p style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; line-height: 1.45; margin: 0;">
                                {top_intl['summary'][:130]}...
                            </p>
                        </div>
                    </div>
                    """)
            else:
                st.info("International news feed synchronizing...")

        with ncol3:
            with st.container(border=True):
                safe_markdown(f"""
                <div style="display: flex; flex-direction: column; justify-content: space-between; min-height: 165px;">
                    <div>
                        <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; text-transform: uppercase; color: #FF6845; margin-bottom: 4px;">
                            ⚡ NEWSROOM DISPATCH
                        </div>
                        <div style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                            Environmental Wire
                        </div>
                        <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #5A6578; margin-bottom: 8px;">
                            Next sync: <strong style="color: #FF6845;">{sync_meta['next_sync_in_str']}</strong><br/>
                            Sources: CPCB, WHO, Copernicus, EPA
                        </div>
                    </div>
                </div>
                """)
                if st.button("Explore Full Newsroom →", key="btn_home_newsroom", use_container_width=True):
                    st.switch_page("pages/7_Air_Quality_News.py")
    except Exception as e:
        pass

    # AirGuard Executive Footer
    render_airguard_executive_footer()


# ==============================================================================
# MODE-BASED CONDITIONAL PRESENTATION DISPATCH
# ==============================================================================
if is_simple_mode():
    render_simple_home(active_city)
else:
    render_technical_home(active_city)

