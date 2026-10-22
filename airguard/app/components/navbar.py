"""
Global Navigation Bar & Synchronized Location Controller for AirGuard.
Provides consistent branding, system status pulse, persistent city state,
and CSS stylesheet injection across all pages.
"""

from __future__ import annotations

import streamlit as st
from pathlib import Path
from typing import Tuple
from src.config import PRESET_CITIES, DEFAULT_CITY
from app.components.design_system import inject_foundation_styles, ICONS, safe_markdown

def render_global_navbar(page_title: str = "") -> str:
    """
    Renders top navigation banner with brand, live status indicator,
    and persistent global city switcher synced across pages.
    Returns the currently active city.
    """
    inject_foundation_styles()

    # Initialize session state for city
    if "selected_city" not in st.session_state:
        st.session_state["selected_city"] = DEFAULT_CITY

    cities_list = list(PRESET_CITIES.keys())
    current_city = st.session_state["selected_city"]

    # Top brand and status bar
    navbar_html = f"""
    <header class="ag-navbar" role="banner">
        <div class="ag-brand">
            <span style="color: var(--color-brand-cyan); display: flex; align-items: center;">{ICONS['shield']}</span>
            <div>
                <div class="ag-brand-name">AIRGUARD</div>
                <div class="ag-brand-tagline">Real-Time Air Quality Intelligence & Forecasting</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 14px;">
            <div class="ag-badge ag-badge-good">
                <span class="ag-pulse-dot" aria-hidden="true"></span>
                <span>TELEMETRY ACTIVE</span>
            </div>
        </div>
    </header>
    """
    safe_markdown(navbar_html)

    # City Selector bar (Persistent location switcher)
    col_label, col_select, col_custom = st.columns([1.2, 2.2, 2.6])
    
    with col_label:
        st.markdown(
            f"<div style='padding-top: 8px; font-weight: 700; color: #94A3B8; font-size: 0.85rem;'>"
            f"📍 ACTIVE LOCATION:</div>",
            unsafe_allow_html=True
        )

    with col_select:
        current_idx = cities_list.index(current_city) if current_city in cities_list else 0
        new_selection = st.selectbox(
            "Select Location",
            options=["-- Custom City Search --"] + cities_list,
            index=current_idx + 1 if current_city in cities_list else 0,
            key="nav_city_select",
            label_visibility="collapsed"
        )

    with col_custom:
        if new_selection == "-- Custom City Search --":
            custom_input = st.text_input(
                "Enter Custom City",
                value="" if current_city in cities_list else current_city,
                placeholder="Type any city (e.g. Kharar, Mohali, Paris)...",
                key="nav_custom_input",
                label_visibility="collapsed"
            )
            if custom_input.strip() and custom_input.strip() != current_city:
                st.session_state["selected_city"] = custom_input.strip().title()
                st.rerun()
        else:
            if new_selection != current_city:
                st.session_state["selected_city"] = new_selection
                st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    return st.session_state["selected_city"]
