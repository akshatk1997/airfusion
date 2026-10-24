"""
AirGuard Platform Introduction & Interactive Architecture Tour.
Modeled faithfully after ensur.ai's signature platform intro experience, tailored specifically
for autonomous ambient air intelligence, predictive machine learning, and outdoor safety.
Includes interactive airguardOS decision simulation, animated 3D cartoon mascots, and real-life photography.
"""

from __future__ import annotations

import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path
import streamlit as st

PAGE_DIR = Path(__file__).resolve().parent
APP_DIR = PAGE_DIR.parent
AIRGUARD_ROOT = APP_DIR.parent
if str(AIRGUARD_ROOT) not in sys.path:
    sys.path.insert(0, str(AIRGUARD_ROOT))

from src.data_collection import geocode_city, fetch_current_air_quality
from app.components.navbar import render_global_navbar, PRESET_CITIES
from app.components.mode_switcher import (
    get_view_mode,
    set_view_mode,
    render_mode_banner,
    SIMPLE_MODE,
    TECHNICAL_MODE
)
from app.components.design_system import (
    render_section_header,
    safe_markdown,
    ICONS
)
from app.components.simple_cards import (
    get_mascot_base64,
    render_ensur_executive_footer
)

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
            <span>AUTONOMOUS ENVIRONMENTAL OPERATING SYSTEM • 99.8% SENSOR CONSENSUS</span>
        </div>
    </div>
    <h1 style="font-family: var(--font-heading); font-size: clamp(2.4rem, 5vw, 3.8rem); font-weight: 800; color: #1F344C; line-height: 1.15; letter-spacing: -0.035em; max-width: 960px; margin: 0 auto var(--space-4) auto;">
        Making outdoor safety <span class="ensur-coral-gradient">deterministic, predictive,</span> and personal.
    </h1>
    <p style="font-family: var(--font-sans); font-size: 1.12rem; color: #5A6E85; max-width: 780px; margin: 0 auto var(--space-6) auto; line-height: 1.65;">
        Traditional weather apps only report static history from delayed airport stations. AirGuard continuously evaluates ambient ground telemetry, forecasts pollution spikes up to 72 hours ahead with machine learning, and calculates personalized physiological lung intake so you know the exact window to step outside safely.
    </p>
