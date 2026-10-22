"""
Air Quality Forecasting Page for AirGuard.
Generates 24-hour and 72-hour multi-step forecasts with 90% confidence bands,
risk indicators, atmospheric drivers, and natural-language diagnostic explanations.
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st
import pandas as pd

APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.predict import generate_forecast, is_model_trained
from src.explainability import generate_natural_language_insight
from src.data_collection import fetch_current_air_quality, geocode_city
from app.components.navbar import render_global_navbar
from app.components.charts import create_forecast_chart
from app.components.design_system import (
    render_section_header,
    render_metric_tile,
    render_callout,
    render_badge,
    safe_markdown,
    ICONS
)

st.set_page_config(
    page_title="Predictive Forecasting — AirGuard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto"
)

# Global Navbar with active city synchronization
selected_city = render_global_navbar("Forecast")

# Model Availability Verification
if not is_model_trained():
    render_callout(
        title="Predictive Model Pipeline Offline",
        message="The machine learning forecasting engine requires trained model weights. Please navigate to the Model Insights workspace to initialize training on empirical telemetry.",
        variant="alert",
        icon="alert"
    )
    if st.button("🚀 Navigate to Model Insights & Training", key="btn_goto_train"):
        st.switch_page("pages/6_Model_Insights.py")
    st.stop()

# Header
render_section_header(
    title="Atmospheric Particulate Trajectory & Predictive Horizons",
    subtitle=f"Multi-step machine learning forecasting for {selected_city} incorporating atmospheric dispersion, diurnal boundary layer compression, and meteorological lag features.",
    badge="PREDICTIVE INTELLIGENCE ENGINE"
)

# Interactive Toolbar Controls
ctrl_col1, ctrl_col2 = st.columns([1.5, 2.5])

with ctrl_col1:
    horizon_choice = st.radio(
        "Forecast Horizon",
        options=[24, 72],
        format_func=lambda x: f"Next {x} Hours (+{x // 24} Day{'s' if x > 24 else ''})",
        horizontal=True,
        key="horizon_selector",
        label_visibility="collapsed"
    )

with ctrl_col2:
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    with btn_col1:
        if st.button("🔄 Refresh Run", use_container_width=True, help="Recompute trajectory with latest atmospheric telemetry"):
            st.cache_data.clear()
            st.rerun()
    with btn_col2:
        if st.button("⚡ Live Telemetry", use_container_width=True, help="Inspect real-time ground-station sensors"):
            st.switch_page("pages/1_Live_Air_Quality.py")
    with btn_col3:
        if st.button("🚨 Configure Alert", use_container_width=True, help="Set threshold alert notifications"):
            st.switch_page("pages/5_Alerts.py")

# Generate Forecast Trajectory
with st.spinner(f"Computing multi-step {horizon_choice}-hour predictive trajectory for {selected_city}..."):
    forecast_df, summary = generate_forecast(selected_city, horizon_hours=horizon_choice)

if forecast_df is None or "error" in summary:
    render_callout(
        title="Forecasting Engine Exception",
        message=f"Unable to generate predictive trajectory: {summary.get('error', 'Unknown telemetry pipeline error')}",
        variant="alert",
        icon="alert"
    )
    st.stop()

# Key Performance Indicators (Top Metric Strip)
current_val = float(summary.get("current_pm2_5", 0.0))
f24_val = float(summary.get("forecast_24h_pm2_5", current_val))
f72_val = summary.get("forecast_72h_pm2_5")
peak_row = forecast_df.sort_values("predicted_pm2_5", ascending=False).iloc[0]
min_row = forecast_df.sort_values("predicted_pm2_5", ascending=True).iloc[0]

kcol1, kcol2, kcol3, kcol4 = st.columns(4)

with kcol1:
    render_metric_tile(
        label="Current PM₂.₅ Baseline",
        value=current_val,
        unit="µg/m³",
        subtext=f"Current AQI: {summary.get('current_aqi', '--')} ({summary.get('current_category', 'Active')})",
        icon="pulse"
    )

with kcol2:
    delta_24 = f24_val - current_val
    render_metric_tile(
        label="+24h Projected PM₂.₅",
        value=f24_val,
        unit="µg/m³",
        delta=f"{delta_24:+.1f} µg/m³",
        delta_positive=(delta_24 <= 0),
        subtext=f"AQI: {summary.get('forecast_24h_aqi', '--')} • {summary.get('forecast_24h_category', 'Moderate')}",
        icon="chart"
    )

with kcol3:
    if f72_val is not None and horizon_choice >= 72:
        f72_val_flt = float(f72_val)
        delta_72 = f72_val_flt - current_val
        render_metric_tile(
            label="+72h Projected PM₂.₅",
            value=f72_val_flt,
            unit="µg/m³",
            delta=f"{delta_72:+.1f} µg/m³",
            delta_positive=(delta_72 <= 0),
            subtext=f"AQI: {summary.get('forecast_72h_aqi', '--')} • {summary.get('forecast_72h_category', 'Moderate')}",
            icon="gauge"
        )
    else:
        # Show horizon window average when in 24h view
        avg_val = float(forecast_df["predicted_pm2_5"].mean())
        delta_avg = avg_val - current_val
        render_metric_tile(
            label=f"{horizon_choice}h Window Mean",
            value=round(avg_val, 1),
            unit="µg/m³",
            delta=f"{delta_avg:+.1f} µg/m³",
            delta_positive=(delta_avg <= 0),
            subtext=f"Expected average over next {horizon_choice}h",
            icon="gauge"
        )

with kcol4:
    peak_val = float(peak_row["predicted_pm2_5"])
    render_metric_tile(
        label=f"Projected Smog Peak (+{peak_row['horizon_hours']}h)",
        value=peak_val,
        unit="µg/m³",
        delta=f"{peak_row['predicted_category']}",
        delta_positive=(peak_val < 35.4),
        subtext=f"Occurs at {peak_row['target_time'].split(' ')[1] if ' ' in str(peak_row['target_time']) else peak_row['target_time']}",
        icon="alert"
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# Diagnostic Synthesis & Model Lineage Grid
diag_col, meta_col = st.columns([1.6, 1.0])

with diag_col:
    loc_meta = geocode_city(selected_city)
    curr_wx = fetch_current_air_quality(loc_meta["latitude"], loc_meta["longitude"]) if loc_meta else {}
    insight_text = generate_natural_language_insight(
        city=selected_city,
        current_pm25=current_val,
        forecast_24h_pm25=f24_val,
        weather_info=curr_wx
    )
    render_callout(
        title="AI Environmental Diagnostic Synthesis",
        message=insight_text,
        variant="info",
        icon="check"
    )

with meta_col:
    champion_name = summary.get("best_model_name", "XGBoost Regressor")
    safe_markdown(
        f"""
        <div class="card" style="padding: var(--space-4); height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2);">
                <span style="font-size: var(--text-xs); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--color-slate-400);">Model Inference Telemetry</span>
                <span class="badge badge-good">ONLINE</span>
            </div>
            <div style="font-size: var(--text-sm); color: var(--color-slate-200); line-height: 1.6;">
                <div><strong>Champion Architecture:</strong> {champion_name}</div>
                <div><strong>Confidence Bounds:</strong> 90% Empirical Residual Interval</div>
                <div><strong>Atmospheric Signals:</strong> 18 Autoregressive & Rolling Lags</div>
                <div><strong>Temporal Resolution:</strong> 1-Hour Discrete Increments</div>
            </div>
            <div style="margin-top: var(--space-2); font-size: var(--text-xs); color: var(--color-slate-500); font-family: var(--font-mono);">
                Validated against Open-Meteo Ground Reanalysis
            </div>
        </div>
        """
    )

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Main Forecast Plotly Canvas with 90% Confidence Ribbon
fig = create_forecast_chart(forecast_df, current_pm25=current_val, city=selected_city)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "scrollZoom": False})

# Exposure Windows & Practical Timing Advisory
st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
adv_col1, adv_col2 = st.columns(2)

with adv_col1:
    cleanest_time = min_row['target_time']
    safe_markdown(
        f"""
        <div class="card" style="border-left: 4px solid var(--color-good); padding: var(--space-4);">
            <div style="display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2);">
                <div style="width: 24px; height: 24px; color: var(--color-good);">{ICONS['check']}</div>
                <div style="font-weight: 700; font-size: var(--text-base); color: var(--color-slate-100);">Optimal Low-Exposure Window</div>
            </div>
            <div style="font-size: var(--text-sm); color: var(--color-slate-300); line-height: 1.5;">
                Particulate concentrations are projected to trough around <strong>{cleanest_time}</strong> at approximately <strong>{min_row['predicted_pm2_5']:.1f} µg/m³</strong> (AQI {min_row['predicted_aqi']}).
                This represents the most favorable window for ventilation and outdoor physical exercise.
            </div>
        </div>
        """
    )

with adv_col2:
    highest_time = peak_row['target_time']
    peak_is_severe = peak_row['predicted_pm2_5'] >= 55.4
    border_color = "var(--color-severe)" if peak_is_severe else "var(--color-moderate)"
    icon_svg = ICONS['alert'] if peak_is_severe else ICONS['gauge']

    safe_markdown(
        f"""
        <div class="card" style="border-left: 4px solid {border_color}; padding: var(--space-4);">
            <div style="display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2);">
                <div style="width: 24px; height: 24px; color: {border_color};">{icon_svg}</div>
                <div style="font-weight: 700; font-size: var(--text-base); color: var(--color-slate-100);">Peak Pollution Concentration</div>
            </div>
            <div style="font-size: var(--text-sm); color: var(--color-slate-300); line-height: 1.5;">
                Peak particulate accumulation is anticipated around <strong>{highest_time}</strong> reaching <strong>{peak_row['predicted_pm2_5']:.1f} µg/m³</strong> ({peak_row['predicted_category']}).
                Sensitive demographics and individuals with respiratory conditions should seal windows and minimize vigorous outdoor activity during this phase.
            </div>
        </div>
        """
    )

# Hourly Trajectory Table & Export
st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
with st.expander(f"📋 Inspect Continuous Hourly Forecast Schedule ({horizon_choice} Timesteps)", expanded=False):
    display_df = forecast_df[[
        "target_time", "horizon_hours", "predicted_pm2_5",
        "predicted_aqi", "predicted_category", "lower_ci", "upper_ci"
    ]].copy()
    display_df.rename(columns={
        "target_time": "Target Timestamp",
        "horizon_hours": "Lead (+h)",
        "predicted_pm2_5": "Projected PM2.5 (µg/m³)",
        "predicted_aqi": "Projected AQI",
        "predicted_category": "Health Tier",
        "lower_ci": "Lower 90% Bound",
        "upper_ci": "Upper 90% Bound"
    }, inplace=True)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# CSV Export Action Bar
csv_col1, csv_col2 = st.columns([3, 1])
with csv_col2:
    csv_data = forecast_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Export {horizon_choice}h Forecast (CSV)",
        data=csv_data,
        file_name=f"airguard_{selected_city.lower()}_{horizon_choice}h_forecast.csv",
        mime="text/csv",
        use_container_width=True
    )
