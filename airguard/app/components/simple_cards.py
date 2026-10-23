"""
AirGuard Simple Mode Presentation Components.
Bespoke, human-crafted environmental decision-support cards designed for clarity,
elegance, and zero visual clutter.
"""

from __future__ import annotations

import streamlit as st
from typing import Optional, Dict, Any, List
from app.components.design_system import safe_markdown, ICONS


def get_simple_status_style(status_level: str) -> Dict[str, str]:
    """
    Returns semantic colors, icons, and refined styling tokens for safety levels.
    """
    level_lower = status_level.lower()
    if "high" in level_lower or "severe" in level_lower or "very" in level_lower:
        return {
            "color": "#D71921",
            "bg": "rgba(215, 25, 33, 0.12)",
            "border": "rgba(215, 25, 33, 0.35)",
            "glow_subtle": "rgba(215, 25, 33, 0.2)",
            "icon": "🔴",
            "label": "High Risk",
            "badge_class": "ag-badge-avoid",
            "gradient": "linear-gradient(180deg, #161A26 0%, #10131D 100%)",
            "top_line": "#D71921"
        }
    elif "avoid" in level_lower or "unhealthy" in level_lower:
        return {
            "color": "#EF4444",
            "bg": "rgba(239, 68, 68, 0.12)",
            "border": "rgba(239, 68, 68, 0.35)",
            "glow_subtle": "rgba(239, 68, 68, 0.2)",
            "icon": "🛑",
            "label": "Avoid",
            "badge_class": "ag-badge-avoid",
            "gradient": "linear-gradient(180deg, #161A26 0%, #10131D 100%)",
            "top_line": "#EF4444"
        }
    elif "caution" in level_lower:
        return {
            "color": "#F97316",
            "bg": "rgba(249, 115, 22, 0.12)",
            "border": "rgba(249, 115, 22, 0.35)",
            "glow_subtle": "rgba(249, 115, 22, 0.2)",
            "icon": "⚠️",
            "label": "Caution",
            "badge_class": "ag-badge-caution",
            "gradient": "linear-gradient(180deg, #161A26 0%, #10131D 100%)",
            "top_line": "#F97316"
        }
    elif "moderate" in level_lower:
        return {
            "color": "#F59E0B",
            "bg": "rgba(245, 158, 11, 0.12)",
            "border": "rgba(245, 158, 11, 0.35)",
            "glow_subtle": "rgba(245, 158, 11, 0.2)",
            "icon": "🟡",
            "label": "Moderate",
            "badge_class": "ag-badge-moderate",
            "gradient": "linear-gradient(180deg, #161A26 0%, #10131D 100%)",
            "top_line": "#F59E0B"
        }
    else:
        return {
            "color": "#10B981",
            "bg": "rgba(16, 185, 129, 0.12)",
            "border": "rgba(16, 185, 129, 0.35)",
            "glow_subtle": "rgba(16, 185, 129, 0.2)",
            "icon": "🟢",
            "label": "Safe",
            "badge_class": "ag-badge-good",
            "gradient": "linear-gradient(180deg, #161A26 0%, #10131D 100%)",
            "top_line": "#10B981"
        }


