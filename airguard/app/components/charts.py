"""
Interactive Plotly Visualizations for AirGuard.
Features Modern Environmental Tech dark styling, JetBrains Mono tooltips,
and zero layout shift.
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


def apply_chart_theme(fig: go.Figure) -> go.Figure:
    """
    Applies unified Plus Jakarta Sans and JetBrains Mono typography, clean white surface,
    hairline warm grid dividers (#EBE6DF), and refined telemetry styling across all visualizations.
    """
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Plus Jakarta Sans, -apple-system, sans-serif", color="#1F344C"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        hoverlabel=dict(
            bgcolor="#1F344C",
            bordercolor="#EBE6DF",
            font=dict(family="JetBrains Mono, monospace", size=12, color="#FFFFFF")
        )
    )
    fig.update_xaxes(
        gridcolor="#EBE6DF",
        zerolinecolor="#CBD5E1",
        showline=True,
        linecolor="#EBE6DF",
        tickfont=dict(family="JetBrains Mono, monospace", color="#5A6E85")
    )
    fig.update_yaxes(
        gridcolor="#EBE6DF",
        zerolinecolor="#CBD5E1",
        showline=True,
        linecolor="#EBE6DF",
        tickfont=dict(family="JetBrains Mono, monospace", color="#5A6E85")
    )
    return fig


def create_forecast_chart(
    forecast_df: pd.DataFrame,
    current_pm25: Optional[float] = None,
    city: str = "",
    threshold: Optional[float] = None
) -> go.Figure:
    """
    Renders 24h & 72h forecast trajectory with shaded 90% confidence ribbon,
    EPA threshold guidelines, and optional user alert threshold.
    """
    fig = go.Figure()

    if forecast_df.empty:
        fig.add_annotation(text="No forecast data available", showarrow=False, font=dict(color="#94A3B8"))
        return apply_chart_theme(fig)

    # 1. Uncertainty Band (Upper Bound)
    fig.add_trace(go.Scatter(
        x=forecast_df["target_time"],
        y=forecast_df["upper_ci"],
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        name="Upper 90% CI",
        hoverinfo="skip"
    ))

    # 2. Uncertainty Band (Lower Bound with Fill)
    fig.add_trace(go.Scatter(
        x=forecast_df["target_time"],
        y=forecast_df["lower_ci"],
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(56, 189, 248, 0.14)",
        name="90% Confidence Interval",
        hovertemplate="Lower 90% CI: %{y:.1f} µg/m³<extra></extra>"
    ))

    # 3. Forecast Point Estimate Line
    fig.add_trace(go.Scatter(
        x=forecast_df["target_time"],
        y=forecast_df["predicted_pm2_5"],
        mode="lines+markers",
        name="Projected PM2.5",
        line=dict(color="#38BDF8", width=3.5),
        marker=dict(size=5, color="#0284C7", symbol="circle"),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Projected PM2.5: <b>%{y:.1f} µg/m³</b><br>"
            "Lead Horizon: +%{customdata[0]}h<br>"
            "Category: %{customdata[1]}<extra></extra>"
        ),
        customdata=list(zip(forecast_df["horizon_hours"], forecast_df["predicted_category"]))
    ))

    # Threshold horizontal reference lines
    if threshold and threshold > 0:
        fig.add_hline(
            y=threshold, line_dash="dash", line_color="#FFFFFF", opacity=0.85,
            annotation_text=f"Your Alert Threshold ({threshold:.0f} µg/m³)", annotation_position="bottom right",
            annotation_font=dict(color="#FFFFFF", size=10, family="Plus Jakarta Sans")
        )
    fig.add_hline(
        y=35.4, line_dash="dot", line_color="#F59E0B", opacity=0.75,
        annotation_text="Moderate Limit (35.4 µg/m³)", annotation_position="top left",
        annotation_font=dict(color="#F59E0B", size=10, family="Plus Jakarta Sans")
    )
    fig.add_hline(
        y=55.4, line_dash="dash", line_color="#EF4444", opacity=0.85,
        annotation_text="Unhealthy Threshold (55.4 µg/m³)", annotation_position="top left",
        annotation_font=dict(color="#EF4444", size=10, family="Plus Jakarta Sans")
    )

    fig.update_layout(
        title=f"<b>{city} — PM2.5 Predictive Multi-Step Trajectory</b>",
        xaxis_title="Forecast Timeline",
        yaxis_title="PM2.5 (µg/m³)",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=65, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
    )

    return apply_chart_theme(fig)


def create_hourly_diurnal_chart(df: pd.DataFrame) -> go.Figure:
    """
    Shows diurnal rhythm (0 to 23 hours) with median line and IQR shading.
    """
    fig = go.Figure()

    if df.empty or "pm2_5" not in df.columns:
        return apply_chart_theme(fig)

    data = df.copy()
    data["hour"] = pd.to_datetime(data["timestamp"], format="mixed").dt.hour

    hourly_stats = data.groupby("hour")["pm2_5"].agg(
        median="median",
        q25=lambda x: x.quantile(0.25),
        q75=lambda x: x.quantile(0.75)
    ).reset_index()

    fig.add_trace(go.Scatter(
        x=hourly_stats["hour"],
        y=hourly_stats["q75"],
        mode="lines",
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=hourly_stats["hour"],
        y=hourly_stats["q25"],
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(168, 85, 247, 0.16)",
        name="Interquartile Range (25-75%)"
    ))

    fig.add_trace(go.Scatter(
        x=hourly_stats["hour"],
        y=hourly_stats["median"],
        mode="lines+markers",
        name="Median PM2.5",
        line=dict(color="#A855F7", width=3),
        marker=dict(size=6, color="#C084FC")
    ))

    fig.update_layout(
        title="<b>Diurnal Pollution Curve (Hourly Rhythm)</b>",
        xaxis=dict(
            title="Hour of Day (24h)",
            tickmode="array",
            tickvals=[0, 4, 8, 12, 16, 20, 23],
            ticktext=["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "23:00"],
            tickangle=0
        ),
        yaxis_title="PM2.5 (µg/m³)",
        margin=dict(l=40, r=40, t=50, b=40)
    )

    return apply_chart_theme(fig)


def create_weekly_pattern_chart(df: pd.DataFrame) -> go.Figure:
    """
    Renders bar chart of mean pollution across days of the week.
    """
    fig = go.Figure()
    if df.empty or "pm2_5" not in df.columns:
        return apply_chart_theme(fig)

    data = df.copy()
    data["day_num"] = pd.to_datetime(data["timestamp"], format="mixed").dt.dayofweek
    days_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
    data["day_name"] = data["day_num"].map(days_map)

    weekly_avg = data.groupby(["day_num", "day_name"])["pm2_5"].mean().reset_index()
    weekly_avg.sort_values("day_num", inplace=True)

    fig = px.bar(
        weekly_avg,
        x="day_name",
        y="pm2_5",
        text_auto=".1f",
        title="<b>Weekly Pollution Trend (Average by Day)</b>",
        labels={"day_name": "Day of Week", "pm2_5": "Mean PM2.5 (µg/m³)"}
    )
    fig.update_traces(
        marker_color="#818CF8",
        marker_line=dict(color="#A5B4FC", width=1.5),
        textfont=dict(family="JetBrains Mono, monospace", size=12, color="#F8FAFC"),
        textposition="outside"
    )
    fig.update_layout(
        margin=dict(l=40, r=40, t=50, b=40),
        yaxis=dict(range=[0, max(weekly_avg["pm2_5"].max() * 1.18, 20.0)])
    )
    return apply_chart_theme(fig)


def create_daily_timeline_chart(df: pd.DataFrame) -> go.Figure:
    """
    Continuous daily aggregated PM2.5 timeline with EPA threshold reference lines.
    """
    fig = go.Figure()
    if df.empty or "pm2_5" not in df.columns:
        return apply_chart_theme(fig)

    data = df.copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], format="mixed")
    daily_stats = data.set_index("timestamp").resample("D")["pm2_5"].agg(["mean", "min", "max"]).reset_index()
    daily_stats = daily_stats.dropna(subset=["mean"])

    fig.add_trace(go.Bar(
        x=daily_stats["timestamp"],
        y=daily_stats["mean"],
        name="Daily Average PM2.5",
        marker=dict(
            color=daily_stats["mean"],
            colorscale=[[0, "#10B981"], [0.35, "#F59E0B"], [0.55, "#EF4444"], [1.0, "#7F1D1D"]],
            cmin=10,
            cmax=80,
            line=dict(color="rgba(255, 255, 255, 0.1)", width=1)
        ),
        hovertemplate=(
            "<b>%{x|%b %d, %Y}</b><br>"
            "Daily Mean PM2.5: <b>%{y:.1f} µg/m³</b><extra></extra>"
        )
    ))

    # Reference Thresholds
    fig.add_hline(
        y=35.4, line_dash="dot", line_color="#F59E0B", opacity=0.85,
        annotation_text="Moderate Limit (35.4 µg/m³)", annotation_position="top left",
        annotation_font=dict(color="#F59E0B", size=10, family="Plus Jakarta Sans")
    )
    fig.add_hline(
        y=55.4, line_dash="dash", line_color="#EF4444", opacity=0.85,
        annotation_text="Unhealthy Threshold (55.4 µg/m³)", annotation_position="top left",
        annotation_font=dict(color="#EF4444", size=10, family="Plus Jakarta Sans")
    )

    fig.update_layout(
        title="<b>Daily Mean Particulate Footprint vs Safety Standards</b>",
        xaxis_title="Observation Timeline",
        yaxis_title="PM2.5 (µg/m³)",
        hovermode="x",
        margin=dict(l=40, r=40, t=50, b=40)
    )

    return apply_chart_theme(fig)


def create_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Interactive cross-correlation matrix between pollutants and weather parameters.
    """
    fig = go.Figure()
    target_cols = [
        "pm2_5", "pm10", "no2", "so2", "co", "o3",
        "temperature", "humidity", "wind_speed", "pressure"
    ]
    avail_cols = [c for c in target_cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]

    if len(avail_cols) < 2:
        return apply_chart_theme(fig)

    corr = df[avail_cols].corr()

    labels_map = {
        "pm2_5": "PM2.5", "pm10": "PM10", "no2": "NO2", "so2": "SO2", "co": "CO", "o3": "Ozone",
        "temperature": "Temp (°C)", "humidity": "Humidity (%)",
        "wind_speed": "Wind (km/h)", "pressure": "Pressure"
    }
    x_labels = [labels_map.get(c, c) for c in corr.columns]
    y_labels = [labels_map.get(c, c) for c in corr.index]

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=x_labels,
        y=y_labels,
        colorscale="RdBu_r",
        zmin=-1,
        zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        hoverongaps=False
    ))

    fig.update_layout(
        title="<b>Atmospheric Cross-Correlation Matrix</b>",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return apply_chart_theme(fig)


def create_feature_importance_chart(df_imp: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart for model explainability.
    """
    fig = go.Figure()
    if df_imp.empty:
        return apply_chart_theme(fig)

    df_sorted = df_imp.sort_values("importance", ascending=True)

    fig = go.Figure(go.Bar(
        x=df_sorted["importance"],
        y=df_sorted["display_name"],
        orientation="h",
        marker=dict(
            color=df_sorted["importance"],
            colorscale="Viridis",
            line=dict(color="rgba(255, 255, 255, 0.15)", width=1)
        ),
        hovertemplate="Feature: <b>%{y}</b><br>Influence: <b>%{x:.2f}%</b><extra></extra>"
    ))

    fig.update_layout(
        title="<b>Global Feature Importance (% Weight)</b>",
        xaxis_title="Relative Contribution (%)",
        yaxis_title="",
        margin=dict(l=160, r=40, t=50, b=40)
    )
    return apply_chart_theme(fig)


def create_city_comparison_bars(
    comparison_records: List[Dict[str, Any]] | pd.DataFrame,
    metric: str = "current_aqi",
    title: str = "City Comparison"
) -> go.Figure:
    """
    Bar chart comparing air quality across multiple selected cities.
    """
    fig = go.Figure()
    if comparison_records is None or (isinstance(comparison_records, list) and len(comparison_records) == 0):
        return apply_chart_theme(fig)

    df_comp = comparison_records if isinstance(comparison_records, pd.DataFrame) else pd.DataFrame(comparison_records)
    if df_comp.empty or metric not in df_comp.columns:
        return apply_chart_theme(fig)

    labels_map = {
        "current_aqi": "Current AQI",
        "current_pm2_5": "PM₂.₅ (µg/m³)",
        "current_pm10": "PM₁₀ (µg/m³)",
        "current_no2": "NO₂ (µg/m³)",
        "current_o3": "O₃ (µg/m³)",
        "forecast_24h_pm2_5": "Forecast PM₂.₅ (µg/m³)",
        "historical_mean_pm2_5": "Historical PM₂.₅ (µg/m³)"
    }
    metric_label = labels_map.get(metric, metric.replace("_", " ").title())
    fmt = True if metric == "current_aqi" else ".1f"
    x_col = "location_label" if "location_label" in df_comp.columns else "city"

    fig = px.bar(
        df_comp,
        x=x_col,
        y=metric,
        color=metric,
        color_continuous_scale="RdYlGn_r" if metric == "current_aqi" else "Temps",
        title=f"<b>{title}</b>",
        labels={x_col: "Location", metric: metric_label},
        text_auto=fmt
    )

    fig.update_layout(
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return apply_chart_theme(fig)


def create_city_grouped_benchmark_chart(df_comp: pd.DataFrame) -> go.Figure:
    """
    Grouped bar chart comparing Current PM2.5, +24h ML Forecast, and Historical Average.
    """
    fig = go.Figure()
    if df_comp.empty:
        return apply_chart_theme(fig)

    x_col = "location_label" if "location_label" in df_comp.columns else "city"

    fig.add_trace(go.Bar(
        x=df_comp[x_col],
        y=df_comp["current_pm2_5"],
        name="Current PM₂.₅",
        marker_color="#38BDF8",
        hovertemplate="<b>%{x}</b><br>Current PM2.5: <b>%{y:.1f} µg/m³</b><extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=df_comp[x_col],
        y=df_comp["forecast_24h_pm2_5"],
        name="+24h Projected PM₂.₅",
        marker_color="#F59E0B",
        hovertemplate="<b>%{x}</b><br>+24h Projected: <b>%{y:.1f} µg/m³</b><extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=df_comp[x_col],
        y=df_comp["historical_mean_pm2_5"],
        name="Historical Mean PM₂.₅",
        marker_color="#A855F7",
        hovertemplate="<b>%{x}</b><br>Historical Mean: <b>%{y:.1f} µg/m³</b><extra></extra>"
    ))

    fig.update_layout(
        title="<b>Particulate Benchmarking across Regional Centers</b>",
        barmode="group",
        yaxis_title="PM2.5 (µg/m³)",
        xaxis_title="",
        hovermode="x",
        margin=dict(l=40, r=40, t=65, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
    )
    return apply_chart_theme(fig)

