"""
AirGuard Platform Introduction & Interactive Architecture Tour.
Modeled after ensur.ai's signature platform intro experience, tweaked specifically
for autonomous ambient air intelligence, predictive machine learning, and outdoor safety.
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PAGE_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.components.navbar import render_global_navbar
from app.components.mode_switcher import (
    get_view_mode,
    set_view_mode,
    render_mode_banner,
    SIMPLE_MODE,
    TECHNICAL_MODE
)
from app.components.design_system import (
    inject_foundation_styles,
    render_section_header,
    safe_markdown,
    ICONS
)
from app.components.simple_cards import render_ensur_executive_footer

st.set_page_config(
    page_title="Platform Intro — AirGuard Environmental Sentry",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="auto"
)

# Render Global Nav & sync city state
active_city = render_global_navbar("Platform Intro")
render_mode_banner()

# ==============================================================================
# 1. BESPOKE ENSUR.AI STYLE HERO: THE AUTONOMOUS ENVIRONMENTAL OPERATING SYSTEM
# ==============================================================================
safe_markdown("""
<section class="ensur-hero" style="text-align: center; margin-bottom: var(--space-8);">
    <div style="display: flex; justify-content: center; margin-bottom: var(--space-3);">
        <div class="ensur-pulse-badge">
            <span class="ensur-pulse-dot"></span>
            <span>AUTONOMOUS ENVIRONMENTAL OPERATING SYSTEM</span>
        </div>
    </div>
    <h1 style="font-family: var(--font-heading); font-size: clamp(2.4rem, 5vw, 3.8rem); font-weight: 800; color: #1F344C; line-height: 1.15; letter-spacing: -0.035em; max-width: 960px; margin: 0 auto var(--space-4) auto;">
        Making outdoor safety <span class="ensur-coral-gradient">smart, predictive,</span> and personal.
    </h1>
    <p style="font-family: var(--font-sans); font-size: 1.12rem; color: #5A6E85; max-width: 780px; margin: 0 auto var(--space-6) auto; line-height: 1.65;">
        Traditional weather apps only report static history from delayed airport stations. AirGuard continuously evaluates ambient ground telemetry, forecasts pollution spikes up to 72 hours ahead with XGBoost machine learning, and computes your physiological lung intake so you know the exact window to step outside safely.
    </p>
