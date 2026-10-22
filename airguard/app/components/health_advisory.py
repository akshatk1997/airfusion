"""
Health Advisory and Clinical Safety Guidance Component for AirGuard.
Renders practical, medical/public health recommendations based on current or forecasted AQI.
"""

from __future__ import annotations

import streamlit as st
from src.alerts import get_health_advisory
from app.components.cards import get_aqi_badge_style
from app.components.design_system import safe_markdown


def render_health_advisory_panel(aqi: int) -> None:
    """
    Renders structured health guidance cards for outdoor exercise, masks,
    ventilation, and sensitive groups.
    """
    advisory = get_health_advisory(aqi)
    category = advisory["category"]
    description = advisory["description"]
    advice = advisory["advice"]
    theme = get_aqi_badge_style(aqi)

    # Header Card
    safe_markdown(f"""
    <div style="
        background: {theme['gradient']};
        border-left: 6px solid {theme['border']};
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.4);
    ">
        <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
            <span style="
                background: {theme['bg']};
                border: 1px solid {theme['border']};
                color: {theme['text']};
                font-weight: 700;
                font-size: 0.82rem;
                padding: 4px 12px;
                border-radius: 9999px;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            ">
                ● {category} (AQI {aqi})
            </span>
            <span style="font-weight: 700; color: #F8FAFC; font-size: 1.15rem; letter-spacing: -0.01em;">
                Clinical Health Guidance & Preventive Protocol
            </span>
        </div>
        <p style="margin: 10px 0 0 0; color: #E2E8F0; font-size: 0.95rem; line-height: 1.5;">
            {description}
        </p>
    </div>
    """)

    # 4-Column Actionable Protocol Cards
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        safe_markdown(f"""
        <div class="ag-health-card">
            <div class="ag-health-icon">🏃</div>
            <div class="ag-health-title">Outdoor Physical Activity</div>
            <div class="ag-health-desc">{advice.get('exercise', 'Standard precautions.')}</div>
        </div>
        """)

    with col2:
        safe_markdown(f"""
        <div class="ag-health-card">
            <div class="ag-health-icon">😷</div>
            <div class="ag-health-title">Respiratory & Mask Guidance</div>
            <div class="ag-health-desc">{advice.get('mask', 'No mask required.')}</div>
        </div>
        """)

    with col3:
        safe_markdown(f"""
        <div class="ag-health-card" style="margin-top: 12px;">
            <div class="ag-health-icon">🪟</div>
            <div class="ag-health-title">Indoor Ventilation & Air Filters</div>
            <div class="ag-health-desc">{advice.get('ventilation', 'Standard natural ventilation.')}</div>
        </div>
        """)

    with col4:
        safe_markdown(f"""
        <div class="ag-health-card" style="margin-top: 12px;">
            <div class="ag-health-icon">🩺</div>
            <div class="ag-health-title">Sensitive Groups Protocol</div>
            <div class="ag-health-desc">{advice.get('sensitive', 'No special precautions required.')}</div>
        </div>
        """)
