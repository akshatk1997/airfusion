"""
Activity Advisor UI Component for AirGuard — My Safe Outdoor Plan.
Renders optimal safe outdoor windows, avoid periods, alternative recommendations,
and discrete hourly timeline status strips.
"""

from __future__ import annotations

import streamlit as st
from typing import Dict, Any, List, Optional
from app.components.design_system import safe_markdown


def render_safe_window_card(
    window_data: Dict[str, Any],
    activity: str,
    duration_mins: int
) -> None:
    """
    Renders optimal safe outdoor window and avoid periods in Nothing OS style.
    """
    best_win = window_data.get("best_window", "Now")
    best_pm25 = window_data.get("best_window_pm25", 0.0)
    best_aqi = window_data.get("best_window_aqi", 0)
    best_cat = window_data.get("best_window_category", "Moderate")
    avoid_list = window_data.get("avoid_periods", [])
    alt = window_data.get("alternative_window")
    is_safe = window_data.get("is_preferred_safe", True)

    win_color = "#10B981" if is_safe else "#F97316"
    win_bg = "rgba(16, 185, 129, 0.1)" if is_safe else "rgba(249, 115, 22, 0.1)"

    avoid_html = ""
    if avoid_list:
        avoid_items = "".join([f"<li>{item}</li>" for item in avoid_list])
        avoid_html = f"""
        <div style="margin-top: 14px; padding: 12px 16px; background: rgba(215, 25, 33, 0.08); border: 1px solid rgba(215, 25, 33, 0.3); border-radius: 10px;">
            <div style="font-family: var(--font-dot); font-size: 0.75rem; font-weight: 700; color: #D71921; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;">
                ⚠️ Unsafe Exposure Periods to Avoid
            </div>
            <ul style="margin: 0; padding-left: 20px; font-family: var(--font-sans); font-size: 0.8rem; color: #E5E5E5; line-height: 1.5;">
                {avoid_items}
            </ul>
        </div>
        """

    alt_html = ""
    if alt:
        alt_html = f"""
        <div style="margin-top: 12px; padding: 12px 16px; background: #181818; border-left: 3px solid #10B981; border-radius: 8px;">
            <div style="font-family: var(--font-dot); font-size: 0.75rem; font-weight: 700; color: #10B981; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px;">
                💡 Recommended Cleaner Alternative
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #CCCCCC;">
                {alt['note']}
            </div>
        </div>
        """

    html = f"""
    <div style="
        background: #121212;
        border: 1px solid #242424;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="
                        background: {win_bg};
                        border: 1px solid {win_color};
                        color: {win_color};
                        font-family: var(--font-dot);
                        font-size: 0.72rem;
                        font-weight: 700;
                        padding: 2px 10px;
                        border-radius: 9999px;
                        letter-spacing: 0.08em;
                        text-transform: uppercase;
                    ">
                        ● Window Finder
                    </span>
                    <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #777777; text-transform: uppercase;">
                        {duration_mins}-Minute {activity.title()}
                    </span>
                </div>
                <div style="font-family: var(--font-heading); font-size: 1.55rem; font-weight: 700; color: #FFFFFF; line-height: 1.3;">
                    Best Window: <span style="color: {win_color};">{best_win}</span>
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.8rem; color: #888888; margin-top: 4px;">
                    Forecasted PM₂.₅: <b style="color: #FFFFFF;">{best_pm25:.1f} µg/m³</b> (AQI {best_aqi}, {best_cat})
                </div>
            </div>
        </div>

        {alt_html}
        {avoid_html}
    </div>
    """
    safe_markdown(html)


def render_hourly_timeline_strip(hourly_timeline: List[Dict[str, Any]]) -> None:
    """
    Renders discrete 24-hour visual safe/caution/avoid timeline boxes.
    """
    if not hourly_timeline:
        return

    boxes_html = []
    for item in hourly_timeline[:24]:
        time_label = item["time"]
        status = item["status"]
        color = item["color"]
        pm25 = item["pm25"]

        boxes_html.append(f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #161616;
            border: 1px solid #282828;
            border-top: 3px solid {color};
            border-radius: 8px;
            padding: 8px 4px;
            min-width: 58px;
            flex: 1;
            text-align: center;
        ">
            <span style="font-family: var(--font-mono); font-size: 0.68rem; color: #888888; margin-bottom: 4px;">{time_label}</span>
            <span style="font-family: var(--font-dot); font-size: 0.85rem; font-weight: 700; color: #FFFFFF;">{pm25:.0f}</span>
            <span style="font-family: var(--font-sans); font-size: 0.62rem; color: {color}; font-weight: 700; text-transform: uppercase; margin-top: 4px;">{status}</span>
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
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <div style="font-family: var(--font-dot); font-size: 0.78rem; font-weight: 700; color: #FFFFFF; text-transform: uppercase; letter-spacing: 0.08em;">
                📅 24-Hour Outdoor Safety Trajectory Timeline
            </div>
            <div style="display: flex; gap: 12px; font-family: var(--font-mono); font-size: 0.68rem;">
                <span style="color: #10B981;">● Safe</span>
                <span style="color: #F59E0B;">● Caution</span>
                <span style="color: #EF4444;">● Avoid</span>
            </div>
        </div>
        <div style="display: flex; gap: 6px; overflow-x: auto; padding-bottom: 6px;">
            {strip_content}
        </div>
    </div>
    """
    safe_markdown(container_html)
