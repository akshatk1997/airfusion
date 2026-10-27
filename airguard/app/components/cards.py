"""
Modern Environmental Tech UI Cards Component for AirFusion.
Features WCAG AAA high-contrast badges, dynamic progress scale bars,
and cinematic atmospheric lighting.
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
            "dot": "#10B981",
            "glow": "0 0 25px rgba(16, 185, 129, 0.35), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)",
            "glow_color": "rgba(16, 185, 129, 0.5)",
            "gradient": "radial-gradient(ellipse 70% 60% at 85% 15%, rgba(16, 185, 129, 0.22), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(8, 12, 20, 0.98) 100%)"
        }
    elif aqi <= 100:
        return {
            "bg": "rgba(245, 158, 11, 0.16)",
            "border": "#F59E0B",
            "text": "#FBBF24",
            "dot": "#F59E0B",
            "glow": "0 0 25px rgba(245, 158, 11, 0.35), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)",
            "glow_color": "rgba(245, 158, 11, 0.5)",
            "gradient": "radial-gradient(ellipse 70% 60% at 85% 15%, rgba(245, 158, 11, 0.22), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(8, 12, 20, 0.98) 100%)"
        }
    elif aqi <= 150:
        return {
            "bg": "rgba(249, 115, 22, 0.16)",
            "border": "#F97316",
            "text": "#FB923C",
            "dot": "#F97316",
            "glow": "0 0 25px rgba(249, 115, 22, 0.35), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)",
            "glow_color": "rgba(249, 115, 22, 0.5)",
            "gradient": "radial-gradient(ellipse 70% 60% at 85% 15%, rgba(249, 115, 22, 0.22), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(8, 12, 20, 0.98) 100%)"
        }
    elif aqi <= 200:
        return {
            "bg": "rgba(239, 68, 68, 0.16)",
            "border": "#EF4444",
            "text": "#F87171",
            "dot": "#EF4444",
            "glow": "0 0 30px rgba(239, 68, 68, 0.4), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)",
            "glow_color": "rgba(239, 68, 68, 0.55)",
            "gradient": "radial-gradient(ellipse 70% 60% at 85% 15%, rgba(239, 68, 68, 0.25), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(8, 12, 20, 0.98) 100%)"
        }
    elif aqi <= 300:
        return {
            "bg": "rgba(168, 85, 247, 0.16)",
            "border": "#A855F7",
            "text": "#C084FC",
            "dot": "#A855F7",
            "glow": "0 0 30px rgba(168, 85, 247, 0.4), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)",
            "glow_color": "rgba(168, 85, 247, 0.55)",
            "gradient": "radial-gradient(ellipse 70% 60% at 85% 15%, rgba(168, 85, 247, 0.25), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(8, 12, 20, 0.98) 100%)"
        }
    else:
        return {
            "bg": "rgba(136, 19, 55, 0.25)",
            "border": "#E11D48",
            "text": "#FB7185",
            "dot": "#E11D48",
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
        min-height: 295px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
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
                        font-family: var(--font-sans);
                        font-size: 0.78rem;
                        font-weight: 700;
                        padding: 3px 12px;
                        border-radius: 9999px;
                        letter-spacing: 0.05em;
                        text-transform: uppercase;
                        box-shadow: 0 0 12px {theme['bg']};
                        display: inline-flex;
                        align-items: center;
                        gap: 6px;
                    ">
                        <span style="width: 6px; height: 6px; border-radius: 50%; background: {theme['text']}; box-shadow: 0 0 8px {theme['text']};"></span>
                        {category}
                    </span>
                    <span style="color: #64748B; font-size: 0.75rem; font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.05em;">US EPA Standard</span>
                </div>
                <div style="margin: 0 0 6px 0; font-family: var(--font-heading); font-size: 2.35rem; font-weight: 800; color: #FFFFFF !important; letter-spacing: -0.025em; text-shadow: 0 2px 14px rgba(0, 0, 0, 0.6); line-height: 1.2;">
                    {city}
                </div>
                <p style="margin: 0; font-family: var(--font-mono); font-size: 0.8rem; color: #94A3B8;">
                    Telemetry Verified: <span style="color: #F8FAFC;">{timestamp}</span>
                </p>
            </div>
            
            <div style="text-align: right; min-width: 140px;">
                <div style="
                    font-family: var(--font-mono);
                    font-size: 5.2rem;
                    font-weight: 800;
                    line-height: 0.88;
                    color: {theme['text']};
                    text-shadow: 0 0 28px {theme['glow_color']};
                    letter-spacing: -0.03em;
                ">
                    {aqi}
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.74rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px;">
                    Air Quality Index
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.84rem; color: #CBD5E1; margin-top: 4px;">
                    PM₂.₅: <b style="color: #F8FAFC;">{pm25_val:.1f}</b> µg/m³
                </div>
            </div>
        </div>

        <!-- Progress Position Scale Bar with Glowing Needle/Pill -->
        <div style="margin-top: 28px; position: relative; z-index: 1;">
            <div style="display: flex; justify-content: space-between; font-size: 0.7rem; font-family: var(--font-mono); color: #64748B; margin-bottom: 8px;">
                <span>0 Good</span>
                <span>50 Moderate</span>
                <span>100 Sensitive</span>
                <span>150 Unhealthy</span>
                <span>300+ Hazardous</span>
            </div>
            <div style="
                height: 8px;
                background: rgba(15, 23, 42, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 9999px;
                position: relative;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.6);
            ">
                <div style="
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, #10B981 0%, #F59E0B 28%, #F97316 48%, #EF4444 68%, #A855F7 85%, #E11D48 100%);
                    border-radius: 9999px;
                    opacity: 0.9;
                "></div>
                <div style="
                    position: absolute;
                    left: calc({pct}% - 6px);
                    top: -3px;
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
    Renders standardized pollutant telemetry card with crisp contrast and AirFusion professional depth.
    """
    val_str = f"{value:.1f}" if (value is not None and value >= 0) else "--"
    delta_html = f"<span style='color: #059669; font-family: var(--font-mono); font-size: 0.78rem; font-weight: 600; margin-left: 6px;'>{delta}</span>" if delta else ""

    html = f"""
    <div class="ag-card ag-metric-card" style="
        background: #FFFFFF;
        border: 1px solid #EBE6DF;
        border-radius: 14px;
        padding: 18px 20px;
        height: 100%;
        min-height: 125px;
        box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    ">
        <div>
            <div style="color: #5A6E85; font-family: var(--font-sans); font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px;">
                {label}
            </div>
            <div style="display: flex; align-items: baseline; gap: 4px;">
                <span style="font-family: var(--font-mono); font-size: 1.85rem; font-weight: 800; color: #1F344C; letter-spacing: -0.02em;">
                    {val_str}
                </span>
                <span style="color: #8896A6; font-family: var(--font-sans); font-size: 0.8rem; font-weight: 600;">
                    {unit}
                </span>
                {delta_html}
            </div>
        </div>
        <div style="color: #5A6E85; font-family: var(--font-mono); font-size: 0.74rem; margin-top: 8px; border-top: 1px solid #EBE6DF; padding-top: 8px;">
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
    Renders meteorological telemetry card with clean AirFusion styling and clear contrast.
    """
    val_str = f"{value:.1f}" if value is not None else "--"
    html = f"""
    <div class="ag-card" style="
        background: #FFFFFF;
        border: 1px solid #EBE6DF;
        border-radius: 14px;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05);
        box-sizing: border-box;
    ">
        <div style="
            font-size: 1.5rem;
            background: #FAF6F1;
            border: 1px solid #EBE6DF;
            border-radius: 12px;
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
            <div style="color: #5A6E85; font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                {label}
            </div>
            <div style="font-family: var(--font-mono); font-size: 1.35rem; font-weight: 800; color: #1F344C;">
                {val_str} <span style="font-size: 0.75rem; color: #8896A6; font-family: var(--font-sans); font-weight: 500;">{unit}</span>
            </div>
        </div>
    </div>
    """
    safe_markdown(html)


