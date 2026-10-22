"""
Multi-City Air Quality Comparison Page for AirGuard.
Allows users to benchmark 2 to 5 locations simultaneously, ranking
the cleanest and most polluted locations across current telemetry,
+24h ML forecasts, and historical baselines.
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PRESET_CITIES
from src.data_collection import fetch_current_air_quality, geocode_city
from src.database import fetch_historical_records, fetch_all_locations, get_or_create_location
from src.predict import generate_forecast, is_model_trained
from app.components.navbar import render_global_navbar
from app.components.design_system import (
    render_section_header,
    render_metric_tile,
    render_callout,
    render_badge,
    safe_markdown,
    format_location_label,
    ICONS
)
from app.components.charts import (
    create_city_grouped_benchmark_chart,
    create_city_comparison_bars
)

st.set_page_config(
    page_title="City Comparison — AirGuard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Global Navbar with active city synchronization
current_active_city = render_global_navbar("City Comparison")

# Page Header
render_section_header(
    title="Regional Multi-City Atmospheric Benchmarking",
    subtitle="Synchronized comparative telemetry across 2 to 5 locations evaluating current pollution, 24-hour machine learning projections, and historical baselines.",
    badge="REGIONAL BENCHMARKING MATRIX"
)

# Target City Selector & Action Toolbar
available_cities = list(PRESET_CITIES.keys())
if "location_registry" in st.session_state and st.session_state["location_registry"]:
    for k in st.session_state["location_registry"].keys():
        if k not in available_cities:
            available_cities.append(k)

try:
    db_locs = fetch_all_locations()
    for d in db_locs:
        c = d["city"]
        if c not in available_cities:
            available_cities.append(c)
except Exception:
    pass

default_selection = ["Chandigarh", "Mohali", "Panchkula", "Delhi"]
# Ensure current active city is included by default if valid
if current_active_city in available_cities and current_active_city not in default_selection:
    default_selection.insert(0, current_active_city)

def comp_location_label(c_key: str) -> str:
    loc = geocode_city(c_key)
    return format_location_label(loc) if loc else c_key

# Custom Location Addition Form for Comparison
with st.expander("➕ Add Custom City, State, Country to Comparison Fleet", expanded=False):
    with st.form("add_comp_location_form", clear_on_submit=True):
        fcol1, fcol2, fcol3, fcol4 = st.columns([1.5, 1.2, 1.2, 1.1])
        with fcol1:
            comp_city_in = st.text_input("City / Place Name *", placeholder="e.g. Panchkula, Kolkata, Sydney")
        with fcol2:
            comp_state_in = st.text_input("State / Province", placeholder="e.g. Haryana, West Bengal, NSW")
        with fcol3:
            comp_country_in = st.text_input("Country", placeholder="e.g. India, Australia")
        with fcol4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            btn_add_comp = st.form_submit_button("🚀 Add to Fleet", use_container_width=True)

        if btn_add_comp:
            if not comp_city_in.strip():
                st.error("Please enter a city name.")
            else:
                q_tokens = [comp_city_in.strip()]
                if comp_state_in.strip():
                    q_tokens.append(comp_state_in.strip())
                if comp_country_in.strip():
                    q_tokens.append(comp_country_in.strip())
                q_str = ", ".join(q_tokens)
                with st.spinner(f"Geocoding '{q_str}'..."):
                    res_loc = geocode_city(q_str)
                    if res_loc:
                        res_city = res_loc["city"]
                        try:
                            get_or_create_location(
                                city=res_city,
                                latitude=res_loc["latitude"],
                                longitude=res_loc["longitude"],
                                country=res_loc.get("country", comp_country_in.strip()),
                                state=res_loc.get("state", comp_state_in.strip())
                            )
                        except Exception:
                            pass
                        if "location_registry" in st.session_state:
                            st.session_state["location_registry"][res_city] = res_loc
                        if res_city not in available_cities:
                            available_cities.append(res_city)
                        st.success(f"✅ Added {format_location_label(res_loc)}! You can now select it below.")
                        st.rerun()
                    else:
                        st.error(f"Could not resolve '{q_str}'. Please check spelling.")

ctrl_col1, ctrl_col2 = st.columns([2.5, 1.5])

with ctrl_col1:
    selected_cities = st.multiselect(
        "Choose 2 to 5 Benchmark Locations",
        options=available_cities,
        default=[c for c in default_selection if c in available_cities][:4],
        format_func=comp_location_label,
        help="Select between 2 and 5 cities to generate comparative cross-regional intelligence"
    )

with ctrl_col2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        if st.button("🔄 Refresh Data", use_container_width=True, help="Re-sync current live atmospheric feeds"):
            st.cache_data.clear()
            st.rerun()
    with bcol2:
        if st.button("⚡ Live Telemetry", use_container_width=True, help=f"Inspect live sensors for {current_active_city}"):
            st.switch_page("pages/1_Live_Air_Quality.py")

# Validation
if len(selected_cities) < 2:
    render_callout(
        title="Insufficient Locations Selected",
        message="Please select at least 2 target locations to activate multi-city comparative evaluation and ranking.",
        variant="info",
        icon="info"
    )
    st.stop()

if len(selected_cities) > 5:
    st.warning("⚠️ For optimal visual clarity, comparison is restricted to the first 5 selected locations.")
    selected_cities = selected_cities[:5]

# Synchronized Telemetry Ingestion
@st.cache_data(ttl=180)
def get_multi_city_telemetry(cities_list: list[str]) -> list[dict]:
    records = []
    for city in cities_list:
        loc = geocode_city(city)
        if not loc:
            continue
        curr = fetch_current_air_quality(loc["latitude"], loc["longitude"])
        loc_label = format_location_label(loc)

        # Fetch historical average from local DB
        df_hist = fetch_historical_records(city=city)
        hist_avg = df_hist["pm2_5"].mean() if not df_hist.empty else curr.get("pm2_5", 0.0)

        # Generate +24h ML forecast
        fc_val = None
        if is_model_trained():
            try:
                _, summary = generate_forecast(city, horizon_hours=24)
                fc_val = summary.get("forecast_24h_pm2_5")
            except Exception:
                fc_val = curr.get("pm2_5", 0.0)
        else:
            fc_val = curr.get("pm2_5", 0.0)

        records.append({
            "city": city,
            "location_label": loc_label,
            "current_aqi": int(curr.get("aqi", 0)),
            "current_category": curr.get("aqi_category", "Moderate"),
            "current_pm2_5": float(curr.get("pm2_5", 0.0)),
            "current_pm10": float(curr.get("pm10", 0.0)),
            "current_no2": float(curr.get("no2", 0.0)),
            "current_o3": float(curr.get("o3", 0.0)),
            "forecast_24h_pm2_5": round(float(fc_val or curr.get("pm2_5", 0.0)), 1),
            "historical_mean_pm2_5": round(float(hist_avg), 1),
            "temperature": curr.get("temperature", "--"),
            "humidity": curr.get("humidity", "--"),
            "wind_speed": curr.get("wind_speed", "--")
        })
    return records

with st.spinner(f"Ingesting synchronized atmospheric telemetry across {len(selected_cities)} regional centers..."):
    city_records = get_multi_city_telemetry(selected_cities)

if not city_records:
    render_callout(
        title="Telemetry Ingestion Failure",
        message="Could not retrieve atmospheric data for the selected cities. Please verify network access.",
        variant="alert",
        icon="alert"
    )
    st.stop()

df_comp = pd.DataFrame(city_records)

# Cleanest vs Most Polluted Ranking Spotlight
cleanest_row = df_comp.sort_values("current_pm2_5", ascending=True).iloc[0]
polluted_row = df_comp.sort_values("current_pm2_5", ascending=False).iloc[0]

rank_col1, rank_col2 = st.columns(2)

with rank_col1:
    clean_city = cleanest_row['city']
    clean_label = cleanest_row.get('location_label', clean_city)
    clean_cat = cleanest_row['current_category']
    badge_cls = "badge-good" if clean_cat == "Good" else "badge-moderate"
    with st.container(border=True):
        safe_markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2);">
                <div style="display: flex; align-items: center; gap: var(--space-2);">
                    <div style="width: 20px; height: 20px; color: var(--color-good);">{ICONS['check']}</div>
                    <span style="font-size: var(--text-xs); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--color-good);">Cleanest Selected Location</span>
                </div>
                <span class="badge {badge_cls}">{clean_cat.upper()}</span>
            </div>
            <div style="font-size: var(--text-2xl); font-weight: 800; color: var(--color-slate-100); margin: var(--space-1) 0;">
                {clean_label}
            </div>
            <div style="font-size: var(--text-sm); color: var(--color-slate-300); display: flex; gap: var(--space-4); margin-bottom: var(--space-3);">
                <span>Current AQI: <strong style="color: var(--color-good); font-family: var(--font-mono); font-size: var(--text-base);">{cleanest_row['current_aqi']}</strong></span>
                <span>PM₂.₅: <strong style="color: var(--color-slate-100); font-family: var(--font-mono); font-size: var(--text-base);">{cleanest_row['current_pm2_5']:.1f} µg/m³</strong></span>
                <span>Wind: <strong style="color: var(--color-slate-200); font-family: var(--font-mono);">{cleanest_row['wind_speed']} km/h</strong></span>
            </div>
            """
        )
        if st.button(f"🔍 Set {clean_city} as Active Monitored City", key="btn_set_clean", use_container_width=True):
            st.session_state["selected_city"] = clean_city
            st.switch_page("pages/1_Live_Air_Quality.py")