def render_air_safety_card(
    city_name: str,
    status_level: str,
    answer_text: str,
    best_window: str,
    avoid_hours: List[str] | str,
    main_reason: str,
    recommendation: str,
    mask_tip: Optional[str] = None,
    live_timestamp: Optional[str] = None
) -> None:
    """
    Renders the primary Air Safety Directive Card for Simple Mode.
    Human-crafted, editorial, high-contrast decision support.
    """
    theme = get_simple_status_style(status_level)

    # Format avoid hours
    if isinstance(avoid_hours, list):
        if avoid_hours:
            avoid_str = ", ".join(avoid_hours[:2])
        else:
            avoid_str = "None expected today — air is safe"
    else:
        avoid_str = avoid_hours or "None expected today — air is safe"

    mask_html = ""
    if mask_tip:
        mask_html = f"""
        <div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px; background: rgba(15, 23, 42, 0.6); border-radius: 10px; border: 1px solid rgba(56, 189, 248, 0.2); font-family: var(--font-sans); font-size: 0.85rem; color: #CBD5E1; margin-top: 14px;">
            <span style="font-size: 1.1rem; line-height: 1;">😷</span>
            <div>
                <strong style="color: #FFFFFF; font-weight: 600;">Mask & Window Advice:</strong> {mask_tip}
            </div>
        </div>
        """

    live_indicator = f"""
    <div style="display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-size: 0.74rem; color: #38BDF8; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); padding: 4px 10px; border-radius: 6px;">
        <span class="ag-pulse-dot"></span>
        <span>{live_timestamp}</span>
    </div>
    """ if live_timestamp else """
    <span style="font-family: var(--font-sans); font-size: 0.74rem; color: #64748B;">
        Today's Outdoor Directive
    </span>
    """

    html = f"""
    <div style="
        background: {theme['gradient']};
        border: 1px solid var(--ag-border);
        border-top: 3px solid {theme['top_line']};
        border-radius: 20px;
        padding: 30px 34px;
        margin-bottom: 24px;
        box-shadow: 0 16px 40px -8px rgba(0, 0, 0, 0.5), 0 0 24px -6px {theme['glow_subtle']};
        position: relative;
        overflow: hidden;
    ">
        <!-- Top Status Bar -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 18px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="
                    background: {theme['bg']};
                    border: 1px solid {theme['border']};
                    color: {theme['color']};
                    font-family: var(--font-sans);
                    font-size: 0.76rem;
                    font-weight: 700;
                    padding: 4px 12px;
                    border-radius: 9999px;
                    text-transform: uppercase;
                    letter-spacing: 0.04em;
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                ">
                    <span>●</span> {theme['label']} Conditions
                </span>
                <span style="font-family: var(--font-sans); font-size: 0.85rem; font-weight: 600; color: #94A3B8;">
                    {city_name}
                </span>
            </div>
            {live_indicator}
        </div>

        <!-- Big Clear Decision Headline -->
        <h2 style="margin: 0 0 10px 0; font-family: var(--font-heading); font-size: 1.95rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.03em; line-height: 1.25;">
            {answer_text}
        </h2>

        <!-- Actionable Recommendation -->
        <p style="margin: 0 0 22px 0; font-family: var(--font-sans); font-size: 0.98rem; color: #CBD5E1; line-height: 1.6;">
            {recommendation}
        </p>

        <!-- Two Core Decision Tickets -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 16px;">
            <!-- Best Window -->
            <div style="
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(13, 19, 31, 0.8) 100%);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 14px;
                padding: 18px 22px;
            ">
                <div style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; color: #34D399; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                    ✨ Best Safe Time Window
                </div>
                <div style="font-family: var(--font-mono); font-size: 1.45rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em; margin-bottom: 4px;">
                    {best_window}
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.78rem; color: #94A3B8;">
                    Cleanest predicted air period for outdoor activity
                </div>
            </div>

            <!-- Hours to Avoid -->
            <div style="
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(13, 19, 31, 0.8) 100%);
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 14px;
                padding: 18px 22px;
            ">
                <div style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; color: #F87171; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                    ⚠️ Hours to Avoid
                </div>
                <div style="font-family: var(--font-mono); font-size: 1.35rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em; margin-bottom: 4px;">
                    {avoid_str}
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.78rem; color: #94A3B8;">
                    High pollution hours — limit outdoor exertion
                </div>
            </div>
        </div>

        <!-- Plain English Explanation -->
        <div style="
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--ag-border);
            border-left: 3px solid #64748B;
            border-radius: 10px;
            padding: 12px 18px;
            font-family: var(--font-sans);
            font-size: 0.85rem;
            color: #94A3B8;
            line-height: 1.55;
        ">
            <strong style="color: #FFFFFF; font-weight: 600;">Why:</strong> {main_reason}
        </div>

        {mask_html}
    </div>
    """
    safe_markdown(html)