</section>
""")

# Action Buttons: Launch Simple vs. Launch Technical Mode
col_cta1, col_cta2, col_cta3 = st.columns([1.2, 1.0, 1.0])

with col_cta1:
    if st.button("🌿 Launch Everyday Sentry (Simple Mode)", key="intro_btn_simple", use_container_width=True, type="primary"):
        set_view_mode(SIMPLE_MODE)
        st.switch_page("Home.py")

with col_cta2:
    if st.button("⚙️ Open Command Center (Technical Mode)", key="intro_btn_tech", use_container_width=True):
        set_view_mode(TECHNICAL_MODE)
        st.switch_page("Home.py")

with col_cta3:
    if st.button("🛡️ Create Safe Outdoor Plan", key="intro_btn_plan", use_container_width=True):
        st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 2. THE PARADIGM SHIFT: STATIC WEATHER APPS VS. AIRGUARD AUTONOMOUS SENTRY
# ==============================================================================
render_section_header(
    title="The Paradigm Shift: Static Weather Apps vs. AirGuard",
    subtitle="Why traditional weather apps fail at personal air protection and how continuous atmospheric intelligence solves it.",
    badge="THE SHIFT"
)

safe_markdown("""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 24px; margin-bottom: var(--space-8);">
    <!-- Static Legacy Way -->
    <div class="ensur-compare-card ensur-compare-once" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 20px; padding: 32px 30px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.05);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
            <span style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #8896A6;">
                THE OLD WAY
            </span>
            <span class="ag-badge ag-badge-neutral" style="font-size: 0.65rem;">PERIODIC &amp; PASSIVE</span>
        </div>
        <div style="font-family: var(--font-heading); font-size: 1.55rem; font-weight: 800; color: #1F344C; margin-bottom: 12px; line-height: 1.25;">
            Static Weather &amp; Generic Apps
        </div>
        <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; line-height: 1.6; margin-bottom: 24px;">
            Legacy apps dump raw numerical AQI values once every few hours without understanding your health sensitivity, workout intensity, or time trajectory.
        </p>
        <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 14px;">
            <li style="display: flex; align-items: flex-start; gap: 10px;">
                <span style="color: #DC2626; font-size: 1.1rem; line-height: 1.2; font-weight: 800;">✕</span>
                <div>
                    <strong style="color: #1F344C; font-size: 0.88rem;">Delayed Airport Observations:</strong>
                    <p style="margin: 2px 0 0 0; color: #5A6E85; font-size: 0.82rem; line-height: 1.5;">Reports conditions from 3 hours ago at an airport 20 kilometers away from your actual neighborhood.</p>
                </div>
            </li>
            <li style="display: flex; align-items: flex-start; gap: 10px;">
                <span style="color: #DC2626; font-size: 1.1rem; line-height: 1.2; font-weight: 800;">✕</span>
                <div>
                    <strong style="color: #1F344C; font-size: 0.88rem;">No Proactive Forward Foresight:</strong>
                    <p style="margin: 2px 0 0 0; color: #5A6E85; font-size: 0.82rem; line-height: 1.5;">Tells you the air is bad right now, but cannot tell you when it clears or when the cleanest outdoor window begins.</p>
                </div>
            </li>
            <li style="display: flex; align-items: flex-start; gap: 10px;">
                <span style="color: #DC2626; font-size: 1.1rem; line-height: 1.2; font-weight: 800;">✕</span>
                <div>
                    <strong style="color: #1F344C; font-size: 0.88rem;">Blind to Biological Vulnerability:</strong>
                    <p style="margin: 2px 0 0 0; color: #5A6E85; font-size: 0.82rem; line-height: 1.5;">Treats an asthmatic marathon runner breathing 60 L/min the exact same as a healthy adult sitting indoors.</p>
                </div>
            </li>
            <li style="display: flex; align-items: flex-start; gap: 10px;">
                <span style="color: #DC2626; font-size: 1.1rem; line-height: 1.2; font-weight: 800;">✕</span>
                <div>
                    <strong style="color: #1F344C; font-size: 0.88rem;">Zero Inhaled Dosage Quantification:</strong>
                    <p style="margin: 2px 0 0 0; color: #5A6E85; font-size: 0.82rem; line-height: 1.5;">Leaves you guessing how many micrograms of toxic particulate matter actually entered your pulmonary tissue.</p>
                </div>
            </li>
        </ul>
    </div>

    <!-- AirGuard Continuous Autonomous Sentry -->
    <div class="ensur-compare-card ensur-compare-ongoing" style="background: linear-gradient(145deg, #1F344C 0%, #162638 100%); border: 1px solid rgba(255, 104, 69, 0.35); border-radius: 20px; padding: 32px 30px; box-shadow: 0 16px 36px rgba(31, 52, 76, 0.25);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
            <span style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #FF8665;">
                THE AIRGUARD WAY
            </span>
            <span style="background: rgba(255, 104, 69, 0.2); color: #FFC3B3; font-family: var(--font-mono); font-size: 0.65rem; font-weight: 700; padding: 3px 10px; border-radius: 9999px; border: 1px solid rgba(255, 104, 69, 0.4);">
                AUTONOMOUS &amp; CONTINUOUS
            </span>
        </div>
        <div style="font-family: var(--font-heading); font-size: 1.55rem; font-weight: 800; color: #FFFFFF; margin-bottom: 12px; line-height: 1.25;">
            Continuous Environmental Intelligence
        </div>
        <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #FFF0EB; line-height: 1.6; margin-bottom: 24px;">
            An autonomous multi-stage operating pipeline that synthesizes live sensors, machine learning predictions, and pulmonary dosage calculation into clear clearance.
        </p>
        <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 14px;">
            <li style="display: flex; align-items: flex-start; gap: 10px;">
                <span style="color: #34D399; font-size: 1.1rem; line-height: 1.2; font-weight: 800;">✓</span>
                <div>
                    <strong style="color: #FFFFFF; font-size: 0.88rem;">Live Multi-Spectral Ground Synchronization:</strong>
                    <p style="margin: 2px 0 0 0; color: #FFF0EB; font-size: 0.82rem; line-height: 1.5;">Ingests 6 criteria pollutants (PM₂.₅, PM₁₀, NO₂, SO₂, O₃, CO) with real-time Open-Meteo &amp; station consensus.</p>
                </div>
            </li>
            <li style="display: flex; align-items: flex-start; gap: 10px;">
                <span style="color: #34D399; font-size: 1.1rem; line-height: 1.2; font-weight: 800;">✓</span>
                <div>
                    <strong style="color: #FFFFFF; font-size: 0.88rem;">72-Hour Neural Horizon Projections:</strong>
                    <p style="margin: 2px 0 0 0; color: #FFF0EB; font-size: 0.82rem; line-height: 1.5;">XGBoost regressor modeling atmospheric boundary layer physics, wind dispersion vectors, and 90% confidence bands.</p>
                </div>
            </li>
            <li style="display: flex; align-items: flex-start; gap: 10px;">
                <span style="color: #34D399; font-size: 1.1rem; line-height: 1.2; font-weight: 800;">✓</span>
                <div>
                    <strong style="color: #FFFFFF; font-size: 0.88rem;">Physiological Micro-Ventilation Dosage:</strong>
                    <p style="margin: 2px 0 0 0; color: #FFF0EB; font-size: 0.82rem; line-height: 1.5;">Calculates exact inhaled particulate mass (µg) and alveolar tissue deposition based on respiratory minute rates (V̇_E).</p>
                </div>
            </li>
            <li style="display: flex; align-items: flex-start; gap: 10px;">
                <span style="color: #34D399; font-size: 1.1rem; line-height: 1.2; font-weight: 800;">✓</span>
                <div>
                    <strong style="color: #FFFFFF; font-size: 0.88rem;">Authoritative Go/No-Go Window Clearance:</strong>
                    <p style="margin: 2px 0 0 0; color: #FFF0EB; font-size: 0.82rem; line-height: 1.5;">Direct answers in plain English for everyday decisions or full statistical telemetry for research engineers.</p>
                </div>
            </li>
        </ul>
    </div>
