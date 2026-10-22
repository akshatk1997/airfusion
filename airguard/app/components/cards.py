"""
Modern Environmental Tech UI Cards Component for AirGuard.
Features WCAG AAA high-contrast badges, dynamic progress scale bars,
and chemical formula typography.
"""

from __future__ import annotations

import streamlit as st
from typing import Optional, Dict, Any
from app.components.design_system import safe_markdown


def get_aqi_badge_style(aqi: int) -> Dict[str, str]:
    """
    Returns accessible high-contrast colors and text styles based on AQI value.
    Complies with WCAG AAA contrast guidelines.
    """
    if aqi <= 50:
        return {
            "bg": "rgba(16, 185, 129, 0.15)",
            "border": "#10B981",
            "text": "#34D399",
            "glow": "0 0 15px rgba(16, 185, 129, 0.3)",
            "gradient": "linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%)"
        }
    elif aqi <= 100:
        return {
            "bg": "rgba(245, 158, 11, 0.15)",
            "border": "#F59E0B",
            "text": "#FBBF24",
            "glow": "0 0 15px rgba(245, 158, 11, 0.3)",
            "gradient": "linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%)"
        }
    elif aqi <= 150:
        return {
            "bg": "rgba(249, 115, 22, 0.15)",
            "border": "#F97316",
            "text": "#FB923C",
            "glow": "0 0 15px rgba(249, 115, 22, 0.3)",
            "gradient": "linear-gradient(135deg, rgba(249, 115, 22, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%)"
        }
    elif aqi <= 200:
        return {
            "bg": "rgba(239, 68, 68, 0.15)",
            "border": "#EF4444",
            "text": "#F87171",
            "glow": "0 0 15px rgba(239, 68, 68, 0.35)",
            "gradient": "linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%)"
        }
    elif aqi <= 300:
        return {
            "bg": "rgba(168, 85, 247, 0.15)",
            "border": "#A855F7",
            "text": "#C084FC",
            "glow": "0 0 15px rgba(168, 85, 247, 0.35)",
            "gradient": "linear-gradient(135deg, rgba(168, 85, 247, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%)"
        }
    else:
        return {
            "bg": "rgba(136, 19, 55, 0.25)",
            "border": "#E11D48",
            "text": "#FB7185",
            "glow": "0 0 20px rgba(225, 29, 72, 0.4)",
            "gradient": "linear-gradient(135deg, rgba(136, 19, 55, 0.4) 0%, rgba(15, 23, 42, 0.95) 100%)"
        }


