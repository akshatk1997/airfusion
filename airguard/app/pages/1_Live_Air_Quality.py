"""
Live Air Quality Dashboard Page for AirGuard.
Displays real-time multi-pollutant telemetry, atmospheric conditions,
AQI classification hero card, comparative WHO limits, and clinical health guidance.
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CACHE_TTL_SECONDS
from src.data_collection import geocode_city, fetch_current_air_quality
from src.database import get_or_create_location, upsert_air_quality_dataframe
from app.components.navbar import render_global_navbar
from app.components.cards import render_aqi_hero_card
from app.components.health_advisory import render_health_advisory_panel
from app.components.design_system import (
    render_section_header,
    render_metric_tile,
    render_callout,
    format_location_label,
    ICONS
)

st.set_page_config(
    page_title="Live Air Quality — AirGuard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="auto"
)

# Global Navbar with state-synced active location
target_city = render_global_navbar("Live Air Quality")

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_live_data(city_name: str, force_refresh: int = 0):
    loc_meta = geocode_city(city_name)
    if not loc_meta:
        return None, None
    curr_data = fetch_current_air_quality(loc_meta["latitude"], loc_meta["longitude"])
    return loc_meta, curr_data

# Primary Action Toolbar
col_head, col_actions = st.columns([2, 1.2])
with col_head:
    render_section_header(
        title=f"Atmospheric Telemetry — {target_city}",
        subtitle="Continuous multi-pollutant concentrations and boundary layer meteorology.",
        badge="REAL-TIME TELEMETRY"
    )

with col_actions:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        if st.button("🔄 Refresh Data", key="refresh_telemetry", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with bcol2:
        if st.button("📈 View Forecast →", key="goto_forecast", use_container_width=True):
            st.switch_page("pages/2_Forecast.py")

with st.spinner(f"Ingesting real-time atmospheric telemetry for {target_city}..."):
    loc_meta, curr_data = get_live_data(target_city)

if not loc_meta or not curr_data:
    render_callout(
        title="Location Unresolved",
        message=f"Could not retrieve telemetry for '{target_city}'. Please verify spelling or pick a location from the active city dropdown above.",
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
        "co": curr_data.get("co"),
        "so2": curr_data.get("so2"),
        "temperature": curr_data.get("temperature"),
        "humidity": curr_data.get("humidity"),
        "wind_speed": curr_data.get("wind_speed"),
        "wind_direction": curr_data.get("wind_direction"),
        "pressure": curr_data.get("pressure")
    }])
    upsert_air_quality_dataframe(df_live, location_id=loc_id)
except Exception as e:
    st.sidebar.warning(f"Database logging note: {e}")

# Display Hero AQI Card with Scale Bar
pm25_val = float(curr_data.get("pm2_5", 0.0))
aqi_val = int(curr_data.get("aqi", 0))
category = curr_data.get("aqi_category", "Unknown")
color = curr_data.get("aqi_color", "#10B981")
timestamp_str = curr_data.get("timestamp", "").replace("T", " ")

render_aqi_hero_card(
    aqi=aqi_val,
    category=category,
    color=color,
    city=format_location_label(loc_meta),
    timestamp=timestamp_str,
    pm25_val=pm25_val
)

# 1. Pollutants Telemetry Grid
render_section_header(
    title="Particulate & Gaseous Pollutants",
    subtitle="Continuous atmospheric mass concentrations for regulated criteria air pollutants.",
    badge="POLLUTANT CONCENTRATIONS"
)

pcol1, pcol2, pcol3 = st.columns(3)
pcol4, pcol5, pcol6 = st.columns(3)

with pcol1:
    render_metric_tile(
        label="PM₂.₅ (Fine Inhalable)",
        value=curr_data.get("pm2_5"),
        unit="µg/m³",
        subtext="Combustion aerosol (<2.5 µm)",
        icon="pulse"
    )
with pcol2:
    render_metric_tile(
        label="PM₁₀ (Coarse Particles)",
        value=curr_data.get("pm10"),
        unit="µg/m³",
        subtext="Mechanical dust & pollen (<10 µm)",
        icon="pulse"
    )
with pcol3:
    render_metric_tile(
        label="NO₂ (Nitrogen Dioxide)",
        value=curr_data.get("no2"),
        unit="µg/m³",
        subtext="Vehicular exhaust & power plants",
        icon="pulse"
    )

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

with pcol4:
    render_metric_tile(
        label="O₃ (Ground Ozone)",
        value=curr_data.get("o3"),
        unit="µg/m³",
        subtext="Photochemical summer smog",
        icon="pulse"
    )
with pcol5:
    render_metric_tile(
        label="CO (Carbon Monoxide)",
        value=curr_data.get("co"),
        unit="µg/m³",
        subtext="Incomplete vehicular fuel combustion",
        icon="pulse"
    )
with pcol6:
    render_metric_tile(
        label="SO₂ (Sulphur Dioxide)",
        value=curr_data.get("so2"),
        unit="µg/m³",
        subtext="Heavy fuel oil & industrial smelting",
        icon="pulse"
    )

st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

# 2. International Health Guideline Benchmarks (WHO 24h Thresholds)
render_section_header(
    title="Current Concentrations vs WHO Safe Limits",
    subtitle="Measured ambient concentrations benchmarked against World Health Organization 24-hour guidelines.",
    badge="REGULATORY BENCHMARKS"
)

# Benchmark limits: PM2.5 (15), PM10 (45), NO2 (25), SO2 (40), O3 (100)
who_benchmarks = [
    {"pollutant": "PM2.5", "current": curr_data.get("pm2_5", 0.0), "limit": 15.0, "unit": "µg/m³"},
    {"pollutant": "PM10", "current": curr_data.get("pm10", 0.0), "limit": 45.0, "unit": "µg/m³"},
    {"pollutant": "NO2", "current": curr_data.get("no2", 0.0), "limit": 25.0, "unit": "µg/m³"},
    {"pollutant": "SO2", "current": curr_data.get("so2", 0.0), "limit": 40.0, "unit": "µg/m³"},
    {"pollutant": "O3", "current": curr_data.get("o3", 0.0), "limit": 100.0, "unit": "µg/m³"},
]

df_who = pd.DataFrame(who_benchmarks)
df_who["ratio"] = (df_who["current"] / df_who["limit"]) * 100.0

bar_colors = ["#10B981" if row["current"] <= row["limit"] else "#F59E0B" for _, row in df_who.iterrows()]

fig_who = go.Figure()
fig_who.add_trace(go.Bar(
    y=df_who["pollutant"],
    x=df_who["current"],
    name="Current Concentration",
    orientation="h",
    marker=dict(color=bar_colors, cornerradius=4),
    text=df_who["current"].apply(lambda v: f"{v:.1f}"),
    textposition="outside",
    textfont=dict(family="JetBrains Mono, monospace", size=11, color="#F8FAFC"),
    hovertemplate="Measured: <b>%{x:.1f} µg/m³</b><extra></extra>"
))
fig_who.add_trace(go.Bar(
    y=df_who["pollutant"],
    x=df_who["limit"],
    name="WHO 24h Safe Limit",
    orientation="h",
    marker=dict(color="rgba(148, 163, 184, 0.35)", cornerradius=4),
    text=df_who["limit"].apply(lambda v: f"{v:.0f}"),
    textposition="outside",
    textfont=dict(family="JetBrains Mono, monospace", size=11, color="#94A3B8"),
    hovertemplate="WHO Safe Ceiling: <b>%{x:.1f} µg/m³</b><extra></extra>"
))
fig_who.update_layout(
    template="plotly_dark",
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#F8FAFC"),
    plot_bgcolor="rgba(17, 24, 39, 0.5)",
    paper_bgcolor="rgba(0, 0, 0, 0)",
    height=290,
    barmode="group",
    bargap=0.25,
    bargroupgap=0.1,
    xaxis_title="Concentration (µg/m³)",
    yaxis_title="",
    yaxis=dict(autorange="reversed"),
    margin=dict(l=70, r=50, t=30, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="right", x=1)
)
st.plotly_chart(fig_who, use_container_width=True)

st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

# 3. Meteorological Context Grid
render_section_header(
    title="Meteorological Boundary Dynamics",
    subtitle="Atmospheric conditions governing particulate dispersion, stagnation, and secondary condensation.",
    badge="WEATHER TELEMETRY"
)

wcol1, wcol2, wcol3, wcol4 = st.columns(4)

with wcol1:
    render_metric_tile(
        label="Ambient Temperature",
        value=curr_data.get("temperature"),
        unit="°C",
        subtext="Surface 2m temperature",
        icon="temp"
    )
with wcol2:
    render_metric_tile(
        label="Relative Humidity",
        value=curr_data.get("humidity"),
        unit="%",
        subtext="Aerosol hydration factor",
        icon="droplet"
    )
with wcol3:
    render_metric_tile(
        label="Wind Velocity",
        value=curr_data.get("wind_speed"),
        unit="km/h",
        subtext="Ventilation & transport rate",
        icon="wind"
    )
with wcol4:
    render_metric_tile(
        label="Barometric Pressure",
        value=curr_data.get("pressure"),
        unit="hPa",
        subtext="Atmospheric stability index",
        icon="gauge"
    )

st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

# 4. Clinical Health Advisory Section
render_section_header(
    title="Clinical Health Advisory & Safety Protocols",
    subtitle="Preventive public health precautions tailored to the current AQI risk level.",
    badge="MEDICAL GUIDELINES"
)
render_health_advisory_panel(aqi_val)

# 5. Data Export Section
st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
export_dict = {
    "City": [loc_meta["city"]],
    "Latitude": [loc_meta["latitude"]],
    "Longitude": [loc_meta["longitude"]],
    "Timestamp": [timestamp_str],
    "AQI": [aqi_val],
    "Category": [category],
    "PM2.5 (ug/m3)": [pm25_val],
    "PM10 (ug/m3)": [curr_data.get("pm10")],
    "NO2 (ug/m3)": [curr_data.get("no2")],
    "O3 (ug/m3)": [curr_data.get("o3")],
    "CO (ug/m3)": [curr_data.get("co")],
    "SO2 (ug/m3)": [curr_data.get("so2")],
    "Temperature (C)": [curr_data.get("temperature")],
    "Humidity (%)": [curr_data.get("humidity")],
    "Wind Speed (km/h)": [curr_data.get("wind_speed")],
    "Pressure (hPa)": [curr_data.get("pressure")]
}
df_export = pd.DataFrame(export_dict)
csv_bytes = df_export.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Telemetry Snapshot as CSV",
    data=csv_bytes,
    file_name=f"{loc_meta['city'].lower()}_telemetry_snapshot.csv",
    mime="text/csv"
)
