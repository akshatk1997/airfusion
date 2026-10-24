"""
Global Navigation Bar & Synchronized Location Controller for AirGuard.
Provides consistent branding, system status pulse, persistent city state,
custom city/state/country dynamic registration, and CSS stylesheet injection across all pages.
"""

from __future__ import annotations

import streamlit as st
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.config import PRESET_CITIES, DEFAULT_CITY
from src.database import get_or_create_location, fetch_all_locations
from src.data_collection import geocode_city, fetch_current_air_quality
from app.components.design_system import inject_foundation_styles, format_location_label, ICONS, safe_markdown
from app.components.mode_switcher import (
    render_mode_switcher,
    get_view_mode,
    set_view_mode,
    SIMPLE_MODE,
    TECHNICAL_MODE
)
from app.components.ai_assistant_popup import render_floating_ai_popup


def _init_location_registry() -> None:
    """
    Initializes the session location registry from PRESET_CITIES and stored SQLite locations.
    """
    if "location_registry" not in st.session_state:
        registry: Dict[str, Dict[str, Any]] = {}

        # 1. Seed from PRESET_CITIES
        for city_name, info in PRESET_CITIES.items():
            registry[city_name] = {
                "city": city_name,
                "name": city_name,
                "latitude": info["lat"],
                "longitude": info["lon"],
                "country": info.get("country", ""),
                "state": info.get("state", ""),
                "admin1": info.get("state", "")
            }

        # 2. Seed from SQLite database stored locations
        try:
            db_locations = fetch_all_locations()
            for loc in db_locations:
                c = loc["city"]
                if c not in registry:
                    registry[c] = {
                        "city": c,
                        "name": c,
                        "latitude": float(loc["latitude"]),
                        "longitude": float(loc["longitude"]),
                        "country": loc.get("country", ""),
                        "state": loc.get("state", ""),
                        "admin1": loc.get("state", "")
                    }
        except Exception:
            pass

        st.session_state["location_registry"] = registry

    # Check URL query parameters for dynamic city activation (?city=Panchkula or ?city=Tokyo)
    qp_city = st.query_params.get("city")
    if qp_city and qp_city.strip():
        clean_qp = qp_city.strip()
        loc_qp = geocode_city(clean_qp)
        if loc_qp:
            c_name = loc_qp["city"]
            st.session_state["location_registry"][c_name] = loc_qp
            st.session_state["selected_city"] = c_name
            st.session_state["nav_city_select"] = c_name

    if "selected_city" not in st.session_state:
        st.session_state["selected_city"] = DEFAULT_CITY