def render_technical_weather_station(curr: Dict[str, Any], city: str) -> None:
    """
    Renders the quantitative Meteorological & Boundary Layer Weather Suite for Technical Mode.
    Provides thermodynamic state variables, kinematic wind vectors, photolysis proxies,
    and step-by-step 18-hour atmospheric continuum modeling.
    """
    import math

    temp_val = float(curr.get("temperature", 20.0) or 20.0)
    app_temp = float(curr.get("apparent_temperature", temp_val) or temp_val)
    hum_val = float(curr.get("humidity", 50.0) or 50.0)
    press_val = float(curr.get("pressure", 1013.0) or 1013.0)
    ws_val = float(curr.get("wind_speed", 5.0) or 5.0)
    wd_val = float(curr.get("wind_direction", 0.0) or 0.0)
    cardinal = curr.get("wind_direction_cardinal", "NE")
    gusts = float(curr.get("wind_gusts", ws_val * 1.5) or ws_val * 1.5)
    wmo_code = curr.get("weather_code", 0)
    weather_desc = curr.get("weather_desc", "Mainly Clear")
    weather_icon = curr.get("weather_icon", "🌤️")
    weather_summary = curr.get("weather_summary", "Stable atmospheric layer.")
    uv_val = float(curr.get("uv_index", 0.0) or 0.0)
    uv_cat = curr.get("uv_category", "Low")
    cloud_cover = float(curr.get("cloud_cover", 0.0) or 0.0)
    pop = int(curr.get("precipitation_probability", 0) or 0)
    precip_mm = float(curr.get("precipitation", 0.0) or 0.0)
    vis_km = float(curr.get("visibility_km", 10.0) or 10.0)
    sunrise = curr.get("sunrise", "06:30 AM")
    sunset = curr.get("sunset", "05:45 PM")
    hourly = curr.get("hourly_weather", [])

    # Magnus-Tetens Dew Point calculation & Dew Point Depression
    gamma = (17.27 * temp_val) / (237.7 + temp_val) + math.log(max(1.0, hum_val) / 100.0)
    dew_point = (237.7 * gamma) / (17.27 - gamma)
    depression = max(0.0, temp_val - dew_point)

    # Koschmieder optical extinction coefficient proxy: sigma = 3.912 / visibility_km
    extinction_coeff = (3.912 / max(0.1, vis_km)) if vis_km > 0 else 0.39

    # Meteorological Header Card
    html = f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #EBE6DF;
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(31, 52, 76, 0.05);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;">
            <div style="display: inline-flex; align-items: center; gap: 8px;">
                <span class="ag-badge ag-badge-neutral" style="font-family: var(--font-mono); font-size: 0.72rem; padding: 3px 10px; border-color: #38BDF8; color: #0284C7;">
                    METEOROLOGICAL SENTRY • WMO CODE {wmo_code}
                </span>
                <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #475569;">
                    Step-by-step on-time telemetry
                </span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px; font-family: var(--font-mono); font-size: 0.76rem; color: #24384D;">
                <span>🌅 Sunrise: <strong>{sunrise}</strong></span>
                <span style="color: #CBD5E1;">•</span>
                <span>🌇 Sunset: <strong>{sunset}</strong></span>
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="font-size: 3rem; line-height: 1;">
                    {weather_icon}
                </div>
                <div>
                    <div style="display: flex; align-items: baseline; gap: 10px;">
                        <span style="font-family: var(--font-mono); font-size: 2.8rem; font-weight: 800; color: #0F1E2E; letter-spacing: -0.03em; line-height: 1;">
                            {temp_val:.1f}°C
                        </span>
                        <span style="font-family: var(--font-mono); font-size: 0.84rem; font-weight: 700; color: #FF6845; background: rgba(255, 104, 69, 0.08); border: 1px solid rgba(255, 104, 69, 0.25); padding: 3px 10px; border-radius: 9999px;">
                            Apparent: {app_temp:.1f}°C
                        </span>
                    </div>
                    <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #0F1E2E; margin-top: 4px;">
                        {weather_desc} • {city} Mesoscale Station
                    </div>
                </div>
            </div>

            <div style="max-width: 520px; background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 12px; padding: 12px 18px;">
                <div style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700; color: #0F1E2E; text-transform: uppercase; margin-bottom: 2px;">
                    Boundary Layer Assessment
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.82rem; font-weight: 500; color: #24384D; line-height: 1.45;">
                    {weather_summary} Dew point depression ΔT = {depression:.1f}°C. Optical extinction σ_ext = {extinction_coeff:.3f} km⁻¹.
                </div>
            </div>
        </div>

        <!-- 4 Quantitative Columns -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin-bottom: 20px;">
            <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 14px; padding: 16px 18px;">
                <div style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                    💧 Moisture &amp; Dew Point
                </div>
                <div style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 800; color: #0F1E2E;">
                    {hum_val:.0f}% <span style="font-size: 0.75rem; color: #475569; font-weight: 600;">RH</span>
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.74rem; font-weight: 600; color: #24384D; margin-top: 4px;">
                    T_d: {dew_point:.1f}°C • ΔT: {depression:.1f}°C
                </div>
            </div>

            <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 14px; padding: 16px 18px;">
                <div style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                    💨 Wind Velocity &amp; Vector
                </div>
                <div style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 800; color: #0F1E2E;">
                    {ws_val:.1f} <span style="font-size: 0.75rem; color: #475569; font-weight: 600;">km/h</span>
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.74rem; font-weight: 600; color: #24384D; margin-top: 4px;">
                    Heading: {cardinal} ({wd_val:.0f}°) • Gusts: {gusts:.1f} km/h
                </div>
            </div>

            <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 14px; padding: 16px 18px;">
                <div style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                    ☀️ UV Index &amp; Irradiance
                </div>
                <div style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 800; color: #0F1E2E;">
                    {uv_val:.1f} <span style="font-size: 0.75rem; color: #475569; font-weight: 600;">UV ({uv_cat})</span>
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.74rem; font-weight: 600; color: #24384D; margin-top: 4px;">
                    Solar photolysis rate: {"Minimal" if uv_val < 3 else "Active O3 generation"}
                </div>
            </div>

            <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 14px; padding: 16px 18px;">
                <div style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                    🌧️ Rain &amp; Atmospheric Depth
                </div>
                <div style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 800; color: #0F1E2E;">
                    {pop}% <span style="font-size: 0.75rem; color: #475569; font-weight: 600;">Prob ({precip_mm:.1f} mm)</span>
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.74rem; font-weight: 600; color: #24384D; margin-top: 4px;">
                    Vis: {vis_km:.1f} km • Cloud: {cloud_cover:.0f}%
                </div>
            </div>
        </div>
    """

    # Hourly Progression strip
    if hourly:
        h_tiles = []
        for h in hourly[:18]:
            h_tiles.append(f"""
            <div style="
                flex: 0 0 92px;
                background: #FAF6F1;
                border: 1px solid #EBE6DF;
                border-radius: 12px;
                padding: 10px 4px;
                text-align: center;
                box-shadow: 0 1px 4px rgba(31, 52, 76, 0.02);
            ">
                <div style="font-family: var(--font-mono); font-size: 0.74rem; font-weight: 700; color: #475569;">
                    {h['time']}
                </div>
                <div style="font-size: 1.5rem; margin: 3px 0;">
                    {h['weather_icon']}
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.95rem; font-weight: 800; color: #0F1E2E;">
                    {h['temp']:.0f}°C
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.68rem; font-weight: 600; color: #24384D;">
                    {h['wind']:.0f}k • {h['pop']}%
                </div>
            </div>
            """)
        track_html = "\n".join(h_tiles)
        html += f"""
        <div style="border-top: 1px solid #EBE6DF; padding-top: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-family: var(--font-heading); font-size: 0.88rem; font-weight: 800; color: #0F1E2E;">
                    Step-by-Step 18-Hour Meteorological Progression
                </span>
                <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #475569;">
                    Wind speed (k) &amp; precipitation chance (%)
                </span>
            </div>
            <div style="display: flex; gap: 8px; overflow-x: auto; padding-bottom: 4px; scrollbar-width: thin;">
                {track_html}
            </div>
        </div>
        """

    html += "</div>"
    safe_markdown(html)