def render_simple_timeline(hourly_data: List[Dict[str, Any]]) -> None:
    """
    Renders a friendly 24-hour safe/caution/avoid visual track for Simple Mode.
    Green = Safe, Yellow = Caution, Orange = Sensitive, Red = Avoid.
    """
    if not hourly_data:
        return

    boxes_html = []
    for item in hourly_data[:24]:
        time_label = item.get("time", "")
        status = item.get("status", "Safe")
        color = item.get("color", "#10B981")
        pm25_val = item.get("pm25", 0.0)

        if "avoid" in status.lower() or "unhealthy" in status.lower():
            badge_text = "Avoid"
            dot_color = "#EF4444"
            badge_bg = "rgba(239, 68, 68, 0.15)"
            badge_border = "rgba(239, 68, 68, 0.3)"
        elif "caution" in status.lower() or "moderate" in status.lower():
            badge_text = "Caution"
            dot_color = "#F59E0B"
            badge_bg = "rgba(245, 158, 11, 0.15)"
            badge_border = "rgba(245, 158, 11, 0.3)"
        else:
            badge_text = "Safe"
            dot_color = "#10B981"
            badge_bg = "rgba(16, 185, 129, 0.15)"
            badge_border = "rgba(16, 185, 129, 0.3)"

        boxes_html.append(f"""
        <div style="
            flex: 0 0 68px;
            background: rgba(11, 15, 25, 0.7);
            border: 1px solid var(--ag-border);
            border-radius: 12px;
            padding: 10px 4px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
        ">
            <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #94A3B8; font-weight: 600;">
                {time_label}
            </span>
            <span style="
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: {dot_color};
                box-shadow: 0 0 8px {dot_color};
                display: inline-block;
            "></span>
            <span style="
                background: {badge_bg};
                border: 1px solid {badge_border};
                color: {dot_color};
                font-family: var(--font-sans);
                font-size: 0.62rem;
                font-weight: 700;
                padding: 1px 6px;
                border-radius: 9999px;
                text-transform: uppercase;
                letter-spacing: 0.03em;
            ">
                {badge_text}
            </span>
        </div>
        """)

    strip_content = "".join(boxes_html)
    container_html = f"""
    <div style="
        background: var(--ag-surface);
        border: 1px solid var(--ag-border);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">
            <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
                <span>📅</span> 24-Hour Safe Outdoor Timeline
            </div>
            <div style="display: flex; gap: 14px; font-family: var(--font-sans); font-size: 0.74rem;">
                <span style="color: #34D399;">● Green = Safe</span>
                <span style="color: #FBBF24;">● Yellow = Caution</span>
                <span style="color: #F87171;">● Red = Avoid</span>
            </div>
        </div>
        <div style="display: flex; gap: 6px; overflow-x: auto; padding-bottom: 6px; scrollbar-width: thin;">
            {strip_content}
        </div>
    </div>
    """
    safe_markdown(container_html)