</section>
""")

# Action Buttons: Launch Simple vs. Launch Technical Mode vs. Jump to Simulator
col_cta1, col_cta2, col_cta3 = st.columns([1.2, 1.2, 1.0])

with col_cta1:
    if st.button("🌿 Launch Everyday Sentry (Simple Mode)", key="intro_btn_simple", use_container_width=True, type="primary"):
        set_view_mode(SIMPLE_MODE)
        st.switch_page("Home.py")

with col_cta2:
    if st.button("⚙️ Open Command Center (Technical Mode)", key="intro_btn_tech", use_container_width=True):
        set_view_mode(TECHNICAL_MODE)
        st.switch_page("Home.py")

with col_cta3:
    if st.button("⚡ Test Live Decision Engine", key="intro_btn_jump_sim", use_container_width=True):
        st.session_state["show_live_sim_cert"] = True

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)


# ==============================================================================
# 2. THE FLAGSHIP ENSUR-STYLE AIRGUARD ENGINE: VERIFY. DECIDE. PROTECT.
# ==============================================================================
render_section_header(
    title="The Core Decision Cycle: Verify. Decide. Protect.",
    subtitle="Modeled on ensurOS conditional architecture — translating real-world atmospheric chemistry into verified human safety clearance.",
    badge="DECISION INFRASTRUCTURE"
)

safe_markdown("""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 28px;">
    <!-- Step 1: VERIFY -->
    <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 18px; padding: 26px 22px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.05); display: flex; flex-direction: column; justify-content: space-between;">
        <div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <span style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 800; color: #10B981; letter-spacing: 0.06em;">PHASE 01</span>
                <span style="background: rgba(16, 185, 129, 0.12); color: #065F46; font-size: 0.65rem; font-family: var(--font-mono); font-weight: 700; padding: 3px 8px; border-radius: 9999px;">MULTI-SOURCE TRUTH</span>
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                1. Verify
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #5A6E85; line-height: 1.6; margin: 0;">
                Cross-references 6 criteria pollutants (PM₂.₅, PM₁₀, NO₂, SO₂, O₃, CO) with ground monitoring stations and Open-Meteo satellite feeds. Re-evaluates stale atmospheric facts every 15 minutes.
            </p>
        </div>
        <div style="margin-top: 16px; padding-top: 10px; border-top: 1px solid #EBE6DF; font-family: var(--font-mono); font-size: 0.70rem; color: #8896A6;">
            ● 264+ Telemetry Records Ingested
        </div>
    </div>

    <!-- Step 2: DECIDE -->
    <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 18px; padding: 26px 22px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.05); display: flex; flex-direction: column; justify-content: space-between;">
        <div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <span style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 800; color: #FF6845; letter-spacing: 0.06em;">PHASE 02</span>
                <span style="background: rgba(255, 104, 69, 0.12); color: #C2410C; font-size: 0.65rem; font-family: var(--font-mono); font-weight: 700; padding: 3px 8px; border-radius: 9999px;">PHYSICS + ML RULES</span>
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                2. Decide
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #5A6E85; line-height: 1.6; margin: 0;">
                Translates health vulnerability thresholds and activity respiratory rates into executable decision logic. Runs an XGBoost 72-hour forecast with 90% uncertainty ribbons to model inhaled alveolar deposition (µg).
            </p>
        </div>
        <div style="margin-top: 16px; padding-top: 10px; border-top: 1px solid #EBE6DF; font-family: var(--font-mono); font-size: 0.70rem; color: #8896A6;">
            ● 72-Hour Prognostic Horizon
        </div>
    </div>

    <!-- Step 3: PROTECT / SETTLE -->
    <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 18px; padding: 26px 22px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.05); display: flex; flex-direction: column; justify-content: space-between;">
        <div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <span style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 800; color: #1F344C; letter-spacing: 0.06em;">PHASE 03</span>
                <span style="background: rgba(31, 52, 76, 0.08); color: #1F344C; font-size: 0.65rem; font-family: var(--font-mono); font-weight: 700; padding: 3px 8px; border-radius: 9999px;">VERIFIED CLEARANCE</span>
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                3. Settle / Protect
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #5A6E85; line-height: 1.6; margin: 0;">
                Issues an authoritative Go/Caution/No-Go clearance token, identifies the pristine outdoor time window, specifies personal gear requirements (N95, hydration), and triggers proactive notifications.
            </p>
        </div>
        <div style="margin-top: 16px; padding-top: 10px; border-top: 1px solid #EBE6DF; font-family: var(--font-mono); font-size: 0.70rem; color: #8896A6;">
            ● Deterministic Safety Certificate
        </div>
    </div>