with rank_col2:
    poll_city = polluted_row['city']
    poll_label = polluted_row.get('location_label', poll_city)
    poll_cat = polluted_row['current_category']
    poll_badge_cls = "badge-alert" if "Unhealthy" in poll_cat or "Hazardous" in poll_cat else "badge-warning"
    poll_border = "var(--color-severe)" if "Unhealthy" in poll_cat or "Hazardous" in poll_cat else "var(--color-moderate)"
    with st.container(border=True):
        safe_markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2);">
                <div style="display: flex; align-items: center; gap: var(--space-2);">
                    <div style="width: 20px; height: 20px; color: {poll_border};">{ICONS['alert']}</div>
                    <span style="font-size: var(--text-xs); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: {poll_border};">Highest Contamination Burden</span>
                </div>
                <span class="badge {poll_badge_cls}">{poll_cat.upper()}</span>
            </div>
            <div style="font-size: var(--text-2xl); font-weight: 800; color: var(--color-slate-100); margin: var(--space-1) 0;">
                {poll_label}
            </div>
            <div style="font-size: var(--text-sm); color: var(--color-slate-300); display: flex; gap: var(--space-4); margin-bottom: var(--space-3);">
                <span>Current AQI: <strong style="color: {poll_border}; font-family: var(--font-mono); font-size: var(--text-base);">{polluted_row['current_aqi']}</strong></span>
                <span>PM₂.₅: <strong style="color: var(--color-slate-100); font-family: var(--font-mono); font-size: var(--text-base);">{polluted_row['current_pm2_5']:.1f} µg/m³</strong></span>
                <span>Wind: <strong style="color: var(--color-slate-200); font-family: var(--font-mono);">{polluted_row['wind_speed']} km/h</strong></span>
            </div>
            """
        )
        if st.button(f"🔍 Set {poll_city} as Active Monitored City", key="btn_set_poll", use_container_width=True):
            st.session_state["selected_city"] = poll_city
            st.switch_page("pages/1_Live_Air_Quality.py")

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# Deep-Dive Visual Comparison Tabs
tab_bars, tab_aqi, tab_matrix = st.tabs([
    "📊 Particulate Benchmark (Current vs +24h vs Baseline)",
    "🎯 Normalized AQI Index Comparison",
    "📋 Cross-Regional Telemetry Matrix"
])

# ----------------- TAB 1: GROUPED PARTICULATE BENCHMARK -----------------
with tab_bars:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.plotly_chart(create_city_grouped_benchmark_chart(df_comp), use_container_width=True)

    # Cross-regional trend insight callout
    pm_spread = polluted_row['current_pm2_5'] - cleanest_row['current_pm2_5']
    trend_summary = (
        f"**Regional Variance:** Across the {len(df_comp)} evaluated locations, ambient PM₂.₅ concentrations vary by "
        f"**{pm_spread:.1f} µg/m³**. **{cleanest_row['city']}** maintains the cleanest air shed ({cleanest_row['current_pm2_5']:.1f} µg/m³), "
        f"while **{polluted_row['city']}** registers **{(polluted_row['current_pm2_5'] / max(1.0, cleanest_row['current_pm2_5'])):.1f}x** higher particulate burden. "
        f"The +24-hour machine learning projections indicate particulate levels will "
        f"{'elevate' if df_comp['forecast_24h_pm2_5'].mean() > df_comp['current_pm2_5'].mean() else 'moderate'} "
        f"across the regional corridor over the next diurnal cycle."
    )
    render_callout(
        title="Regional Atmospheric Gradient Insight",
        message=trend_summary,
        variant="info",
        icon="check"
    )

# ----------------- TAB 2: NORMALIZED AQI COMPARISON -----------------
with tab_aqi:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.plotly_chart(create_city_comparison_bars(df_comp, metric="current_aqi", title="Comparative Air Quality Index (US AQI Scale)"), use_container_width=True)

    # Criteria Pollutant Comparison Bar
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(create_city_comparison_bars(df_comp, metric="current_pm10", title="Coarse Particulate Comparison (PM₁₀ µg/m³)"), use_container_width=True)
    with c2:
        st.plotly_chart(create_city_comparison_bars(df_comp, metric="current_no2", title="Nitrogen Dioxide Comparison (NO₂ µg/m³)"), use_container_width=True)

# ----------------- TAB 3: MATRIX & RAW DATA -----------------
with tab_matrix:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    display_matrix = df_comp[[
        "city", "current_aqi", "current_category", "current_pm2_5",
        "forecast_24h_pm2_5", "historical_mean_pm2_5", "temperature", "humidity", "wind_speed"
    ]].copy()
    display_matrix.rename(columns={
        "city": "Location",
        "current_aqi": "Current AQI",
        "current_category": "Health Status",
        "current_pm2_5": "Current PM2.5 (µg/m³)",
        "forecast_24h_pm2_5": "+24h Projected (µg/m³)",
        "historical_mean_pm2_5": "Historical Mean (µg/m³)",
        "temperature": "Temp (°C)",
        "humidity": "Humidity (%)",
        "wind_speed": "Wind (km/h)"
    }, inplace=True)
    st.dataframe(display_matrix, use_container_width=True, hide_index=True)

# CSV Export Section
st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
exp_col1, exp_col2 = st.columns([3, 1])
with exp_col2:
    csv_comp = df_comp.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Export Benchmarking Dataset ({len(df_comp)} Cities)",
        data=csv_comp,
        file_name="airguard_regional_city_comparison.csv",
        mime="text/csv",
        use_container_width=True
    )