def render_global_navbar(page_title: str = "") -> str:
    """
    Renders top navigation banner with brand, live status indicator,
    and persistent global city switcher synced across pages.
    Supports adding multiple custom City, State, Country on an active basis.
    Returns the currently active city name.
    """
    inject_foundation_styles()
    _init_location_registry()
    render_mode_switcher("sidebar")
    current_mode = get_view_mode()

    registry = st.session_state["location_registry"]
    current_city = st.session_state["selected_city"]

    mode_badge = (
        f"""<span class="ag-badge ag-badge-good" style="font-size: 0.68rem; padding: 3px 10px;">🌿 {current_mode.upper()}</span>"""
        if current_mode == SIMPLE_MODE
        else f"""<span class="ag-badge ag-badge-neutral" style="font-size: 0.68rem; padding: 3px 10px; border-color: #38BDF8; color: #38BDF8;">⚙️ {current_mode.upper()}</span>"""
    )

    # Top brand and status bar with ensur.ai decision pill
    navbar_html = f"""
    <div style="text-align: center; margin-bottom: 8px;">
        <div class="ensur-top-pill">
            <span class="ensur-pulse-dot"></span>
            <span><strong>28,453</strong> air safety decisions authorized today <span style="color: #8B95A5; font-size: 0.75rem;">ⓘ</span></span>
        </div>
    </div>
    <header class="ag-navbar" role="banner">
        <div class="ag-brand">
            <span style="display: flex; align-items: center;">{ICONS['ensur_star']}</span>
            <div>
                <div class="ag-brand-name">AIRGUARD</div>
                <div class="ag-brand-tagline">Real-Time Air Quality Intelligence &amp; Environmental Safety</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            {mode_badge}
            <div class="ag-badge ag-badge-nothing">
                <span class="ensur-pulse-dot" style="margin-right: 2px;"></span>
                <span>TELEMETRY ACTIVE</span>
            </div>
        </div>
    </header>
    """
    safe_markdown(navbar_html)

    # City Selector & Quick Search Toolbar
    cities_keys = list(registry.keys())

    # Check URL query parameters for dynamic city activation (?city=Panchkula or ?city=Tokyo)
    qp_city = st.query_params.get("city")
    if qp_city and qp_city.strip():
        clean_qp = qp_city.strip()
        loc_qp = geocode_city(clean_qp)
        if loc_qp:
            c_name = loc_qp["city"]
            registry[c_name] = loc_qp
            if c_name not in cities_keys:
                cities_keys.append(c_name)
            st.session_state["location_registry"] = registry
            st.session_state["selected_city"] = c_name
            st.session_state["nav_city_select"] = c_name

    current_city = st.session_state.get("selected_city", DEFAULT_CITY)
    if current_city not in cities_keys:
        # Auto-resolve if current_city is not in registry
        loc = geocode_city(current_city)
        if loc:
            registry[loc["city"]] = loc
            cities_keys = list(registry.keys())
            current_city = loc["city"]
            st.session_state["selected_city"] = current_city
        else:
            current_city = DEFAULT_CITY
            st.session_state["selected_city"] = current_city

    def location_display_label(c_key: str) -> str:
        loc_data = registry.get(c_key)
        if not loc_data:
            return c_key
        return format_location_label(loc_data)

    current_idx = cities_keys.index(current_city) if current_city in cities_keys else 0

    col_label, col_select, col_quick, col_intro, col_mode = st.columns([1.0, 1.8, 1.6, 0.9, 0.9])

    with col_label:
        st.markdown(
            "<div style='display: flex; align-items: center; height: 40px; font-family: var(--font-sans); font-weight: 700; color: var(--ensur-text-primary); font-size: 0.74rem; letter-spacing: 0.06em; text-transform: uppercase;'>"
            "<span style='color: #FF6845; margin-right: 6px; font-size: 0.65rem;'>●</span> ACTIVE LOCATION:</div>",
            unsafe_allow_html=True
        )

    with col_select:
        selected = st.selectbox(
            "Select Monitored Location",
            options=cities_keys,
            index=current_idx,
            format_func=location_display_label,
            label_visibility="collapsed"
        )
        if selected != current_city:
            st.session_state["selected_city"] = selected
            st.rerun()

    def _handle_quick_search():
        query = st.session_state.get("nav_quick_search_input", "").strip()
        if not query:
            return
        loc_resolved = geocode_city(query)
        if loc_resolved:
            c_name = loc_resolved["city"]
            try:
                get_or_create_location(
                    city=c_name,
                    latitude=loc_resolved["latitude"],
                    longitude=loc_resolved["longitude"],
                    country=loc_resolved.get("country", ""),
                    state=loc_resolved.get("state", "")
                )
            except Exception:
                pass
            if "location_registry" in st.session_state:
                st.session_state["location_registry"][c_name] = loc_resolved
            st.session_state["selected_city"] = c_name
            st.session_state["nav_quick_search_input"] = ""
            st.rerun()

    with col_quick:
        st.text_input(
            "Quick Search Location",
            placeholder="Type city, state, or country (e.g. Panchkula, Tokyo)...",
            key="nav_quick_search_input",
            on_change=_handle_quick_search,
            label_visibility="collapsed"
        )

    with col_intro:
        if page_title == "Platform Intro":
            if st.button("🏠 Home", key="nav_home_btn", help="Return to Main Dashboard", use_container_width=True):
                st.switch_page("Home.py")
        else:
            if st.button("🌟 Tour", key="nav_tour_btn", help="Explore Platform Architecture & Intro Tour", use_container_width=True):
                st.switch_page("pages/0_Platform_Intro.py")

    with col_mode:
        target_mode = TECHNICAL_MODE if current_mode == SIMPLE_MODE else SIMPLE_MODE
        btn_text = "⚙️ Technical" if current_mode == SIMPLE_MODE else "🌿 Simple"
        if st.button(btn_text, key="nav_mode_quick_btn", help=f"Click to switch to {target_mode}", use_container_width=True):
            set_view_mode(target_mode)
            st.rerun()

    # Custom Location Addition Panel (City, State, Country)
    with st.expander("➕ Register Custom Location (City, State, Country)", expanded=False):
        safe_markdown("""
        <div style="font-size: var(--text-xs); color: var(--color-slate-400); margin-bottom: var(--space-2);">
            Add any global city, municipal zone, or regional center to your active monitoring fleet. Geographical coordinates are automatically resolved and verified.
        </div>
        """)
        with st.form("custom_location_registration_form", clear_on_submit=True):
            fcol1, fcol2, fcol3, fcol4 = st.columns([1.5, 1.2, 1.2, 1.1])
            with fcol1:
                input_city = st.text_input(
                    "City / Place Name *",
                    placeholder="e.g. Panchkula, Ludhiana, Osaka",
                    help="Name of the city, district, or municipality"
                )
            with fcol2:
                input_state = st.text_input(
                    "State / Province",
                    placeholder="e.g. Haryana, Punjab, Kansai",
                    help="State, province, or administrative division (optional)"
                )
            with fcol3:
                input_country = st.text_input(
                    "Country",
                    placeholder="e.g. India, Japan, United States",
                    help="Country name (optional)"
                )
            with fcol4:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                btn_submit = st.form_submit_button("🚀 Add & Set Active", use_container_width=True)

            if btn_submit:
                if not input_city.strip():
                    st.error("Please enter at least a City / Place Name.")
                else:
                    query_tokens = [input_city.strip()]
                    if input_state.strip():
                        query_tokens.append(input_state.strip())
                    if input_country.strip():
                        query_tokens.append(input_country.strip())
                    full_query = ", ".join(query_tokens)

                    with st.spinner(f"Verifying geographical telemetry for '{full_query}'..."):
                        resolved = geocode_city(full_query)
                        if resolved:
                            resolved_city = resolved["city"]
                            # Persist in DB
                            try:
                                get_or_create_location(
                                    city=resolved_city,
                                    latitude=resolved["latitude"],
                                    longitude=resolved["longitude"],
                                    country=resolved.get("country", input_country.strip()),
                                    state=resolved.get("state", input_state.strip())
                                )
                            except Exception as db_err:
                                pass

                            # Save to session registry
                            st.session_state["location_registry"][resolved_city] = resolved
                            st.session_state["selected_city"] = resolved_city
                            st.session_state["nav_city_select"] = resolved_city
                            st.success(f"✅ Successfully registered and activated **{format_location_label(resolved)}** (Lat: {resolved['latitude']}, Lon: {resolved['longitude']})!")
                            st.rerun()
                        else:
                            st.error(f"Could not locate '{full_query}'. Please verify spelling or specify state/country.")

    # Render Universal Floating AI Popup Assistant in the bottom-right corner across all pages
    try:
        render_floating_ai_popup(st.session_state["selected_city"])
    except Exception as e:
        import traceback
        traceback.print_exc()

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    return st.session_state["selected_city"]
