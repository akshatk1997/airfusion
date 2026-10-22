"""
Nothing OS Design System UI Cards Component for AirGuard.
Features authentic Ndot-57 / Space Grotesk typography, zero glow effects,
matte high-contrast surfaces, and industrial precision telemetry.
"""

from __future__ import annotations

import streamlit as st
from typing import Optional, Dict, Any
from app.components.design_system import safe_markdown


def get_aqi_badge_style(aqi: int) -> Dict[str, str]:
    """
    Returns accessible high-contrast Nothing OS styles based on AQI value.
    Zero glow, matte high-contrast status colors.
    """
    if aqi <= 50:
        return {
            "bg": "rgba(16, 185, 129, 0.12)",
            "border": "#10B981",
            "text": "#10B981",
            "dot": "#10B981"
        }
    elif aqi <= 100:
        return {
            "bg": "rgba(245, 158, 11, 0.12)",
            "border": "#F59E0B",
            "text": "#F59E0B",
            "dot": "#F59E0B"
        }
    elif aqi <= 150:
        return {
            "bg": "rgba(249, 115, 22, 0.12)",
            "border": "#F97316",
            "text": "#F97316",
            "dot": "#F97316"
        }
    elif aqi <= 200:
        return {
            "bg": "rgba(239, 68, 68, 0.12)",
            "border": "#EF4444",
            "text": "#EF4444",
            "dot": "#EF4444"
        }
    elif aqi <= 300:
        return {
            "bg": "rgba(168, 85, 247, 0.12)",
            "border": "#A855F7",
            "text": "#A855F7",
            "dot": "#A855F7"
        }
    else:
        return {
            "bg": "rgba(225, 29, 72, 0.14)",
            "border": "#E11D48",
            "text": "#E11D48",
            "dot": "#E11D48"
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
    Renders high-impact Nothing OS Hero AQI card with authentic Ndot-57 dot matrix numerals,
    matte dark slate container, clean pill badge, zero glow, and mechanical progress slider.
    """
    theme = get_aqi_badge_style(aqi)
    pct = min(100.0, max(2.0, (aqi / 500.0) * 100.0))

    html = f"""
    <div style="
        background: #121212;
        border: 1px solid #242424;
        border-radius: 16px;
        padding: 26px 30px;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        position: relative;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 20px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                    <span style="
                        background: {theme['bg']};
                        border: 1px solid {theme['border']};
                        color: {theme['text']};
                        font-family: var(--font-dot);
                        font-size: 0.76rem;
                        font-weight: 700;
                        padding: 4px 12px;
                        border-radius: 9999px;
                        letter-spacing: 0.08em;
                        text-transform: uppercase;
                        display: inline-flex;
                        align-items: center;
                        gap: 6px;
                    ">
                        ● {category}
                    </span>
                    <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #777777; text-transform: uppercase; letter-spacing: 0.04em;">US EPA Standard</span>
                </div>
                <h1 style="margin: 0 0 6px 0; font-family: var(--font-heading); font-size: 2.3rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em;">
                    {city}
                </h1>
                <p style="margin: 0; font-family: var(--font-mono); font-size: 0.8rem; color: #888888;">
                    Telemetry Verified: <span style="color: #CCCCCC;">{timestamp}</span>
                </p>
            </div>
            
            <div style="text-align: right; min-width: 140px;">
                <div style="
                    font-family: var(--font-dot);
                    font-size: 5.2rem;
                    font-weight: 700;
                    line-height: 0.9;
                    color: {theme['text']};
                    letter-spacing: -0.02em;
                ">
                    {aqi}
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.75rem; font-weight: 700; color: #777777; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px;">
                    AIR QUALITY INDEX
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.85rem; color: #AAAAAA; margin-top: 4px;">
                    PM₂.₅: <b style="color: #FFFFFF;">{pm25_val:.1f}</b> µg/m³
                </div>
            </div>
        </div>

        <!-- Nothing OS Minimalist Matte Scale Bar (Zero Glow) -->
        <div style="margin-top: 24px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.7rem; font-family: var(--font-mono); color: #777777; margin-bottom: 8px;">
                <span>0 Good</span>
                <span>50 Moderate</span>
                <span>100 Sensitive</span>
                <span>150 Unhealthy</span>
                <span>300+ Hazardous</span>
            </div>
            <div style="
                height: 6px;
                background: #202020;
                border-radius: 9999px;
                position: relative;
            ">
                <div style="
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, #10B981 0%, #F59E0B 30%, #EF4444 60%, #A855F7 85%, #E11D48 100%);
                    border-radius: 9999px;
                "></div>
                <div style="
                    position: absolute;
                    left: calc({pct}% - 6px);
                    top: -3px;
                    width: 12px;
                    height: 12px;
                    background: #FFFFFF;
                    border: 2px solid #000000;
                    border-radius: 50%;
                    transition: left 0.4s ease;
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
    Renders Nothing OS standardized pollutant telemetry card with matte surface,
    clean mono numbers, and zero glow effects.
    """
    val_str = f"{value:.1f}" if (value is not None and value >= 0) else "--"
    delta_html = f"<span style='color: #10B981; font-family: var(--font-mono); font-size: 0.75rem; font-weight: 600; margin-left: 6px;'>{delta}</span>" if delta else ""

    html = f"""
    <div class="ag-card ag-metric-card" style="
        background: #141414;
        border: 1px solid #242424;
        border-radius: 12px;
        padding: 16px 18px;
        height: 100%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: border-color 0.2s ease, transform 0.2s ease;
    ">
        <div>
            <div style="color: #888888; font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px;">
                {label}
            </div>
            <div style="display: flex; align-items: baseline; gap: 4px;">
                <span style="font-family: var(--font-mono); font-size: 1.8rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em;">
                    {val_str}
                </span>
                <span style="color: #666666; font-family: var(--font-sans); font-size: 0.8rem; font-weight: 500;">
                    {unit}
                </span>
                {delta_html}
            </div>
        </div>
        <div style="color: #666666; font-family: var(--font-mono); font-size: 0.72rem; margin-top: 8px; border-top: 1px solid #222222; padding-top: 6px;">
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
    Renders Nothing OS meteorological telemetry card.
    """
    val_str = f"{value:.1f}" if value is not None else "--"
    html = f"""
    <div class="ag-card" style="
        background: #141414;
        border: 1px solid #242424;
        border-radius: 12px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
        transition: border-color 0.2s ease, transform 0.2s ease;
    ">
        <div style="
            font-size: 1.5rem;
            background: #1A1A1A;
            border: 1px solid #282828;
            border-radius: 10px;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        ">
            {icon}
        </div>
        <div>
            <div style="color: #888888; font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                {label}
            </div>
            <div style="font-family: var(--font-mono); font-size: 1.35rem; font-weight: 700; color: #FFFFFF;">
                {val_str} <span style="font-size: 0.75rem; color: #666666; font-family: var(--font-sans); font-weight: 400;">{unit}</span>
            </div>
        </div>
    </div>
    """
    safe_markdown(html)