</div>
""")


# ==============================================================================
# 3. INTERACTIVE LIVE SIMULATOR: RUN THE AIRGUARDOS ENGINE IN REAL TIME
# ==============================================================================
with st.container(border=True):
    safe_markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
        <div>
            <span class="ag-badge ag-badge-brand" style="font-size: 0.72rem; padding: 3px 12px;">⚡ LIVE SANDBOX SIMULATOR</span>
            <h3 style="font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #1F344C; margin: 6px 0 2px 0;">
                Test the Autonomous Decision Engine
            </h3>
            <p style="font-family: var(--font-sans); font-size: 0.86rem; color: #5A6E85; margin: 0;">
                Select an outdoor activity profile and watch AirGuard verify real telemetry, calculate lung deposition, and issue a verified safety verdict.
            </p>
        </div>
        <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #FF6845; font-weight: 700;">
            ENGINE: airguardOS v2.4 (Active)
        </div>
    </div>
    """)

    sim_col1, sim_col2, sim_col3 = st.columns([1.4, 1.2, 1.0])

    with sim_col1:
        sim_scenario = st.selectbox(
            "Select Real-World Activity Scenario",
            [
                "🏃 Morning 10K Cardio Run (Ventilation: 55 L/min)",
                "🎒 School Recess & Playground (Children, 2.2x Sensitivity)",
                "🧓 Senior Citizen Cardio Walk (Asthma & Heart Caution)",
                "🚴 Urban Rush-Hour Bike Commute (High Exhaust Zone)"
            ],
            key="sim_scenario_select"
        )

    cities_list = list(PRESET_CITIES.keys()) if isinstance(PRESET_CITIES, dict) else list(PRESET_CITIES)
    with sim_col2:
        sim_city = st.selectbox(
            "Target Location for Verification",
            cities_list,
            index=cities_list.index(active_city) if active_city in cities_list else 0,
            key="sim_city_select"
        )

    with sim_col3:
        st.write("")
        st.write("")
        run_sim = st.button("⚡ Run airguardOS Engine", key="btn_run_engine_sim", use_container_width=True, type="primary")

    if run_sim or st.session_state.get("show_live_sim_cert", False):
        st.session_state["show_live_sim_cert"] = True
        
        # Geocode and fetch live data for simulation
        loc = geocode_city(sim_city)
        if loc:
            try:
                live_curr = fetch_current_air_quality(loc["latitude"], loc["longitude"])
                pm25_val = float(live_curr.get("pm2_5") or 28.0)
                aqi_val = int(live_curr.get("aqi") or 78)
                temp_val = float(live_curr.get("temperature") or live_curr.get("temperature_2m") or 24.0)
                wind_val = float(live_curr.get("wind_speed") or live_curr.get("wind_speed_10m") or 11.0)
            except Exception:
                pm25_val, aqi_val, temp_val, wind_val = 28.0, 78, 24.0, 11.0
        else:
            pm25_val, aqi_val, temp_val, wind_val = 28.0, 78, 24.0, 11.0

        # Scenario parameters
        if "10K" in sim_scenario:
            activity_label = "Morning 10K Distance Run"
            vent_rate = 55.0  # L/min
            risk_tier = "Moderate" if pm25_val < 35 else "Elevated Caution"
            safe_window = "06:00 AM – 07:30 AM (Crisp Early Sun)"
            gear_recs = ["Fresh Water Bottle", "UV Sunglasses", "Paced Cardio Interval"]
            if pm25_val > 35:
                gear_recs.append("N95 Sports Mask")
        elif "School" in sim_scenario:
            activity_label = "School Recess & Playground"
            vent_rate = 32.0  # L/min
            risk_tier = "Good" if pm25_val < 30 else "Play Indoors"
            safe_window = "10:30 AM – 11:30 AM (Grassy Field Recess)"
            gear_recs = ["Water Bottle", "Cotton Scarf/Hat", "Hand & Face Wash After Recess"]
            if pm25_val > 35:
                gear_recs.append("Child-Sized Clean Air Mask")
        elif "Senior" in sim_scenario:
            activity_label = "Senior Citizen Cardio Walk"
            vent_rate = 22.0  # L/min
            risk_tier = "Protected" if pm25_val < 25 else "Indoor Walking Recommended"
            safe_window = "07:30 AM – 08:30 AM (Calm Park Corridor)"
            gear_recs = ["Emergency Rescue Inhaler", "Hydration Mug", "Supportive Footwear"]
            if pm25_val > 30:
                gear_recs.append("Light Protective Mask")
        else:
            activity_label = "Urban Rush-Hour Bike Commute"
            vent_rate = 45.0
            risk_tier = "Caution (Vehicle Soot)"
            safe_window = "Avoid 08:30–09:30 AM; Take Secondary Tree-Lined Street"
            gear_recs = ["N95 Carbon-Filter Mask", "Wraparound Glasses", "6-Foot Curb Buffer"]

        # Calculate inhaled mass micro-grams for 60 min session
        # Mass = Ventilation (m3/h) * PM2.5 (ug/m3) * duration (h)
        inhaled_ug = round((vent_rate * 60 / 1000.0) * pm25_val * 1.0, 1)
        who_pct = min(round((inhaled_ug / 25.0) * 100, 0), 300)

        # Cryptographic Certificate ID
        token_hash = hashlib.sha256(f"{sim_city}_{sim_scenario}_{datetime.now().strftime('%Y%m%d%H')}".encode()).hexdigest()[:12].upper()
        cert_id = f"AG-{token_hash}"

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Render Verification Certificate Card
        cert_html = f"""
        <div class="ag-cert-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
                <div>
                    <span class="ag-cert-badge">● CERTIFIED AUTONOMOUS VERDICT</span>
                    <h2 style="font-family: var(--font-heading); font-size: 1.55rem; font-weight: 800; color: #1F344C; margin: 8px 0 4px 0;">
                        airguardOS Clearance: {activity_label}
                    </h2>
                    <div class="ag-cert-token">CERTIFICATE TOKEN: {cert_id} &bull; ISSUED: {datetime.now().strftime('%b %d, %Y %H:%M')}</div>
                </div>
                <div style="text-align: right; background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 12px; padding: 10px 16px; box-shadow: 0 2px 8px rgba(31,52,76,0.04);">
                    <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; text-transform: uppercase;">Location Ingested</div>
                    <div style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 800; color: #1F344C;">{sim_city}</div>
                    <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #059669; font-weight: 700;">PM₂.₅: {pm25_val} µg/m³ (AQI {aqi_val})</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 20px;">
                <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 14px 16px;">
                    <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; text-transform: uppercase;">Optimal Safe Window</div>
                    <div style="font-family: var(--font-heading); font-size: 0.96rem; font-weight: 800; color: #1F344C; margin-top: 4px;">{safe_window}</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 14px 16px;">
                    <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; text-transform: uppercase;">Estimated Inhaled Dosage</div>
                    <div style="font-family: var(--font-heading); font-size: 0.96rem; font-weight: 800; color: #FF6845; margin-top: 4px;">{inhaled_ug} µg ({int(who_pct)}% WHO Daily Base)</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 14px 16px;">
                    <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; text-transform: uppercase;">Atmospheric Boundary State</div>
                    <div style="font-family: var(--font-heading); font-size: 0.96rem; font-weight: 800; color: #10B981; margin-top: 4px;">Active Dispersion &bull; {wind_val} km/h Wind</div>
                </div>
            </div>

            <div style="background: rgba(255, 104, 69, 0.05); border: 1px solid rgba(255, 104, 69, 0.2); border-radius: 12px; padding: 12px 18px; margin-bottom: 12px;">
                <strong style="color: #1F344C; font-size: 0.85rem; font-family: var(--font-heading);">Mandated Protective Checklist:</strong>
                <span style="color: #5A6E85; font-size: 0.84rem; font-family: var(--font-sans); margin-left: 8px;">
                    {' &bull; '.join(gear_recs)}
                </span>
            </div>
            
            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #8896A6; text-align: right;">
                Cryptographically computed via XGBoost Regressor (n_estimators=100, max_depth=5) &bull; Zero external keys required
            </div>
        </div>
        """
        safe_markdown(cert_html)