def render_todays_tip(aqi: int, wind_speed: float, humidity: float) -> None:
    """
    Renders one short, practical non-technical insight for Simple Mode.
    """
    if aqi <= 50:
        tip_title = "Great Day for Outdoors"
        tip_text = "The air is wonderfully clean and fresh today! Open your windows for fresh indoor air, and enjoy running, walking, or playing outside."
        tip_icon = "🌿"
    elif aqi <= 100:
        if wind_speed < 2.0:
            tip_title = "Light Winds in the Afternoon"
            tip_text = "Calm air may keep car exhaust near street level this afternoon. If walking or cycling, pick quiet neighborhood streets or parks away from heavy traffic."
        else:
            tip_title = "Breezy & Mostly Clean"
            tip_text = "A gentle breeze is helping disperse pollutants. Outdoor activities are safe, but anyone with asthma should keep their regular inhaler on hand."
        tip_icon = "🍃"
    elif aqi <= 150:
        tip_title = "Caution for Sensitive Lungs"
        tip_text = "Air pollution is elevated today. Sensitive adults and children should choose gentler activities and schedule outdoor walks before 10 AM or after sunset."
        tip_icon = "💡"
    else:
        tip_title = "Keep Windows Closed Today"
        tip_text = "Air pollution is high today. Keep home windows closed, avoid outdoor cardio, and consider wearing an N95 mask if you need to travel through heavy traffic."
        tip_icon = "🛡️"

    html = f"""
    <div style="
        background: var(--ag-surface);
        border: 1px solid var(--ag-border);
        border-left: 3px solid #F59E0B;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 24px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
    ">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span style="font-size: 1.15rem;">{tip_icon}</span>
            <span style="font-family: var(--font-heading); font-size: 0.92rem; font-weight: 700; color: #FFFFFF;">
                Today's Tip: {tip_title}
            </span>
        </div>
        <p style="margin: 0; font-family: var(--font-sans); font-size: 0.86rem; color: #94A3B8; line-height: 1.55;">
            {tip_text}
        </p>
    </div>
    """
    safe_markdown(html)


def render_simple_alert_setup(current_threshold: float, on_save_callback=None) -> None:
    """
    Renders a friendly alert configuration card for Simple Mode.
    'Warn me when AQI crosses ___'
    """
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
                <span>🔔</span> Simple Safety Alerts
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.82rem; color: #94A3B8; margin-bottom: 12px; line-height: 1.45;">
                Set a personal alert level. AirGuard will notify you whenever pollution rises above your comfort line.
            </p>
            """,
            unsafe_allow_html=True
        )

        col_s1, col_s2 = st.columns([2.0, 1.0])

        with col_s1:
            presets = {
                "Sensitive (Warn me if air is Moderate or worse)": 35.0,
                "Standard (Warn me if air becomes Unhealthy for sensitive groups)": 55.0,
                "Strict (Warn me at the slightest rise in pollution)": 25.0,
                "High Tolerance (Warn me only during severe pollution)": 80.0
            }

            matched_key = None
            for k, v in presets.items():
                if abs(v - current_threshold) < 5.0:
                    matched_key = k
                    break
            if not matched_key:
                matched_key = "Standard (Warn me if air becomes Unhealthy for sensitive groups)"

            selected_preset = st.selectbox(
                "When should we warn you?",
                options=list(presets.keys()),
                index=list(presets.keys()).index(matched_key),
                label_visibility="collapsed"
            )

        with col_s2:
            new_val = presets[selected_preset]
            if st.button("💾 Save Alert Level", key="btn_save_simple_alert", use_container_width=True):
                if on_save_callback:
                    on_save_callback(new_val)
                st.success(f"Alert level saved! We will warn you if PM₂.₅ exceeds {new_val:.0f} µg/m³.")


def render_simple_disclaimer() -> None:
    """
    Renders the required visible safety disclaimer for Simple Mode.
    """
    html = """
    <div style="
        background: rgba(11, 15, 23, 0.5);
        border: 1px solid var(--ag-border);
        border-radius: 10px;
        padding: 12px 18px;
        margin-top: 24px;
        font-family: var(--font-sans);
        font-size: 0.74rem;
        color: #64748B;
        line-height: 1.5;
        text-align: center;
    ">
        <strong>Safety Note:</strong> This app gives general environmental safety guidance based on outdoor sensor readings and mathematical forecasts. It does not provide medical diagnosis or treatment. Follow your doctor's advice for personal health decisions.
    </div>
    """
    safe_markdown(html)


def render_simple_weather_cards(
    temperature: Optional[float],
    humidity: Optional[float],
    wind_speed: Optional[float]
) -> None:
    """
    Renders 3 friendly weather cards for Simple Mode.
    Translates raw meteorological variables into clear human comfort explanations.
    """
    temp_val = f"{temperature:.0f}°C" if temperature is not None else "--"
    if temperature is not None:
        if temperature < 15:
            temp_note = "Cool & crisp air"
        elif temperature <= 28:
            temp_note = "Pleasantly comfortable"
        else:
            temp_note = "Warm outdoor temperatures"
    else:
        temp_note = "Temperature data pending"

    hum_val = f"{humidity:.0f}%" if humidity is not None else "--"
    if humidity is not None:
        if humidity < 40:
            hum_note = "Dry air — stay hydrated"
        elif humidity <= 70:
            hum_note = "Normal comfortable moisture"
        else:
            hum_note = "Humid — may hold particles near ground"
    else:
        hum_note = "Humidity data pending"

    wind_val = f"{wind_speed:.1f} km/h" if wind_speed is not None else "--"
    if wind_speed is not None:
        if wind_speed < 5:
            wind_note = "Still air — smoke tends to settle"
        elif wind_speed <= 18:
            wind_note = "Gentle breeze helps clear pollutants"
        else:
            wind_note = "Brisk winds — active dust dispersion"
    else:
        wind_note = "Wind data pending"

    html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-bottom: 24px;">
        <div style="
            background: var(--ag-surface);
            border: 1px solid var(--ag-border);
            border-radius: 14px;
            padding: 18px 22px;
        ">
            <div style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                🌡️ Outdoor Temperature
            </div>
            <div style="font-family: var(--font-mono); font-size: 1.85rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em;">
                {temp_val}
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.78rem; color: #CBD5E1; margin-top: 4px;">
                {temp_note}
            </div>
        </div>

        <div style="
            background: var(--ag-surface);
            border: 1px solid var(--ag-border);
            border-radius: 14px;
            padding: 18px 22px;
        ">
            <div style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                💧 Air Moisture (Humidity)
            </div>
            <div style="font-family: var(--font-mono); font-size: 1.85rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em;">
                {hum_val}
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.78rem; color: #CBD5E1; margin-top: 4px;">
                {hum_note}
            </div>
        </div>

        <div style="
            background: var(--ag-surface);
            border: 1px solid var(--ag-border);
            border-radius: 14px;
            padding: 18px 22px;
        ">
            <div style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                💨 Wind & Ventilation
            </div>
            <div style="font-family: var(--font-mono); font-size: 1.85rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em;">
                {wind_val}
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.78rem; color: #CBD5E1; margin-top: 4px;">
                {wind_note}
            </div>
        </div>
    </div>
    """
    safe_markdown(html)


