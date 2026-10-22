"""
Simple Mode UI Cards & Visual Components for AirGuard.
Translates technical atmospheric telemetry, forecasting models, and risk evaluations
into plain, friendly language, large readable status cards, and action-oriented advice.
"""

from __future__ import annotations

import streamlit as st
from typing import Dict, Any, List, Optional
from app.components.design_system import safe_markdown, ICONS


def get_simple_status_style(status_level: str) -> Dict[str, str]:
    """
    Returns friendly color tokens for simple safety status levels.
    """
    status_clean = status_level.lower().strip()
    if "safe" in status_clean or "good" in status_clean or "low" in status_clean:
        return {
            "label": "Safe",
            "color": "#10B981",
            "bg": "rgba(16, 185, 129, 0.12)",
            "icon": "🟢",
            "badge_class": "ag-badge-good"
        }
    elif "moderate" in status_clean:
        return {
            "label": "Moderate",
            "color": "#F59E0B",
            "bg": "rgba(245, 158, 11, 0.12)",
            "icon": "🟡",
            "badge_class": "ag-badge-moderate"
        }
    elif "caution" in status_clean or "sensitive" in status_clean:
        return {
            "label": "Caution",
            "color": "#F97316",
            "bg": "rgba(249, 115, 22, 0.12)",
            "icon": "🟠",
            "badge_class": "ag-badge-sensitive"
        }
    elif "high risk" in status_clean or "hazardous" in status_clean or "very high" in status_clean:
        return {
            "label": "High Risk",
            "color": "#D71921",
            "bg": "rgba(215, 25, 33, 0.15)",
            "icon": "🛑",
            "badge_class": "ag-badge-hazardous"
        }
    else:
        return {
            "label": "Avoid",
            "color": "#EF4444",
            "bg": "rgba(239, 68, 68, 0.12)",
            "icon": "🔴",
            "badge_class": "ag-badge-unhealthy"
        }


def render_air_safety_card(
    city_name: str,
    status_level: str,
    answer_text: str,
    best_window: str,
    avoid_hours: List[str] | str,
    main_reason: str,
    recommendation: str,
    mask_tip: Optional[str] = None
) -> None:
    """
    Renders the primary Air Safety Card for Simple Mode.
    Answers: 'Is it safe for me to go outside right now?' with direct guidance.
    """
    theme = get_simple_status_style(status_level)

    # Format avoid hours
    if isinstance(avoid_hours, list):
        if avoid_hours:
            avoid_str = ", ".join(avoid_hours[:2])
        else:
            avoid_str = "None expected today"
    else:
        avoid_str = avoid_hours or "None expected today"

    mask_html = ""
    if mask_tip:
        mask_html = f"""
        <div style="margin-top: 14px; padding: 10px 14px; background: #181818; border-radius: 8px; border-left: 3px solid #38BDF8; font-family: var(--font-sans); font-size: 0.82rem; color: #CCCCCC;">
            <strong style="color: #FFFFFF;">😷 Mask & Window Advice:</strong> {mask_tip}
        </div>
        """

    html = f"""
    <div style="
        background: #121212;
        border: 1px solid #242424;
        border-radius: 16px;
        padding: 26px 30px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
    ">
        <!-- Top Status Row -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.25rem;">{theme['icon']}</span>
                <div>
                    <span style="
                        background: {theme['bg']};
                        border: 1px solid {theme['color']};
                        color: {theme['color']};
                        font-family: var(--font-sans);
                        font-size: 0.78rem;
                        font-weight: 700;
                        padding: 3px 12px;
                        border-radius: 9999px;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    ">
                        ● {theme['label']} Conditions
                    </span>
                    <span style="font-family: var(--font-mono); font-size: 0.74rem; color: #888888; margin-left: 10px;">
                        {city_name}
                    </span>
                </div>
            </div>
            <span style="font-family: var(--font-sans); font-size: 0.74rem; color: #777777;">
                Today's Outdoor Decision Guide
            </span>
        </div>

        <!-- Big Friendly Answer -->
        <h2 style="margin: 0 0 10px 0; font-family: var(--font-heading); font-size: 1.65rem; font-weight: 700; color: #FFFFFF; line-height: 1.3;">
            {answer_text}
        </h2>

        <!-- Actionable Recommendation -->
        <p style="margin: 0 0 18px 0; font-family: var(--font-sans); font-size: 0.95rem; color: #CCCCCC; line-height: 1.5;">
            {recommendation}
        </p>

        <!-- Two Core Decision Pillars -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin-bottom: 14px;">
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 14px 18px;">
                <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #10B981; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">
                    ✨ Best Safe Time Window
                </div>
                <div style="font-family: var(--font-heading); font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">
                    {best_window}
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.76rem; color: #A7F3D0; margin-top: 4px;">
                    Cleanest predicted air period for outdoor activity
                </div>
            </div>

            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 14px 18px;">
                <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #EF4444; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">
                    ⚠️ Hours to Avoid
                </div>
                <div style="font-family: var(--font-heading); font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">
                    {avoid_str}
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.76rem; color: #FCA5A5; margin-top: 4px;">
                    High pollution hours — limit outdoor exertion
                </div>
            </div>
        </div>

        <!-- Plain Reason -->
        <div style="background: #161616; border-left: 3px solid #666666; border-radius: 6px; padding: 10px 14px; font-family: var(--font-sans); font-size: 0.82rem; color: #AAAAAA; line-height: 1.5;">
            <strong style="color: #FFFFFF;">Why:</strong> {main_reason}
        </div>

        {mask_html}
    </div>
    """
    safe_markdown(html)