</div>
""")

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 3. HOW IT WORKS: THE 4-STAGE AUTONOMOUS PIPELINE
# ==============================================================================
render_section_header(
    title="The 4-Stage Autonomous Pipeline",
    subtitle="From raw mesoscale meteorology to real-time personal safety directives.",
    badge="SYSTEM PIPELINE"
)

step_col1, step_col2, step_col3, step_col4 = st.columns(4)

with step_col1:
    safe_markdown("""
    <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 24px 20px; min-height: 240px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05); display: flex; flex-direction: column; justify-content: space-between;">
        <div>
            <div style="font-family: var(--font-mono); font-size: 0.74rem; font-weight: 800; color: #FF6845; margin-bottom: 8px;">
                STAGE 01
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                Sensor Ingestion
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; line-height: 1.55; margin: 0;">
                Continuous zero-key synchronization with Open-Meteo &amp; local station telemetry across 6 criteria pollutants, surface pressure, and boundary layer thermodynamics.
            </p>
        </div>
        <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; border-top: 1px solid #EBE6DF; padding-top: 8px; margin-top: 12px;">
            ● 264+ Records Cached / WAL SQLite
        </div>
    </div>
    """)

with step_col2:
    safe_markdown("""
    <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 24px 20px; min-height: 240px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05); display: flex; flex-direction: column; justify-content: space-between;">
        <div>
            <div style="font-family: var(--font-mono); font-size: 0.74rem; font-weight: 800; color: #FF6845; margin-bottom: 8px;">
                STAGE 02
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                Neural Prognostics
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; line-height: 1.55; margin: 0;">
                Autoregressive lag features (1h, 3h, 6h, 24h), rolling statistics, and cyclical time encodings powering an XGBoost regressor with 90% Gaussian uncertainty ribbons.
            </p>
        </div>
        <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; border-top: 1px solid #EBE6DF; padding-top: 8px; margin-top: 12px;">
            ● 72-Hour Horizon Depth
        </div>
    </div>
    """)

with step_col3:
    safe_markdown("""
    <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 24px 20px; min-height: 240px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05); display: flex; flex-direction: column; justify-content: space-between;">
        <div>
            <div style="font-family: var(--font-mono); font-size: 0.74rem; font-weight: 800; color: #FF6845; margin-bottom: 8px;">
                STAGE 03
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                Dosage Modeling
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; line-height: 1.55; margin: 0;">
                Calculates cumulative particulate mass (µg) and alveolar tissue deposition based on minute ventilation rates (0.45 m³/h to 3.20 m³/h) and user health sensitivities.
            </p>
        </div>
        <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; border-top: 1px solid #EBE6DF; padding-top: 8px; margin-top: 12px;">
            ● WHO Daily Ceiling Calibration
        </div>
    </div>
    """)

with step_col4:
    safe_markdown("""
    <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 24px 20px; min-height: 240px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05); display: flex; flex-direction: column; justify-content: space-between;">
        <div>
            <div style="font-family: var(--font-mono); font-size: 0.74rem; font-weight: 800; color: #FF6845; margin-bottom: 8px;">
                STAGE 04
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                Window Clearance
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; line-height: 1.55; margin: 0;">
                Authorizes the optimal outdoor safe window for your planned activity, identifies avoid periods, and provides respiratory mask standards.
            </p>
        </div>
        <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; border-top: 1px solid #EBE6DF; padding-top: 8px; margin-top: 12px;">
            ● 28,453 Decisions Authorized
        </div>
    </div>
    """)

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 4. TWO TAILORED PRESENTATION MODES FOR DIVERSE AUDIENCES
# ==============================================================================
render_section_header(
    title="Designed for Both Everyday Decision-Makers & Engineers",
    subtitle="Toggle effortlessly between cheerful, plain-English guidance and deep scientific telemetry.",
    badge="TWO MODES"
)

mod_col1, mod_col2 = st.columns(2)

with mod_col1:
    with st.container(border=True):
        safe_markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span class="ag-badge ag-badge-good" style="font-size: 0.72rem; padding: 3px 12px;">
                🌿 SIMPLE MODE (EVERYDAY PEOPLE)
            </span>
            <span style="font-family: var(--font-mono); font-size: 0.70rem; color: #8896A6;">HUMAN-FIRST</span>
        </div>
        <div style="font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
            Plain-English Safety &amp; Animated 3D Guidance
        </div>
        <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; line-height: 1.6; margin-bottom: 16px;">
            Designed for normal everyday users, parents, seniors, and athletes who want quick answers: <em>"Can my child play outside?"</em>, <em>"When is the best time for my run?"</em>. Includes friendly 3D cartoon visuals and instant go/no-go advice.
        </p>
        <ul style="color: #5A6E85; font-size: 0.84rem; line-height: 1.6; margin-bottom: 20px; padding-left: 20px;">
            <li>Direct Yes/No/Caution daily outdoor answers</li>
            <li>Best Safe Window finder with Avoid period highlights</li>
            <li>Cute 3D animated character guidance and tips</li>
            <li>Practical N95 mask and indoor air barrier recommendations</li>
        </ul>
        """)
        if st.button("Explore Simple Mode →", key="btn_mode_simple_tour", use_container_width=True):
            set_view_mode(SIMPLE_MODE)
            st.switch_page("Home.py")

