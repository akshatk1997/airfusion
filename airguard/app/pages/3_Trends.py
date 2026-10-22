"""
Atmospheric Trends & Longitudinal Time-Series Analytics for AirGuard.
Displays multi-scale historical and projected trends:
- 24-Hour Historical & Forecast Trend with Safe/Unsafe Zones
- Diurnal Pollution Pattern (Hourly Rhythms 00:00–23:00)
- Last 7-Day & Multi-Day Longitudinal Timeline
- Atmospheric Cross-Correlation Heatmap (PM2.5, Pollutants, Meteorology)
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import fetch_historical_records, get_user_profile
from src.data_collection import fetch_and_store_city_data
from src.preprocessing import clean_air_quality_dataframe
from src.predict import generate_forecast, is_model_trained
from app.components.navbar import render_global_navbar
from app.components.design_system import (
    render_section_header,
    render_metric_tile,
    render_callout,
    render_badge,
    safe_markdown,
    ICONS
)
from app.components.charts import (
    apply_chart_theme,
    create_hourly_diurnal_chart,
    create_weekly_pattern_chart,
    create_daily_timeline_chart,
    create_correlation_heatmap
)

st.set_page_config(
    page_title="Trends & Analytics — AirGuard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto"
)

# Global Navbar
selected_city = render_global_navbar("Trends")

# Data Retrieval with automatic backfill if sparse
df_hist = fetch_historical_records(city=selected_city)
if df_hist.empty or len(df_hist) < 24:
    with st.spinner(f"Ingesting historical telemetry archive for {selected_city} from Open-Meteo..."):
        _, df_hist = fetch_and_store_city_data(selected_city, past_days=30)

if df_hist.empty:
    render_callout(
        title="No Telemetry Records Available",
        message=f"No atmospheric observations could be retrieved for '{selected_city}'. Please select another city from the navigation switcher.",
        variant="alert",
        icon="alert"
    )
    st.stop()

# Clean and sort historical dataframe
df_hist = clean_air_quality_dataframe(df_hist)
df_hist["timestamp"] = pd.to_datetime(df_hist["timestamp"], format="mixed")
df_hist.sort_values("timestamp", inplace=True)

min_date = df_hist["timestamp"].min().date()
max_date = df_hist["timestamp"].max().date()

# Header & Toolbar
render_section_header(
    title=f"Atmospheric Trends & Patterns — {selected_city}",
    subtitle="Diurnal cycles, 7-day longitudinal patterns, pollutant-weather correlations, and timeline safety zones.",
    badge="TIME-SERIES ARCHIVE"
)

ctrl_col1, ctrl_col2 = st.columns([2, 1])
with ctrl_col1:
    default_start = max(min_date, max_date - timedelta(days=14))
    date_range = st.date_input(
        "Observation Time Window",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filter historical observations by date"
    )
with ctrl_col2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("📡 Live Tracking", use_container_width=True):
            st.switch_page("pages/2_Live_Tracking.py")
    with b2:
        if st.button("🛡️ Outdoor Plan", use_container_width=True):
            st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")

# Filter data
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
    mask = (df_hist["timestamp"].dt.date >= start_d) & (df_hist["timestamp"].dt.date <= end_d)
    df_filtered = df_hist[mask].copy()
else:
    df_filtered = df_hist.copy()

if df_filtered.empty:
    df_filtered = df_hist.copy()

# Summary Metrics Bar
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)

mean_pm = df_filtered["pm2_5"].mean() if "pm2_5" in df_filtered else 0.0
peak_pm = df_filtered["pm2_5"].max() if "pm2_5" in df_filtered else 0.0
clean_hrs = len(df_filtered[df_filtered["pm2_5"] <= 35.4]) if "pm2_5" in df_filtered else 0
clean_pct = (clean_hrs / len(df_filtered) * 100) if len(df_filtered) > 0 else 0

with m1:
    render_metric_tile(label="Mean PM₂.₅", value=f"{mean_pm:.1f}", unit="µg/m³", subtext="Period average", icon="pulse")
with m2:
    render_metric_tile(label="Peak PM₂.₅", value=f"{peak_pm:.1f}", unit="µg/m³", subtext="Highest observed spike", icon="alert")
with m3:
    render_metric_tile(label="Total Observations", value=f"{len(df_filtered):,}", unit="hours", subtext="Valid hourly readings", icon="gauge")
with m4:
    render_metric_tile(label="Safe Air Ratio", value=f"{clean_pct:.1f}", unit="%", subtext="Readings ≤ 35.4 µg/m³", icon="check")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ----------------- CHART 1: 24-HOUR TREND & FORECAST WITH SAFE/UNSAFE PERIODS -----------------
render_section_header(
    title="24-Hour Horizon: Historical Trend & Predictive Forecast",
    subtitle="Continuously highlighted timeline showing safe outdoor zones (green) and caution/avoid periods (amber/red).",
    badge="SAFETY TIMELINE"
)

# Build unified 24h past + 24h forecast curve
profile = get_user_profile()
user_threshold = float(profile.get("aqi_alert_threshold", 55.0))

last_24h = df_hist.tail(24).copy()
fc_df = None
if is_model_trained():
    try:
        fc_df, _ = generate_forecast(selected_city, horizon_hours=24)
    except Exception:
        pass

fig_timeline = go.Figure()

# Historical past 24h trace
if not last_24h.empty:
    fig_timeline.add_trace(go.Scatter(
        x=last_24h["timestamp"],
        y=last_24h["pm2_5"],
        mode="lines+markers",
        name="Past 24h Observed",
        line=dict(color="#A3A3A3", width=2.5),
        marker=dict(size=4, color="#FFFFFF"),
        hovertemplate="Observed: <b>%{y:.1f} µg/m³</b><extra></extra>"
    ))

# Forecast next 24h trace
if fc_df is not None and not fc_df.empty:
    fig_timeline.add_trace(go.Scatter(
        x=fc_df["target_time"],
        y=fc_df["predicted_pm2_5"],
        mode="lines+markers",
        name="Next 24h ML Forecast",
        line=dict(color="#D71921", width=3, dash="solid"),
        marker=dict(size=5, color="#D71921"),
        hovertemplate="Forecast: <b>%{y:.1f} µg/m³</b><extra></extra>"
    ))
    # Confidence ribbon
    fig_timeline.add_trace(go.Scatter(
        x=fc_df["target_time"],
        y=fc_df["upper_ci"],
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip"
    ))
    fig_timeline.add_trace(go.Scatter(
        x=fc_df["target_time"],
        y=fc_df["lower_ci"],
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(215, 25, 33, 0.12)",
        name="90% Confidence Interval",
        hovertemplate="Lower 90% CI: %{y:.1f} µg/m³<extra></extra>"
    ))

# Shaded Safe vs Caution vs Unsafe zones
fig_timeline.add_hrect(
    y0=0, y1=35.4,
    fillcolor="rgba(34, 197, 94, 0.08)", line_width=0,
    annotation_text="SAFE ZONE (≤ 35.4 µg/m³)", annotation_position="top left",
    annotation_font=dict(color="#22C55E", size=10, family="Space Mono")
)
fig_timeline.add_hrect(
    y0=35.4, y1=55.4,
    fillcolor="rgba(234, 179, 8, 0.08)", line_width=0,
    annotation_text="CAUTION ZONE (35.4–55.4 µg/m³)", annotation_position="top left",
    annotation_font=dict(color="#EAB308", size=10, family="Space Mono")
)
fig_timeline.add_hrect(
    y0=55.4, y1=max(250.0, peak_pm * 1.1),
    fillcolor="rgba(215, 25, 33, 0.08)", line_width=0,
    annotation_text="UNHEALTHY / AVOID ZONE (> 55.4 µg/m³)", annotation_position="top left",
    annotation_font=dict(color="#D71921", size=10, family="Space Mono")
)

# Personal Threshold line
fig_timeline.add_hline(
    y=user_threshold, line_dash="dash", line_color="#FFFFFF", opacity=0.85,
    annotation_text=f"Your Threshold ({user_threshold:.0f} µg/m³)", annotation_position="bottom right",
    annotation_font=dict(color="#FFFFFF", size=10, family="Space Mono")
)

fig_timeline.update_layout(
    title=f"<b>{selected_city} — 24-Hour Observation & Predictive Projection Timeline</b>",
    xaxis_title="Time",
    yaxis_title="PM₂.₅ (µg/m³)",
    hovermode="x unified",
    margin=dict(l=40, r=40, t=55, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1)
)
apply_chart_theme(fig_timeline)
st.plotly_chart(fig_timeline, use_container_width=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ----------------- CHART 2 & 3: HOURLY DIURNAL & 7-DAY LONGITUDINAL PATTERN -----------------
c_left, c_right = st.columns(2)

with c_left:
    render_section_header(
        title="Hourly Diurnal Pattern (24h Rhythms)",
        subtitle="Median hourly concentrations showing morning and evening traffic/stagnation peaks.",
        badge="DIURNAL CURVE"
    )
    fig_diurnal = create_hourly_diurnal_chart(df_filtered)
    st.plotly_chart(fig_diurnal, use_container_width=True)

with c_right:
    render_section_header(
        title="Weekly Human Activity Trend (Day of Week)",
        subtitle="Anthropogenic workday vs weekend particulate variations.",
        badge="WEEKLY CYCLE"
    )
    fig_weekly = create_weekly_pattern_chart(df_filtered)
    st.plotly_chart(fig_weekly, use_container_width=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ----------------- CHART 4 & 5: DAILY TIMELINE & CORRELATION HEATMAP -----------------
render_section_header(
    title="Daily Mean Particulate Footprint & Atmospheric Cross-Correlations",
    subtitle="Long-term exposure tracking alongside correlation coefficients between pollutants and weather parameters.",
    badge="ANALYTICS"
)

t_col1, t_col2 = st.columns([1.4, 1.6])

with t_col1:
    fig_daily = create_daily_timeline_chart(df_filtered)
    st.plotly_chart(fig_daily, use_container_width=True)

with t_col2:
    fig_corr = create_correlation_heatmap(df_filtered)
    st.plotly_chart(fig_corr, use_container_width=True)
