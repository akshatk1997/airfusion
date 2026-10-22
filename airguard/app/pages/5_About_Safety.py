"""
Safety Protocols, Health Cohorts & Architectural Blueprint for AirGuard.
Features:
- Clinical & Non-Medical Health Cohort Guidance (Asthma, Children, Seniors, Pregnancy, Runners)
- N95/KN95 Mask Standards & Proper Seal Guide
- Indoor Air Defense Protocols (HEPA Filtration, Sealed Windows, HVAC Recirculation)
- Full Technical Architecture, Open-Meteo Attribution & Safety Disclaimers
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PRESET_CITIES
from src.predict import is_model_trained
from app.components.navbar import render_global_navbar
from app.components.mode_switcher import is_simple_mode, render_mode_banner
from app.components.simple_views import render_simple_about_safety
from app.components.design_system import (
    render_section_header,
    render_metric_tile,
    render_callout,
    render_badge,
    safe_markdown,
    ICONS
)

st.set_page_config(
    page_title="About & Safety Protocols — AirGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Global Navbar
_ = render_global_navbar("About & Safety")

# Render Mode Notification Banner
render_mode_banner()

if is_simple_mode():
    render_simple_about_safety()
    st.stop()

# Page Header
render_section_header(
    title="Health Safety Protocols & Architectural Blueprint",
    subtitle="Cohort-specific environmental guidance, certified respiratory defense, indoor air protocols, and open-source system architecture.",
    badge="HEALTH PROTOCOLS & BLUEPRINT"
)

# Top Action Toolbar
tb_col1, tb_col2 = st.columns([1.6, 1.6])
with tb_col2:
    btn1, btn2, btn3 = st.columns(3)
    with btn1:
        if st.button("🛡️ Safe Plan", use_container_width=True):
            st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")
    with btn2:
        if st.button("📡 Live Tracking", use_container_width=True):
            st.switch_page("pages/2_Live_Tracking.py")
    with btn3:
        if st.button("📊 Trends", use_container_width=True):
            st.switch_page("pages/3_Trends.py")

# Prominent Medical Disclaimer Banner
safe_markdown(
    """
    <div class="ag-card" style="border: 1px solid #D71921; background: rgba(215, 25, 33, 0.05); padding: var(--space-4); margin-bottom: var(--space-4);">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span style="font-family: var(--font-heading); font-size: 0.78rem; font-weight: 700; color: #D71921;">
                ⚠️ GENERAL ENVIRONMENTAL SAFETY DISCLAIMER
            </span>
        </div>
        <div style="font-family: var(--font-sans); font-size: 0.86rem; color: #E5E5E5; line-height: 1.6;">
            <strong>This app provides general environmental safety guidance. It does not provide medical diagnosis or treatment.</strong><br>
            All recommendations, risk scores, safe outdoor windows, and precautions are generated based on mathematical models and ambient environmental observations. If you suffer from asthma, COPD, cardiovascular conditions, or other medical sensitivities, always prioritize your licensed physician's guidance and carry prescribed reliever medication as instructed.
        </div>
    </div>
    """
)

# Navigation Tabs
tab_cohorts, tab_masks, tab_indoor, tab_arch = st.tabs([
    "👥 Health Cohorts & Risk Profiles",
    "😷 Respiratory Mask Standards",
    "🏠 Indoor Air Defense Protocols",
    "⚙️ System Architecture & Data Sources"
])

# ----------------- TAB 1: HEALTH COHORTS & RISK PROFILES -----------------
with tab_cohorts:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    safe_markdown(
        """
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px;">
            <div class="ag-card" style="border: 1px solid #242424; background: #0E0E0E; padding: var(--space-4);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Asthma & Respiratory Allergies</span>
                    <span class="ag-badge ag-badge-nothing" style="color: #D71921;">HIGH SENSITIVITY</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #AAAAAA; line-height: 1.6;">
                    Fine particulates (PM₂.₅) penetrate deep into the bronchial tree, triggering hyper-responsiveness, bronchospasm, and acute flare-ups.
                    <br><br>
                    <strong>Guidance:</strong> Keep outdoor exertion under 30 minutes when PM₂.₅ exceeds 35 µg/m³. Always carry prescribed rescue inhalers. Wear a sealed N95/KN95 mask if outdoor transit is unavoidable.
                </div>
            </div>

            <div class="ag-card" style="border: 1px solid #242424; background: #0E0E0E; padding: var(--space-4);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Children & Young Dependents</span>
                    <span class="ag-badge ag-badge-nothing" style="color: #EAB308;">DEVELOPING LUNGS</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #AAAAAA; line-height: 1.6;">
                    Children breathe 50% more air per pound of body weight than adults and have narrower airways and developing immune defense systems.
                    <br><br>
                    <strong>Guidance:</strong> Relocate school recess and sports indoors when AQI exceeds 100. Choose early morning safe windows (06:00–08:00) before photochemical smog develops.
                </div>
            </div>

            <div class="ag-card" style="border: 1px solid #242424; background: #0E0E0E; padding: var(--space-4);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Senior Citizens (65+)</span>
                    <span class="ag-badge ag-badge-nothing" style="color: #EAB308;">VULNERABLE</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #AAAAAA; line-height: 1.6;">
                    Elevated particulate exposure triggers systemic vascular inflammation, arterial stiffness, and increases ischemic cardiac events.
                    <br><br>
                    <strong>Guidance:</strong> Prefer gentle indoor walking during high-pollution episodes. Avoid morning traffic corridors where diesel soot (elemental carbon) is concentrated.
                </div>
            </div>

            <div class="ag-card" style="border: 1px solid #242424; background: #0E0E0E; padding: var(--space-4);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Athletes & Outdoor Runners</span>
                    <span class="ag-badge ag-badge-nothing">HIGH VENTILATION</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #AAAAAA; line-height: 1.6;">
                    During vigorous running or cycling, minute ventilation surges from 6 L/min to over 60 L/min, shifting breathing from nasal filtration to mouth breathing.
                    <br><br>
                    <strong>Guidance:</strong> Check the Safe Outdoor Window Finder before training. Avoid evening rush hour (17:00–21:00) when inversion layers trap vehicle emissions.
                </div>
            </div>
        </div>
        """
    )

# ----------------- TAB 2: RESPIRATORY MASK STANDARDS -----------------
with tab_masks:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    safe_markdown(
        """
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
            <div class="ag-card" style="border: 1px solid #242424; background: #0E0E0E; padding: var(--space-4);">
                <div style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                    N95 / KN95 / FFP2 Respirators
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #22C55E; margin-bottom: 12px;">RECOMMENDED STANDARD (≥95% FILTRATION)</div>
                <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #AAAAAA; line-height: 1.6;">
                    Electrostatic meltblown filter layers capture sub-micron particles down to 0.1 µm. Requires a tight facial seal without air leaks around the bridge of the nose.
                    <br><br>
                    <strong>Best for:</strong> Commuting, walking, or essential outdoor presence when PM₂.₅ > 55 µg/m³.
                </div>
            </div>

            <div class="ag-card" style="border: 1px solid #242424; background: #0E0E0E; padding: var(--space-4);">
                <div style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                    Surgical 3-Ply Masks
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #EAB308; margin-bottom: 12px;">PARTIAL BENEFIT (30–50% LEAKAGE)</div>
                <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #AAAAAA; line-height: 1.6;">
                    Captures large respiratory droplets and coarse dust (PM₁₀), but loose perimeter gaps permit ambient PM₂.₅ aerosols to bypass the filter media entirely.
                    <br><br>
                    <strong>Best for:</strong> Emergency barrier only when certified respirators are unavailable.
                </div>
            </div>

            <div class="ag-card" style="border: 1px solid #242424; background: #0E0E0E; padding: var(--space-4);">
                <div style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                    Cloth Bandanas & Fabric Covers
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #D71921; margin-bottom: 12px;">INEFFECTIVE AGAINST PM₂.₅ (&lt;15% EFFICIENCY)</div>
                <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #AAAAAA; line-height: 1.6;">
                    Woven cotton weaves have pore sizes exceeding 50–200 µm, offering zero physical resistance against combustion particles and hazardous toxic chemicals.
                    <br><br>
                    <strong>Notice:</strong> Do not rely on fabric masks during severe pollution or smog events.
                </div>
            </div>
        </div>
        """
    )

# ----------------- TAB 3: INDOOR AIR DEFENSE PROTOCOLS -----------------
with tab_indoor:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    safe_markdown(
        """
        <div class="ag-card" style="border: 1px solid #242424; background: #0E0E0E; padding: var(--space-5);">
            <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-bottom: 14px;">
                Indoor Clean Air Sanctuary Checklist
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; font-family: var(--font-sans); font-size: 0.85rem; color: #BBBBBB; line-height: 1.6;">
                <div>
                    <strong style="color: #FFFFFF;">1. True HEPA Air Purification:</strong><br>
                    Operate a mechanical H13/H14 HEPA purifier in the bedroom and living spaces. Ensure the Clean Air Delivery Rate (CADR) matches the room volume with 4 to 5 air changes per hour (ACH).
                </div>
                <div>
                    <strong style="color: #FFFFFF;">2. Window & Door Sealing:</strong><br>
                    Keep exterior windows tightly shut during morning and evening stagnation inversions (07:00–10:00 and 18:00–22:00). Use rubber weather stripping on frame gaps.
                </div>
                <div>
                    <strong style="color: #FFFFFF;">3. HVAC Recirculation Mode:</strong><br>
                    In vehicles and buildings equipped with central air conditioning, ensure the system is set to internal recirculation mode to prevent drawing contaminated street air inside.
                </div>
                <div>
                    <strong style="color: #FFFFFF;">4. Eliminate Indoor Combustion:</strong><br>
                    Avoid burning incense, mosquito coils, candles, or indoor fireplaces during high AQI days. Use kitchen exhaust hoods during cooking to prevent fine oil mist accumulation.
                </div>
            </div>
        </div>
        """
    )

# ----------------- TAB 4: SYSTEM ARCHITECTURE & DATA SOURCES -----------------
with tab_arch:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    safe_markdown(
        """
        <div class="ag-card" style="border: 1px solid #242424; background: #0E0E0E; padding: var(--space-5);">
            <div style="font-family: var(--font-heading); font-size: 1.2rem; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;">
                Open Environmental Tech Architecture
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.88rem; color: #AAAAAA; line-height: 1.7;">
                <p>
                    AirGuard is an autonomous, open environmental intelligence platform built with Python 3.10+, Streamlit, Scikit-learn, XGBoost, and SQLite.
                </p>
                <ul>
                    <li><strong>Live Air Quality & Weather Ingestion:</strong> Ingests continuous boundary layer meteorology and atmospheric particulate concentrations via the free, open-access <strong>Open-Meteo Air Quality & Weather APIs</strong>.</li>
                    <li><strong>Autoregressive ML Forecaster:</strong> Sequential lag feature engineering (1h–24h) and rolling statistics (3h–24h) powering an XGBoost champion regressor with expanding confidence bands.</li>
                    <li><strong>Transparent Risk Engine:</strong> Multi-factor composite weighting that factors health sensitivity, age vulnerability, outdoor activity intensity, and continuous exposure duration.</li>
                    <li><strong>Local Privacy-Preserving Storage:</strong> SQLite Write-Ahead Logging (WAL) stores historical telemetry and user health profiles locally without transmitting sensitive personal records to third-party servers.</li>
                </ul>
            </div>
        </div>
        """
    )