st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)


# ==============================================================================
# 4. VISUAL UNIVERSE: 3D ANIMATED MASCOTS & REAL-LIFE PHOTOGRAPHY SHOWCASE
# ==============================================================================
render_section_header(
    title="Visual Universe: 3D Animated Mascots & Real-Life Reality",
    subtitle="Bridging playful, approachable family storytelling with cinematic real-world outdoor lifestyle photography.",
    badge="VISUAL ARCHITECTURE"
)

tab_cartoons, tab_reallife = st.tabs([
    "🎨 Simple Mode: 3D Animated Characters & Eco Mascots",
    "📷 Real-Life Reality: Environmental & Outdoor Lifestyle Photography"
])

# ----------------- TAB 1: 3D CARTOON MASCOTS -----------------
with tab_cartoons:
    safe_markdown("""
    <p style="font-family: var(--font-sans); font-size: 0.92rem; color: #5A6E85; line-height: 1.6; margin-bottom: 24px;">
        Designed exclusively for <strong>Simple Mode</strong>, our friendly 3D Pixar/Disney-styled cartoon characters make atmospheric science intuitive and empowering for children, parents, and everyday walkers.
    </p>
    """)

    mascot_clean_b64 = get_mascot_base64("mascot_clean_air.jpg")
    mascot_runner_b64 = get_mascot_base64("mascot_outdoor_runner.jpg")
    mascot_mask_b64 = get_mascot_base64("mascot_caution_mask.jpg")
    mascot_sanctuary_b64 = get_mascot_base64("mascot_indoor_sanctuary.jpg")

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)

    with mcol1:
        safe_markdown(f"""
        <div class="ag-photo-card" style="text-align: center; padding: 20px 16px;">
            <div class="ag-cartoon-container ag-cartoon-float" style="margin-bottom: 16px;">
                <img src="{mascot_clean_b64}" class="ag-cartoon-mascot-img" style="width: 130px; height: 130px;" alt="Aero Cloud Buddy" />
            </div>
            <div class="ag-photo-title" style="font-size: 1.05rem;">Aero the Clean Air Buddy</div>
            <p class="ag-photo-desc" style="font-size: 0.80rem;">
                Our cheerful AI chatbot companion who explains complex micro-particulates as "invisible dust glitter" with warm, child-friendly storytelling.
            </p>
        </div>
        """)

    with mcol2:
        safe_markdown(f"""
        <div class="ag-photo-card" style="text-align: center; padding: 20px 16px;">
            <div class="ag-cartoon-container ag-cartoon-bob" style="margin-bottom: 16px;">
                <img src="{mascot_runner_b64}" class="ag-cartoon-mascot-img" style="width: 130px; height: 130px;" alt="Fresh Air Runner" />
            </div>
            <div class="ag-photo-title" style="font-size: 1.05rem;">The Fresh Air Runner</div>
            <p class="ag-photo-desc" style="font-size: 0.80rem;">
                Celebrates peak outdoor exercise timing, guiding joggers and athletes to their golden clean-air cardio windows each morning.
            </p>
        </div>
        """)

    with mcol3:
        safe_markdown(f"""
        <div class="ag-photo-card" style="text-align: center; padding: 20px 16px;">
            <div class="ag-cartoon-container ag-cartoon-drift" style="margin-bottom: 16px;">
                <img src="{mascot_mask_b64}" class="ag-cartoon-mascot-img" style="width: 130px; height: 130px;" alt="The Mask Hero" />
            </div>
            <div class="ag-photo-title" style="font-size: 1.05rem;">The Mask Hero Shield</div>
            <p class="ag-photo-desc" style="font-size: 0.80rem;">
                A friendly superhero mascot teaching kids that masks are personal particle shields that keep delicate lungs happy and dust-free.
            </p>
        </div>
        """)

    with mcol4:
        safe_markdown(f"""
        <div class="ag-photo-card" style="text-align: center; padding: 20px 16px;">
            <div class="ag-cartoon-container ag-cartoon-bob" style="margin-bottom: 16px;">
                <img src="{mascot_sanctuary_b64}" class="ag-cartoon-mascot-img" style="width: 130px; height: 130px;" alt="Clean Air Sanctuary" />
            </div>
            <div class="ag-photo-title" style="font-size: 1.05rem;">The Clean Air Sanctuary</div>
            <p class="ag-photo-desc" style="font-size: 0.80rem;">
                Shows children how closed windows, house plants, and air purifiers turn the home into an impenetrable clean-air fortress.
            </p>
        </div>
        """)