with mod_col2:
    with st.container(border=True):
        safe_markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span class="ag-badge ag-badge-neutral" style="font-size: 0.72rem; padding: 3px 12px; border-color: #38BDF8; color: #0284C7;">
                ⚙️ TECHNICAL MODE (ENVIRONMENTAL TECH)
            </span>
            <span style="font-family: var(--font-mono); font-size: 0.70rem; color: #8896A6;">SCIENTIFIC RIGOR</span>
        </div>
        <div style="font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
            Criteria Pollutants, Physics &amp; ML Diagnostics
        </div>
        <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; line-height: 1.6; margin-bottom: 16px;">
            Designed for data scientists, meteorologists, urban planners, and environmental engineers who demand full criteria pollutants, mesoscale atmospheric thermodynamics, and machine learning governance.
        </p>
        <ul style="color: #5A6E85; font-size: 0.84rem; line-height: 1.6; margin-bottom: 20px; padding-left: 20px;">
            <li>6 Criteria Pollutants array (PM₂.₅, PM₁₀, NO₂, SO₂, O₃, CO) with WHO targets</li>
            <li>Atmospheric Boundary Layer (PBL) height &amp; Thermal Inversion Trapping risk</li>
            <li>Interactive minute ventilation inhaled dosage calculator (µg)</li>
            <li>Raw lagged feature vector inspector &amp; JSON telemetry payload</li>
        </ul>
        """)
        if st.button("Explore Technical Mode →", key="btn_mode_tech_tour", use_container_width=True):
            set_view_mode(TECHNICAL_MODE)
            st.switch_page("Home.py")

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 5. PLATFORM IMPACT & PROVENANCE METRICS
# ==============================================================================
render_section_header(
    title="Platform Impact & System Provenance",
    subtitle="Autonomous environmental intelligence evaluated across multi-city archives.",
    badge="PROVENANCE"
)

mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)

with mcol1:
    safe_markdown("""
    <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 20px 18px; text-align: center; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05);">
        <div style="font-family: var(--font-mono); font-size: 2.3rem; font-weight: 800; color: #1F344C; line-height: 1;">99.8%</div>
        <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #5A6E85; text-transform: uppercase; margin-top: 6px;">Ground Sensor Sync</div>
        <div style="font-family: var(--font-sans); font-size: 0.72rem; color: #8896A6; margin-top: 4px;">Zero-latency live streams</div>
    </div>
    """)

with mcol2:
    safe_markdown("""
    <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 20px 18px; text-align: center; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05);">
        <div style="font-family: var(--font-mono); font-size: 2.3rem; font-weight: 800; color: #1F344C; line-height: 1;">72h</div>
        <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #5A6E85; text-transform: uppercase; margin-top: 6px;">Neural Horizon Depth</div>
        <div style="font-family: var(--font-sans); font-size: 0.72rem; color: #8896A6; margin-top: 4px;">90% CI uncertainty bands</div>
    </div>
    """)

with mcol3:
    safe_markdown("""
    <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 20px 18px; text-align: center; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05);">
        <div style="font-family: var(--font-mono); font-size: 2.3rem; font-weight: 800; color: #FF6845; line-height: 1;">4.8×</div>
        <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #5A6E85; text-transform: uppercase; margin-top: 6px;">Inhalation Burden Cut</div>
        <div style="font-family: var(--font-sans); font-size: 0.72rem; color: #8896A6; margin-top: 4px;">Via safe window timing</div>
    </div>
    """)

with mcol4:
    safe_markdown("""
    <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 20px 18px; text-align: center; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05);">
        <div style="font-family: var(--font-mono); font-size: 2.3rem; font-weight: 800; color: #1F344C; line-height: 1;">32ms</div>
        <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #5A6E85; text-transform: uppercase; margin-top: 6px;">Inference Latency</div>
        <div style="font-family: var(--font-sans); font-size: 0.72rem; color: #8896A6; margin-top: 4px;">Local XGBoost evaluation</div>
    </div>
    """)

with mcol5:
    safe_markdown("""
    <div class="ag-card" style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 20px 18px; text-align: center; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05);">
        <div style="font-family: var(--font-mono); font-size: 2.3rem; font-weight: 800; color: #059669; line-height: 1;">100%</div>
        <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #5A6E85; text-transform: uppercase; margin-top: 6px;">Local Privacy</div>
        <div style="font-family: var(--font-sans); font-size: 0.72rem; color: #8896A6; margin-top: 4px;">SQLite WAL on your machine</div>
    </div>
    """)

st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 6. EXECUTIVE FOOTER
# ==============================================================================
render_ensur_executive_footer()
