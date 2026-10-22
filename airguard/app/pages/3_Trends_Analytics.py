"""
Trends & Historical Analytics Page for AirGuard.
Displays multi-scale historical atmospheric trends: hourly diurnal rhythms,
weekly anthropogenic cycles, continuous daily timelines, correlation matrices,
and high-pollution episode tracking.
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np

APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import fetch_historical_records
from src.data_collection import fetch_and_store_city_data
from src.preprocessing import clean_air_quality_dataframe
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

# Global Navbar with active city synchronization
selected_city = render_global_navbar("Trends & Analytics")

# Data Retrieval from SQLite with automatic API backfill
df_hist = fetch_historical_records(city=selected_city)
if df_hist.empty or len(df_hist) < 24:
    with st.spinner(f"Ingesting historical telemetry archive for {selected_city} from Open-Meteo..."):
        _, df_hist = fetch_and_store_city_data(selected_city, past_days=45)

if df_hist.empty:
    render_callout(
        title="No Telemetry Records Available",
        message=f"No atmospheric observations could be retrieved for '{selected_city}'. Please verify internet connectivity or select another monitored city from the header.",
        variant="alert",
        icon="alert"
    )
    st.stop()

# Clean and parse timestamps
df_hist = clean_air_quality_dataframe(df_hist)
df_hist["timestamp"] = pd.to_datetime(df_hist["timestamp"], format="mixed")
df_hist.sort_values("timestamp", inplace=True)

min_date = df_hist["timestamp"].min().date()
max_date = df_hist["timestamp"].max().date()

# Section Header
render_section_header(
    title="Atmospheric Trends & Historical Longitudinal Analytics",
    subtitle=f"Multi-scale empirical analysis for {selected_city} across diurnal hours, weekly human activity cycles, and atmospheric cross-correlation matrices.",
    badge="EMPIRICAL TIME-SERIES ARCHIVE"
)

# Controls & Filter Toolbar
ctrl_col1, ctrl_col2 = st.columns([1.8, 2.2])

with ctrl_col1:
    default_start = max(min_date, max_date - timedelta(days=30))
    date_range = st.date_input(
        "Observation Time Window",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filter historical observations by start and end date"
    )

with ctrl_col2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    with btn_col1:
        if st.button("⚡ Live Telemetry", use_container_width=True, help="Inspect current real-time ground readings"):
            st.switch_page("pages/1_Live_Air_Quality.py")
    with btn_col2:
        if st.button("📈 Forecast Model", use_container_width=True, help="View predictive trajectories"):
            st.switch_page("pages/2_Forecast.py")
    with btn_col3:
        if st.button("🏙️ Compare Cities", use_container_width=True, help="Benchmark against regional hubs"):
            st.switch_page("pages/4_City_Comparison.py")

# Apply Date Filter
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
    mask = (df_hist["timestamp"].dt.date >= start_d) & (df_hist["timestamp"].dt.date <= end_d)
    df_filtered = df_hist.loc[mask].copy()
else:
    df_filtered = df_hist.copy()

if df_filtered.empty:
    st.warning("No records found within the selected date window. Resetting to full history.")
    df_filtered = df_hist.copy()

# High-Contrast Key Performance Indicator Strip
avg_pm25 = float(df_filtered["pm2_5"].mean())
max_row = df_filtered.sort_values("pm2_5", ascending=False).iloc[0]
max_pm25 = float(max_row["pm2_5"])
max_time_str = max_row["timestamp"].strftime("%b %d, %H:%M")

unhealthy_hours = int((df_filtered["pm2_5"] >= 55.4).sum())
pct_unhealthy = (unhealthy_hours / len(df_filtered)) * 100.0

compliant_hours = int((df_filtered["pm2_5"] < 35.4).sum())
pct_compliant = (compliant_hours / len(df_filtered)) * 100.0

mcol1, mcol2, mcol3, mcol4 = st.columns(4)

with mcol1:
    render_metric_tile(
        label="Historical Mean PM₂.₅",
        value=round(avg_pm25, 1),
        unit="µg/m³",
        subtext=f"{len(df_filtered):,} hourly samples analyzed",
        icon="pulse"
    )

with mcol2:
    render_metric_tile(
        label="Peak Historical Spike",
        value=round(max_pm25, 1),
        unit="µg/m³",
        subtext=f"Recorded on {max_time_str}",
        icon="alert"
    )

with mcol3:
    render_metric_tile(
        label="Unhealthy Episodes (≥55.4)",
        value=unhealthy_hours,
        unit="hrs",
        subtext=f"{pct_unhealthy:.1f}% of monitored timeline",
        delta=f"{pct_unhealthy:.1f}% Unsafe",
        delta_positive=(pct_unhealthy <= 10.0),
        icon="chart"
    )

with mcol4:
    render_metric_tile(
        label="Clean Air Compliance (<35.4)",
        value=round(pct_compliant, 1),
        unit="%",
        subtext=f"{compliant_hours:,} hours in Good/Moderate tier",
        delta=f"{pct_compliant:.1f}% Clean",
        delta_positive=(pct_compliant >= 60.0),
        icon="check"
    )

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# Deep-Dive Analytics Navigation Tabs
tab_diurnal, tab_timeline, tab_correlations = st.tabs([
    "🕒 Diurnal & Weekly Patterns",
    "📅 Daily Aggregated Footprint",
    "🔬 Atmospheric Cross-Correlations"
])

# ----------------- TAB 1: DIURNAL & WEEKLY PATTERNS -----------------
with tab_diurnal:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(create_hourly_diurnal_chart(df_filtered), use_container_width=True)
    with c2:
        st.plotly_chart(create_weekly_pattern_chart(df_filtered), use_container_width=True)

    # Diagnostic Insight Callout
    df_filtered["hour"] = df_filtered["timestamp"].dt.hour
    hourly_means = df_filtered.groupby("hour")["pm2_5"].mean()
    peak_hr = hourly_means.idxmax()
    low_hr = hourly_means.idxmin()

    insight_summary = (
        f"In **{selected_city}**, particulate pollution demonstrates a pronounced diurnal cycle. "
        f"Maximum concentrations typically aggregate around **{peak_hr:02d}:00 hours** ({hourly_means.max():.1f} µg/m³) "
        f"driven by morning rush emissions trapped beneath the compressed nocturnal boundary layer. "
        f"The cleanest ambient conditions emerge around **{low_hr:02d}:00 hours** ({hourly_means.min():.1f} µg/m³) "
        f"when intense solar radiation drives strong convective mixing and atmospheric vertical dispersion."
    )

    render_callout(
        title="Diurnal Boundary Layer Dynamics Insight",
        message=insight_summary,
        variant="info",
        icon="check"
    )

# ----------------- TAB 2: DAILY TIMELINE & HIGH SMOG EPISODES -----------------
with tab_timeline:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.plotly_chart(create_daily_timeline_chart(df_filtered), use_container_width=True)

    # Exceedance Episodes Breakdown Table
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    daily_summary = df_filtered.set_index("timestamp").resample("D")["pm2_5"].agg(
        mean="mean",
        max="max",
        min="min"
    ).reset_index()
    daily_summary = daily_summary.dropna(subset=["mean"])

    severe_days = daily_summary[daily_summary["mean"] >= 35.4].copy()
    severe_days["date_str"] = severe_days["timestamp"].dt.strftime("%Y-%m-%d")
    severe_days["mean"] = severe_days["mean"].round(1)
    severe_days["max"] = severe_days["max"].round(1)
    severe_days["status"] = severe_days["mean"].apply(
        lambda x: "🚨 Unhealthy" if x >= 55.4 else ("⚠️ Unhealthy for Sensitive Groups" if x >= 35.4 else "✅ Moderate")
    )
    severe_days.sort_values("mean", ascending=False, inplace=True)

    with st.expander(f"⚠️ Inspect Elevated Smog Days ({len(severe_days)} Days Exceeding Moderate Limit)", expanded=False):
        if not severe_days.empty:
            table_display = severe_days[["date_str", "mean", "max", "status"]].copy()
            table_display.rename(columns={
                "date_str": "Calendar Date",
                "mean": "Daily Mean PM2.5 (µg/m³)",
                "max": "Peak Hour PM2.5 (µg/m³)",
                "status": "EPA Health Tier"
            }, inplace=True)
            st.dataframe(table_display, use_container_width=True, hide_index=True)
        else:
            st.info("No elevated smog days recorded in the selected observation window.")

# ----------------- TAB 3: ATMOSPHERIC CORRELATIONS -----------------
with tab_correlations:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    corr_col1, corr_col2 = st.columns([1.6, 1.0])

    with corr_col1:
        st.plotly_chart(create_correlation_heatmap(df_filtered), use_container_width=True)

    with corr_col2:
        safe_markdown(
            """
            <div class="card" style="padding: var(--space-4); height: 100%;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-3);">
                    <span style="font-size: var(--text-xs); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--color-slate-400);">Atmospheric Dynamics</span>
                    <span class="badge badge-info">PHYSICAL COUPLING</span>
                </div>
                <div style="font-size: var(--text-sm); color: var(--color-slate-200); line-height: 1.6;">
                    <div style="margin-bottom: var(--space-3);">
                        <strong style="color: var(--color-sky-400);">💨 Wind Speed (Ventilation):</strong><br>
                        Strong negative correlation with PM2.5. Sustained horizontal surface winds accelerate advective transport and disperse stagnant particulate matter.
                    </div>
                    <div style="margin-bottom: var(--space-3);">
                        <strong style="color: var(--color-sky-400);">💧 Relative Humidity (Trapping):</strong><br>
                        Positive correlation with particulate density. Elevated moisture promotes hygroscopic growth of sulfate/nitrate aerosols and often accompanies thermal inversion.
                    </div>
                    <div>
                        <strong style="color: var(--color-sky-400);">🚗 Combustion Markers (NO₂ & CO):</strong><br>
                        High co-linearity with PM2.5 indicates primary anthropogenic fossil-fuel emissions, such as vehicular combustion and biomass burning.
                    </div>
                </div>
            </div>
            """
        )

# CSV Export Section
st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
exp_col1, exp_col2 = st.columns([3, 1])
with exp_col2:
    csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Export Time-Series Dataset ({len(df_filtered):,} Rows)",
        data=csv_bytes,
        file_name=f"airguard_{selected_city.lower()}_historical_telemetry.csv",
        mime="text/csv",
        use_container_width=True
    )