def render_simple_pollutant_cards(pm25: float, pm10: Optional[float] = None) -> None:
    """
    Renders 2 plain-language pollutant explanation cards for Simple Mode.
    Translates raw numbers into plain meanings (Tiny harmful particles vs Coarse dust).
    """
    if pm25 <= 15:
        pm25_status = "Very Clean"
        pm25_color = "#10B981"
        pm25_desc = "Tiny particles are low and air is very healthy to breathe."
    elif pm25 <= 35:
        pm25_status = "Moderate"
        pm25_color = "#F59E0B"
        pm25_desc = "Acceptable air. Fine for most healthy adults."
    elif pm25 <= 75:
        pm25_status = "High"
        pm25_color = "#F97316"
        pm25_desc = "Tiny harmful particles in the air are elevated. Sensitive lungs should limit time outside."
    else:
        pm25_status = "Very High"
        pm25_color = "#EF4444"
        pm25_desc = "Tiny harmful particles are at dangerous levels. Avoid outdoor exercise."

    pm10_val = pm10 if pm10 is not None else pm25 * 1.6
    if pm10_val <= 45:
        pm10_status = "Low Dust"
        pm10_color = "#10B981"
        pm10_desc = "Coarse dust, pollen, and road grit are low."
    elif pm10_val <= 100:
        pm10_status = "Moderate Dust"
        pm10_color = "#F59E0B"
        pm10_desc = "Some road dust or pollen present, but generally fine."
    else:
        pm10_status = "Heavy Dust"
        pm10_color = "#EF4444"
        pm10_desc = "Noticeable dust, smoke, or pollen in the air."

    html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 24px;">
        <div style="
            background: var(--ag-surface);
            border: 1px solid var(--ag-border);
            border-left: 3px solid {pm25_color};
            border-radius: 14px;
            padding: 20px 24px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-family: var(--font-heading); font-size: 0.94rem; font-weight: 700; color: #FFFFFF;">
                    🔬 Tiny Particles (PM₂.₅)
                </span>
                <span style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; color: {pm25_color}; background: rgba(255, 255, 255, 0.06); padding: 2px 8px; border-radius: 9999px; border: 1px solid {pm25_color};">
                    ● {pm25_status}
                </span>
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #CBD5E1; margin: 0 0 8px 0; line-height: 1.55;">
                {pm25_desc}
            </p>
            <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #94A3B8;">
                Measured: {pm25:.1f} µg/m³ (particles 30x smaller than a human hair)
            </div>
        </div>

        <div style="
            background: var(--ag-surface);
            border: 1px solid var(--ag-border);
            border-left: 3px solid {pm10_color};
            border-radius: 14px;
            padding: 20px 24px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-family: var(--font-heading); font-size: 0.94rem; font-weight: 700; color: #FFFFFF;">
                    💨 Coarse Dust & Pollen (PM₁₀)
                </span>
                <span style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; color: {pm10_color}; background: rgba(255, 255, 255, 0.06); padding: 2px 8px; border-radius: 9999px; border: 1px solid {pm10_color};">
                    ● {pm10_status}
                </span>
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #CBD5E1; margin: 0 0 8px 0; line-height: 1.55;">
                {pm10_desc}
            </p>
            <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #94A3B8;">
                Measured: {pm10_val:.1f} µg/m³ (road dust, vehicle grit, construction particles)
            </div>
        </div>
    </div>
    """
    safe_markdown(html)


def render_simple_indoor_mask_cards(mask_advice: Any, indoor_advice: Any) -> None:
    """
    Renders 2 side-by-side cards for Mask guidance and Indoor air protection.
    """
    if isinstance(mask_advice, (list, tuple)):
        mask_content = "<ul style='margin: 0; padding-left: 18px; line-height: 1.6; color: #CBD5E1; font-size: 0.86rem;'>" + "".join(f"<li style='margin-bottom: 4px;'>{item}</li>" for item in mask_advice) + "</ul>"
    else:
        mask_content = f"<p style='font-family: var(--font-sans); font-size: 0.86rem; color: #CBD5E1; margin: 0; line-height: 1.6;'>{mask_advice}</p>"

    if isinstance(indoor_advice, (list, tuple)):
        indoor_content = "<ul style='margin: 0; padding-left: 18px; line-height: 1.6; color: #CBD5E1; font-size: 0.86rem;'>" + "".join(f"<li style='margin-bottom: 4px;'>{item}</li>" for item in indoor_advice) + "</ul>"
    else:
        indoor_content = f"<p style='font-family: var(--font-sans); font-size: 0.86rem; color: #CBD5E1; margin: 0; line-height: 1.6;'>{indoor_advice}</p>"

    html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 24px;">
        <div style="
            background: var(--ag-surface);
            border: 1px solid var(--ag-border);
            border-left: 3px solid #38BDF8;
            border-radius: 14px;
            padding: 20px 24px;
        ">
            <div style="font-family: var(--font-heading); font-size: 0.94rem; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
                <span>😷</span> Mask Advice
            </div>
            {mask_content}
        </div>

        <div style="
            background: var(--ag-surface);
            border: 1px solid var(--ag-border);
            border-left: 3px solid #10B981;
            border-radius: 14px;
            padding: 20px 24px;
        ">
            <div style="font-family: var(--font-heading); font-size: 0.94rem; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
                <span>🏠</span> Indoor Air Defense
            </div>
            {indoor_content}
        </div>
    </div>
    """
    safe_markdown(html)