def render_aqi_hero_card(
    aqi: int,
    category: str,
    color: str,
    city: str,
    timestamp: str,
    pm25_val: float
) -> None:
    """
    Renders high-impact Hero AQI card with progress position bar,
    high-contrast pill, and mono typography.
    """
    theme = get_aqi_badge_style(aqi)
    # Calculate percentage along 0-500 scale capped at 100%
    pct = min(100.0, max(2.0, (aqi / 500.0) * 100.0))

    html = f"""
    <div style="
        background: {theme['gradient']};
        border: 1px solid {theme['border']};
        border-radius: 20px;
        padding: 26px 30px;
        margin-bottom: 24px;
        box-shadow: {theme['glow']}, 0 20px 40px -10px rgba(0, 0, 0, 0.6);
        position: relative;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 20px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <span style="
                        background: {theme['bg']};
                        border: 1px solid {theme['border']};
                        color: {theme['text']};
                        font-size: 0.85rem;
                        font-weight: 700;
                        padding: 5px 14px;
                        border-radius: 9999px;
                        letter-spacing: 0.04em;
                        text-transform: uppercase;
                        display: inline-flex;
                        align-items: center;
                        gap: 6px;
                    ">
                        ● {category}
                    </span>
                    <span style="font-size: 0.78rem; color: #94A3B8;">US EPA Standard</span>
                </div>
                <h1 style="margin: 0 0 6px 0; font-size: 2.3rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">
                    {city}
                </h1>
                <p style="margin: 0; font-size: 0.82rem; color: #94A3B8;">
                    Telemetry Last Verified: <span style="color: #E2E8F0; font-family: 'JetBrains Mono', monospace;">{timestamp}</span>
                </p>
            </div>
            
            <div style="text-align: right; min-width: 140px;">
                <div style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 4.2rem;
                    font-weight: 800;
                    line-height: 0.95;
                    color: {theme['text']};
                    letter-spacing: -0.04em;
                ">
                    {aqi}
                </div>
                <div style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px;">
                    AIR QUALITY INDEX
                </div>
                <div style="font-size: 0.82rem; color: #E2E8F0; font-family: 'JetBrains Mono', monospace; margin-top: 4px;">
                    PM₂.₅: <b>{pm25_val:.1f}</b> µg/m³
                </div>
            </div>
        </div>

        <!-- AQI Scale Bar -->
        <div style="margin-top: 24px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; color: #94A3B8; margin-bottom: 6px;">
                <span>0 GOOD</span>
                <span>50</span>
                <span>100 MODERATE</span>
                <span>150 SENSITIVE</span>
                <span>200 UNHEALTHY</span>
                <span>300 VERY UNHEALTHY</span>
                <span>500 HAZARDOUS</span>
            </div>
            <div style="
                height: 8px;
                background: rgba(255, 255, 255, 0.08);
                border-radius: 9999px;
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    width: {pct}%;
                    height: 100%;
                    background: linear-gradient(90deg, #10B981 0%, #F59E0B 30%, #EF4444 60%, #A855F7 85%, #881337 100%);
                    border-radius: 9999px;
                    transition: width 0.5s ease-in-out;
                "></div>
            </div>
        </div>
    </div>
    """
    safe_markdown(html)


def render_pollutant_metric_card(
    label: str,
    value: Optional[float],
    unit: str = "µg/m³",
    subtext: str = "",
    delta: Optional[str] = None
) -> None:
    """
    Renders standardized pollutant telemetry card with subscript formatting.
    """
    val_str = f"{value:.1f}" if (value is not None and value >= 0) else "--"
    delta_html = f"<span style='color: #34D399; font-size: 0.78rem; font-weight: 600; margin-left: 6px;'>{delta}</span>" if delta else ""

    html = f"""
    <div style="
        background: #111827;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 16px 18px;
        height: 100%;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    ">
        <div>
            <div style="color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                {label}
            </div>
            <div style="display: flex; align-items: baseline; gap: 4px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #F8FAFC; letter-spacing: -0.02em;">
                    {val_str}
                </span>
                <span style="color: #64748B; font-size: 0.8rem; font-weight: 500;">
                    {unit}
                </span>
                {delta_html}
            </div>
        </div>
        <div style="color: #64748B; font-size: 0.75rem; margin-top: 8px; border-top: 1px solid #1E293B; padding-top: 6px;">
            {subtext}
        </div>
    </div>
    """
    safe_markdown(html)


def render_weather_metric_card(
    label: str,
    value: Optional[float],
    unit: str,
    icon: str = "🌤️"
) -> None:
    """
    Renders meteorological telemetry card.
    """
    val_str = f"{value:.1f}" if value is not None else "--"
    html = f"""
    <div style="
        background: #111827;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
    ">
        <div style="
            font-size: 1.6rem;
            background: #0B0F17;
            border: 1px solid #1E293B;
            border-radius: 12px;
            width: 46px;
            height: 46px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        ">
            {icon}
        </div>
        <div>
            <div style="color: #94A3B8; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">
                {label}
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.35rem; font-weight: 700; color: #F8FAFC;">
                {val_str} <span style="font-size: 0.75rem; color: #64748B; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 400;">{unit}</span>
            </div>
        </div>
    </div>
    """
    safe_markdown(html)
