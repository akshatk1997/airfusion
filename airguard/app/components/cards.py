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
    Returns accessible high-contrast colors and cinematic lighting styles based on AQI value.
    Complies with WCAG AAA contrast guidelines with atmospheric optical glow effects.
    """
    if aqi <= 50:
        return {
            "bg": "rgba(16, 185, 129, 0.16)",
            "border": "#10B981",
            "text": "#34D399",
            "glow": "0 0 25px rgba(16, 185, 129, 0.35), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)",
            "glow_color": "rgba(16, 185, 129, 0.5)",
            "gradient": "radial-gradient(ellipse 70% 60% at 85% 15%, rgba(16, 185, 129, 0.22), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(8, 12, 20, 0.98) 100%)"
        }
    elif aqi <= 100:
        return {
            "bg": "rgba(245, 158, 11, 0.16)",
            "border": "#F59E0B",
            "text": "#FBBF24",
            "glow": "0 0 25px rgba(245, 158, 11, 0.35), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)",
            "glow_color": "rgba(245, 158, 11, 0.5)",
            "gradient": "radial-gradient(ellipse 70% 60% at 85% 15%, rgba(245, 158, 11, 0.22), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(8, 12, 20, 0.98) 100%)"
        }
    elif aqi <= 150:
        return {
            "bg": "rgba(249, 115, 22, 0.16)",
            "border": "#F97316",
            "text": "#FB923C",
            "glow": "0 0 25px rgba(249, 115, 22, 0.35), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)",
            "glow_color": "rgba(249, 115, 22, 0.5)",
            "gradient": "radial-gradient(ellipse 70% 60% at 85% 15%, rgba(249, 115, 22, 0.22), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(8, 12, 20, 0.98) 100%)"
        }
    elif aqi <= 200:
        return {
            "bg": "rgba(239, 68, 68, 0.16)",
            "border": "#EF4444",
            "text": "#F87171",
            "glow": "0 0 30px rgba(239, 68, 68, 0.4), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)",
            "glow_color": "rgba(239, 68, 68, 0.55)",
            "gradient": "radial-gradient(ellipse 70% 60% at 85% 15%, rgba(239, 68, 68, 0.25), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(8, 12, 20, 0.98) 100%)"
        }
    elif aqi <= 300:
        return {
            "bg": "rgba(168, 85, 247, 0.16)",
            "border": "#A855F7",
            "text": "#C084FC",
            "glow": "0 0 30px rgba(168, 85, 247, 0.4), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)",
            "glow_color": "rgba(168, 85, 247, 0.55)",
            "gradient": "radial-gradient(ellipse 70% 60% at 85% 15%, rgba(168, 85, 247, 0.25), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(8, 12, 20, 0.98) 100%)"
        }
    else:
        return {
            "bg": "rgba(136, 19, 55, 0.25)",
            "border": "#E11D48",
            "text": "#FB7185",
            "glow": "0 0 35px rgba(225, 29, 72, 0.5), inset 0 1px 0 0 rgba(255, 255, 255, 0.15)",
            "glow_color": "rgba(225, 29, 72, 0.65)",
            "gradient": "radial-gradient(ellipse 70% 60% at 85% 15%, rgba(136, 19, 55, 0.35), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(8, 12, 20, 0.98) 100%)"
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
    Renders high-impact cinematic Hero AQI card with progress position bar,
    optical ambient backlight, high-contrast pill, and glowing mono typography.
    """
    theme = get_aqi_badge_style(aqi)
    # Calculate percentage along 0-500 scale capped at 100%
    pct = min(100.0, max(2.0, (aqi / 500.0) * 100.0))

    html = f"""
    <div style="
        background: {theme['gradient']};
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-top: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: {theme['glow']}, 0 20px 50px -10px rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        position: relative;
        overflow: hidden;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 20px; position: relative; z-index: 1;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                    <span style="
                        background: {theme['bg']};
                        border: 1px solid {theme['border']};
                        color: {theme['text']};
                        font-size: 0.85rem;
                        font-weight: 700;
                        padding: 6px 14px;
                        border-radius: 9999px;
                        letter-spacing: 0.04em;
                        text-transform: uppercase;
                        display: inline-flex;
                        align-items: center;
                        gap: 6px;
                        box-shadow: 0 0 12px {theme['glow_color']};
                    ">
                        ● {category}
                    </span>
                    <span style="font-size: 0.78rem; color: #94A3B8; font-weight: 500;">US EPA Standard</span>
                </div>
                <h1 style="margin: 0 0 6px 0; font-size: 2.35rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.025em; text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);">
                    {city}
                </h1>
                <p style="margin: 0; font-size: 0.82rem; color: #94A3B8;">
                    Telemetry Last Verified: <span style="color: #E2E8F0; font-family: 'JetBrains Mono', monospace;">{timestamp}</span>
                </p>
            </div>
            
            <div style="text-align: right; min-width: 140px;">
                <div style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 4.4rem;
                    font-weight: 800;
                    line-height: 0.92;
                    color: {theme['text']};
                    letter-spacing: -0.04em;
                    text-shadow: 0 0 24px {theme['glow_color']};
                ">
                    {aqi}
                </div>
                <div style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px;">
                    AIR QUALITY INDEX
                </div>
                <div style="font-size: 0.85rem; color: #E2E8F0; font-family: 'JetBrains Mono', monospace; margin-top: 4px;">
                    PM₂.₅: <b style="color: #FFFFFF;">{pm25_val:.1f}</b> µg/m³
                </div>
            </div>
        </div>

        <!-- AQI Scale Bar with Cinematic Illuminated Marker -->
        <div style="margin-top: 26px; position: relative; z-index: 1;">
            <div style="display: flex; justify-content: space-between; font-size: 0.72rem; font-family: 'JetBrains Mono', monospace; color: #94A3B8; margin-bottom: 8px;">
                <span>0 Good</span>
                <span>50 Moderate</span>
                <span>100 Sensitive</span>
                <span>150 Unhealthy</span>
                <span>300+ Hazardous</span>
            </div>
            <div style="
                height: 10px;
                background: rgba(255, 255, 255, 0.08);
                border-radius: 9999px;
                position: relative;
            ">
                <div style="
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, #10B981 0%, #F59E0B 30%, #EF4444 60%, #A855F7 85%, #881337 100%);
                    border-radius: 9999px;
                    opacity: 0.85;
                "></div>
                <div style="
                    position: absolute;
                    left: calc({pct}% - 6px);
                    top: -2px;
                    width: 14px;
                    height: 14px;
                    background: #FFFFFF;
                    border: 2px solid {theme['border']};
                    border-radius: 50%;
                    box-shadow: 0 0 10px #FFFFFF, 0 0 16px {theme['border']};
                    transition: left 0.6s cubic-bezier(0.16, 1, 0.3, 1);
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
    Renders standardized pollutant telemetry card with subscript formatting and cinematic depth.
    """
    val_str = f"{value:.1f}" if (value is not None and value >= 0) else "--"
    delta_html = f"<span style='color: #34D399; font-size: 0.78rem; font-weight: 600; margin-left: 6px;'>{delta}</span>" if delta else ""

    html = f"""
    <div class="ag-card ag-metric-card" style="
        background: radial-gradient(circle at 85% 15%, rgba(56, 189, 248, 0.05), transparent 60%), rgba(17, 24, 39, 0.88);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(255, 255, 255, 0.16);
        border-radius: 14px;
        padding: 16px 18px;
        height: 100%;
        box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.4), inset 0 1px 0 0 rgba(255, 255, 255, 0.08);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    ">
        <div>
            <div style="color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                {label}
            </div>
            <div style="display: flex; align-items: baseline; gap: 4px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #F8FAFC; letter-spacing: -0.02em; text-shadow: 0 0 16px rgba(255, 255, 255, 0.15);">
                    {val_str}
                </span>
                <span style="color: #64748B; font-size: 0.8rem; font-weight: 500;">
                    {unit}
                </span>
                {delta_html}
            </div>
        </div>
        <div style="color: #64748B; font-size: 0.75rem; margin-top: 8px; border-top: 1px solid rgba(255, 255, 255, 0.06); padding-top: 6px;">
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
    Renders meteorological telemetry card with cinematic glass and icon aura.
    """
    val_str = f"{value:.1f}" if value is not None else "--"
    html = f"""
    <div class="ag-card" style="
        background: radial-gradient(circle at 15% 20%, rgba(56, 189, 248, 0.06), transparent 70%), rgba(17, 24, 39, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.35), inset 0 1px 0 0 rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    ">
        <div style="
            font-size: 1.6rem;
            background: rgba(11, 15, 23, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            width: 46px;
            height: 46px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
        ">
            {icon}
        </div>
        <div>
            <div style="color: #94A3B8; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">
                {label}
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.35rem; font-weight: 700; color: #F8FAFC; text-shadow: 0 0 12px rgba(255, 255, 255, 0.1);">
                {val_str} <span style="font-size: 0.75rem; color: #64748B; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 400;">{unit}</span>
            </div>
        </div>
    </div>
    """
    safe_markdown(html)