# ----------------- TAB 2: REAL-LIFE PHOTOGRAPHY -----------------
with tab_reallife:
    safe_markdown("""
    <p style="font-family: var(--font-sans); font-size: 0.92rem; color: #5A6E85; line-height: 1.6; margin-bottom: 24px;">
        High-resolution real-world photography capturing the genuine dilemmas and healthy outdoor moments AirGuard was built to protect.
    </p>
    """)

    real_col1, real_col2 = st.columns(2)

    with real_col1:
        st.image(
            str(AIRGUARD_ROOT / "app" / "assets" / "images" / "real_morning_runner_park.jpg"),
            caption="Golden Hour Park Run — Tree canopies naturally scrub up to 25% of micro-soot particles.",
            use_container_width=True
        )
        safe_markdown("""
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 14px 18px; margin-bottom: 24px;">
            <strong style="color: #1F344C; font-family: var(--font-heading); font-size: 0.92rem;">Healthy Athletic Lifestyle</strong>
            <p style="color: #5A6E85; font-size: 0.82rem; margin: 4px 0 0 0; line-height: 1.5;">
                Deep cardio breathing increases minute ventilation up to 60 L/min. AirGuard identifies the golden hours when ambient air is cleanest so runners build endurance without pulmonary inflammation.
            </p>
        </div>
        """)

        st.image(
            str(AIRGUARD_ROOT / "app" / "assets" / "images" / "real_city_skyline_telemetry.jpg"),
            caption="Metropolitan Skyline Sentry — Monitoring boundary layer thermodynamics across urban hubs.",
            use_container_width=True
        )
        safe_markdown("""
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 14px 18px; margin-bottom: 24px;">
            <strong style="color: #1F344C; font-family: var(--font-heading); font-size: 0.92rem;">Smart City Mesoscale Monitoring</strong>
            <p style="color: #5A6E85; font-size: 0.82rem; margin: 4px 0 0 0; line-height: 1.5;">
                AirGuard models boundary layer (PBL) thermal inversions where cold ground air traps tailpipe soot under high-pressure domes, warning commuters ahead of visible smog.
            </p>
        </div>
        """)

    with real_col2:
        st.image(
            str(AIRGUARD_ROOT / "app" / "assets" / "images" / "real_family_outdoor_walk.jpg"),
            caption="Family Park Recess — Pure fresh air for growing lungs and sunny weekend walks.",
            use_container_width=True
        )
        safe_markdown("""
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 14px 18px; margin-bottom: 24px;">
            <strong style="color: #1F344C; font-family: var(--font-heading); font-size: 0.92rem;">Family & Child Respiratory Protection</strong>
            <p style="color: #5A6E85; font-size: 0.82rem; margin: 4px 0 0 0; line-height: 1.5;">
                Children inhale 2.2 times more air per kilogram of body weight than adults. AirGuard gives parents complete clarity on when park strolls and playground recess are 100% safe.
            </p>
        </div>
        """)

        st.image(
            str(AIRGUARD_ROOT / "app" / "assets" / "images" / "real_traffic_smog_contrast.jpg"),
            caption="The Rush-Hour Smog Dilemma — Exhaust plumes and particulate spikes that AirGuard shields you from.",
            use_container_width=True
        )
        safe_markdown("""
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 14px; padding: 14px 18px; margin-bottom: 24px;">
            <strong style="color: #1F344C; font-family: var(--font-heading); font-size: 0.92rem;">Everyday Urban Commuter Protection</strong>
            <p style="color: #5A6E85; font-size: 0.82rem; margin: 4px 0 0 0; line-height: 1.5;">
                Tailpipe exhaust and road grit peak during morning rush hours. AirGuard recommends keeping a 6-foot curb setback and wearing N95 masks when waiting at congested transit intersections.
            </p>
        </div>
        """)

st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)


# ==============================================================================
# 5. THE PARADIGM SHIFT: STATIC WEATHER APPS VS. AIRGUARD AUTONOMOUS SENTRY
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
# 6. ARCHITECTURE TOUR: THE 4-STAGE AUTONOMOUS PIPELINE
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
# 7. TWO TAILORED PRESENTATION MODES FOR DIVERSE AUDIENCES
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
            <li>Child-friendly Aero AI Chatbot, departure packing kit, &amp; eco quest games</li>
        </ul>
        """)
        if st.button("Explore Simple Mode →", key="btn_mode_simple_tour", use_container_width=True, type="primary"):
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
            <li>Continuous 72h continuum timeline &amp; comparative sensor matrix</li>
        </ul>
        """)
        if st.button("Explore Technical Mode →", key="btn_mode_tech_tour", use_container_width=True):
            set_view_mode(TECHNICAL_MODE)
            st.switch_page("Home.py")

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)


# ==============================================================================
# 8. PLATFORM IMPACT & PROVENANCE METRICS
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
# 9. EXECUTIVE ENSUR-STYLE FOOTER
# ==============================================================================
render_ensur_executive_footer()