def render_simple_timeline(hourly_data: List[Dict[str, Any]]) -> None:
    """
    Renders a friendly 24-hour safe/caution/avoid visual strip for Simple Mode.
    Green = Safe, Yellow = Caution, Orange = Sensitive, Red = Avoid.
    """
    if not hourly_data:
        return

    boxes_html = []
    for item in hourly_data[:24]:
        time_label = item.get("time", "")
        status = item.get("status", "Safe")
        color = item.get("color", "#10B981")
        
        # Friendly simplified label
        if "avoid" in status.lower() or "unhealthy" in status.lower():
            badge_text = "Avoid"
            bg_tint = "rgba(239, 68, 68, 0.15)"
        elif "caution" in status.lower() or "moderate" in status.lower():
            badge_text = "Caution"
            bg_tint = "rgba(245, 158, 11, 0.15)"
        else:
            badge_text = "Safe"
            bg_tint = "rgba(16, 185, 129, 0.15)"

        boxes_html.append(f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #141414;
            border: 1px solid #282828;
            border-top: 3px solid {color};
            border-radius: 8px;
            padding: 8px 4px;
            min-width: 54px;
            flex: 1;
            text-align: center;
        ">
            <span style="font-family: var(--font-mono); font-size: 0.68rem; color: #888888; margin-bottom: 4px;">{time_label}</span>
            <span style="
                background: {bg_tint};
                color: {color};
                font-family: var(--font-sans);
                font-size: 0.64rem;
                font-weight: 700;
                padding: 2px 6px;
                border-radius: 4px;
                text-transform: uppercase;
            ">
                {badge_text}
            </span>
        </div>
        """)

    strip_content = "".join(boxes_html)
    container_html = f"""
    <div style="
        background: #121212;
        border: 1px solid #242424;
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 20px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
            <div style="font-family: var(--font-heading); font-size: 0.88rem; font-weight: 700; color: #FFFFFF;">
                📅 24-Hour Safe Outdoor Timeline
            </div>
            <div style="display: flex; gap: 12px; font-family: var(--font-sans); font-size: 0.72rem;">
                <span style="color: #10B981;">● Green = Safe</span>
                <span style="color: #F59E0B;">● Yellow = Caution</span>
                <span style="color: #EF4444;">● Red = Avoid</span>
            </div>
        </div>
        <div style="display: flex; gap: 6px; overflow-x: auto; padding-bottom: 6px;">
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
        background: #141414;
        border: 1px solid #282828;
        border-left: 3px solid #F59E0B;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 20px;
    ">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span style="font-size: 1.1rem;">{tip_icon}</span>
            <span style="font-family: var(--font-heading); font-size: 0.88rem; font-weight: 700; color: #FFFFFF;">
                Today's Tip: {tip_title}
            </span>
        </div>
        <p style="margin: 0; font-family: var(--font-sans); font-size: 0.86rem; color: #CCCCCC; line-height: 1.5;">
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
            <div style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 4px;">
                🔔 Simple Safety Alerts
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.82rem; color: #888888; margin-bottom: 12px;">
                Set a personal alert level. AirGuard will notify you whenever pollution rises above your comfort line.
            </p>
            """,
            unsafe_allow_html=True
        )

        col_s1, col_s2 = st.columns([2.0, 1.0])

        with col_s1:
            # Map threshold to friendly presets
            presets = {
                "Sensitive (Warn me if air is Moderate or worse)": 35.0,
                "Standard (Warn me if air becomes Unhealthy for sensitive groups)": 55.0,
                "Strict (Warn me at the slightest rise in pollution)": 25.0,
                "High Tolerance (Warn me only during severe pollution)": 80.0
            }

            # Find matching preset key or custom
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
        background: #0E0E0E;
        border: 1px solid #222222;
        border-radius: 8px;
        padding: 12px 18px;
        margin-top: 16px;
        font-family: var(--font-sans);
        font-size: 0.74rem;
        color: #777777;
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
    Renders 3 friendly, large readable weather cards for Simple Mode.
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
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 20px;">
        <div style="background: #121212; border: 1px solid #222222; border-radius: 12px; padding: 16px 20px;">
            <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #888888; text-transform: uppercase; margin-bottom: 6px;">
                🌡️ Outdoor Temperature
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.7rem; font-weight: 800; color: #FFFFFF;">
                {temp_val}
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.78rem; color: #AAAAAA; margin-top: 4px;">
                {temp_note}
            </div>
        </div>

        <div style="background: #121212; border: 1px solid #222222; border-radius: 12px; padding: 16px 20px;">
            <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #888888; text-transform: uppercase; margin-bottom: 6px;">
                💧 Air Moisture (Humidity)
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.7rem; font-weight: 800; color: #FFFFFF;">
                {hum_val}
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.78rem; color: #AAAAAA; margin-top: 4px;">
                {hum_note}
            </div>
        </div>

        <div style="background: #121212; border: 1px solid #222222; border-radius: 12px; padding: 16px 20px;">
            <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #888888; text-transform: uppercase; margin-bottom: 6px;">
                💨 Wind & Ventilation
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.7rem; font-weight: 800; color: #FFFFFF;">
                {wind_val}
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.78rem; color: #AAAAAA; margin-top: 4px;">
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
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 20px;">
        <div style="background: #121212; border: 1px solid #222222; border-left: 4px solid {pm25_color}; border-radius: 12px; padding: 18px 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 700; color: #FFFFFF;">
                    🔬 Tiny Particles (PM₂.₅)
                </span>
                <span style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; color: {pm25_color}; background: rgba(255, 255, 255, 0.05); padding: 2px 8px; border-radius: 4px; border: 1px solid {pm25_color};">
                    ● {pm25_status}
                </span>
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #BBBBBB; margin: 0 0 8px 0; line-height: 1.5;">
                {pm25_desc}
            </p>
            <div style="font-family: var(--font-mono); font-size: 0.74rem; color: #777777;">
                Measured: {pm25:.1f} µg/m³ (particles 30x smaller than a human hair)
            </div>
        </div>

        <div style="background: #121212; border: 1px solid #222222; border-left: 4px solid {pm10_color}; border-radius: 12px; padding: 18px 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 700; color: #FFFFFF;">
                    💨 Coarse Dust & Pollen (PM₁₀)
                </span>
                <span style="font-family: var(--font-sans); font-size: 0.72rem; font-weight: 700; color: {pm10_color}; background: rgba(255, 255, 255, 0.05); padding: 2px 8px; border-radius: 4px; border: 1px solid {pm10_color};">
                    ● {pm10_status}
                </span>
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #BBBBBB; margin: 0 0 8px 0; line-height: 1.5;">
                {pm10_desc}
            </p>
            <div style="font-family: var(--font-mono); font-size: 0.74rem; color: #777777;">
                Measured: {pm10_val:.1f} µg/m³ (road dust, vehicle grit, construction particles)
            </div>
        </div>
    </div>
    """
    safe_markdown(html)


def render_simple_indoor_mask_cards(mask_advice: str, indoor_advice: str) -> None:
    """
    Renders 2 side-by-side cards for Mask guidance and Indoor air protection.
    """
    html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 20px;">
        <div style="background: #121212; border: 1px solid #222222; border-left: 4px solid #38BDF8; border-radius: 12px; padding: 18px 22px;">
            <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 8px;">
                😷 Mask Advice
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #CCCCCC; margin: 0; line-height: 1.5;">
                {mask_advice}
            </p>
        </div>

        <div style="background: #121212; border: 1px solid #222222; border-left: 4px solid #10B981; border-radius: 12px; padding: 18px 22px;">
            <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 8px;">
                🏠 Indoor Air Defense
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #CCCCCC; margin: 0; line-height: 1.5;">
                {indoor_advice}
            </p>
        </div>
    </div>
    """
    safe_markdown(html)

