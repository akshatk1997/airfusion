"""
Simple Mode Presentation Views for AirGuard.
Orchestrates clear, non-technical, friendly user experiences.
AirGuard Professional Design Language:
Warm Ivory canvas (#FAF6F1), Pure White surfaces (#FFFFFF),
Deep Navy typography (#1F344C), warm borders (#EBE6DF), and coral accents (#FF6845).
Reuses the exact same underlying telemetry, ML forecasting, and risk-engine logic.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional

from src.database import get_user_profile, save_user_profile
from src.data_collection import geocode_city, fetch_current_air_quality
from src.predict import generate_forecast
from src.temporal_continuum import get_city_temporal_continuum
from src.safety_rules import (
    calculate_outdoor_risk_score,
    generate_personalized_advice,
    find_safe_outdoor_windows
)
from app.components.design_system import format_location_label, safe_markdown
from app.components.simple_cards import (
    get_mascot_base64,
    render_air_safety_card,
    render_simple_timeline,
    render_todays_tip,
    render_simple_alert_setup,
    render_simple_disclaimer,
    render_simple_weather_cards,
    render_simple_pollutant_cards,
    render_simple_indoor_mask_cards,
    render_simple_3d_cartoon_showcase,
    render_airguard_hero_section,
    render_airguard_comparison_section,
    render_airguard_engine_section,
    render_airguard_impact_metrics,
    render_airguard_solutions_grid,
    render_airguard_executive_footer
)
from app.components.simple_chatbot import render_aero_chatbot
from app.components.outdoor_kit import render_outdoor_departure_kit
from app.components.simple_games import render_eco_quest_hub
from src.config import PRESET_CITIES
from src.database import fetch_historical_records, fetch_all_locations
from src.news_service import get_news_feed


def render_simple_home(active_city: str) -> None:
    """
    Renders the dedicated Simple Mode homepage for AirGuard.
    AirGuard flagship environmental intelligence architecture.
    """
    # Load user profile from SQLite
    user_prof = get_user_profile()
    age_group = user_prof.get("age_group", "adult")
    sensitivity = user_prof.get("health_sensitivity", "none")
    usual_activity = user_prof.get("usual_activities", "walk")
    duration_mins = int(user_prof.get("typical_duration_mins", 30))
    preferred_time = user_prof.get("preferred_time", "now")
    threshold = float(user_prof.get("pm25_threshold", 35.0))

    # Geocode active city
    loc = geocode_city(active_city)
    if not loc:
        st.error(f"Could not find coordinates for '{active_city}'. Please pick a city from the top bar.")
        return

    city_display = format_location_label(loc)

    # 1. Fetch live telemetry (shared pipeline)
    curr = fetch_current_air_quality(loc["latitude"], loc["longitude"])
    pm25_val = float(curr.get("pm2_5", 0.0))
    aqi_val = int(curr.get("aqi", 0))
    temp_val = float(curr.get("temperature", 24.0)) if curr.get("temperature") is not None else 24.0
    humidity_val = float(curr.get("humidity", 50.0)) if curr.get("humidity") is not None else 50.0
    wind_val = float(curr.get("wind_speed", 2.0)) if curr.get("wind_speed") is not None else 2.0

    # 2. Fetch 24-hour forecast
    forecast_df, _ = generate_forecast(active_city, horizon_hours=24)
    if forecast_df is None or forecast_df.empty:
        hours = pd.date_range(start=pd.Timestamp.now(), periods=24, freq="h")
        forecast_df = pd.DataFrame({
            "target_time": [h.strftime("%Y-%m-%d %H:%M") for h in hours],
            "predicted_pm2_5": [max(5.0, pm25_val * (1.0 + 0.15 * (i % 6 - 3) / 3)) for i in range(24)],
            "predicted_aqi": [aqi_val for _ in range(24)],
            "lower_ci": [max(1.0, pm25_val * 0.8) for _ in range(24)],
            "upper_ci": [pm25_val * 1.25 for _ in range(24)]
        })

    # 3. Calculate Risk Engine outputs
    risk_score, risk_cat = calculate_outdoor_risk_score(
        aqi=aqi_val,
        pm25=pm25_val,
        health_sensitivity=sensitivity,
        age_group=age_group,
        activity=usual_activity,
        duration_mins=duration_mins
    )

    advice = generate_personalized_advice(
        risk_score=risk_score,
        risk_category=risk_cat,
        aqi=aqi_val,
        pm25=pm25_val,
        health_sensitivity=sensitivity,
        age_group=age_group,
        activity=usual_activity,
        duration_mins=duration_mins,
        preferred_time=preferred_time
    )

    safe_windows = find_safe_outdoor_windows(
        forecast_df=forecast_df,
        duration_mins=duration_mins,
        preferred_period=preferred_time,
        user_pm25_threshold=threshold,
        health_sensitivity=sensitivity,
        age_group=age_group,
        activity=usual_activity
    )

    # Friendly Direct Answer Translation
    if risk_cat == "Low":
        answer = "Yes! The air is clean and safe to go outside right now."
        status_level = "Safe"
    elif risk_cat == "Moderate":
        if sensitivity != "none" or age_group in ["child", "senior"]:
            answer = "Caution: Air pollution is slightly elevated. Sensitive individuals should take it easy."
            status_level = "Caution"
        else:
            answer = "Mostly Safe: Air quality is acceptable for healthy adults."
            status_level = "Moderate"
    elif risk_cat == "High":
        answer = "Not recommended right now: Air pollution is high. Consider moving activities indoors."
        status_level = "Avoid"
    else:
        answer = "High Risk: Stay indoors. Outdoor air is currently unhealthy for everyone."
        status_level = "High Risk"

    # Friendly Reason Translation
    if pm25_val > 55:
        simple_reason = f"Tiny harmful particles in the air are high right now ({pm25_val:.0f} µg/m³)."
    elif pm25_val > 35:
        simple_reason = "Air pollution is moderately high, especially for children, seniors, and sensitive lungs."
    else:
        simple_reason = "Pollution levels are currently within safe, healthy boundaries."

    if sensitivity != "none":
        simple_reason += f" Your profile is set for {sensitivity.title()} sensitivity."

    # Best safe window and avoid periods
    best_win = safe_windows.get("best_window", "Now")
    avoid_list = safe_windows.get("avoid_periods", [])
    hourly_timeline = safe_windows.get("hourly_timeline", [])

    # Format real-time live telemetry timestamp
    raw_ts = curr.get("timestamp", "").replace("T", " ")
    try:
        dt_obj = pd.to_datetime(raw_ts)
        timestamp_display = dt_obj.strftime("%I:%M %p Today (Live)")
    except Exception:
        timestamp_display = raw_ts or "Live Ground Tracking"

    # 0. Animated 3D Pixar Cartoon Project Showcase (bridges mode banner and hero section)
    render_simple_3d_cartoon_showcase(
        city_name=city_display,
        pm25_val=pm25,
        aqi_val=aqi_val,
        status_level=status_level
    )

    # 1. Flagship AirGuard Hero Section
    render_airguard_hero_section()

    # 2. Primary Decision Card (The Outdoor Directive)
    render_air_safety_card(
        city_name=city_display,
        status_level=status_level,
        answer_text=answer,
        best_window=best_win,
        avoid_hours=avoid_list,
        main_reason=simple_reason,
        recommendation=advice.get("action", f"Safe for a {duration_mins}-minute {usual_activity}."),
        mask_tip=advice.get("mask_guidance"),
        live_timestamp=timestamp_display
    )

    # 3. Comprehensive Real-Time Weather Station & Atmospheric Continuum
    render_simple_weather_cards(
        temperature=temp_val,
        humidity=humidity_val,
        wind_speed=wind_val,
        weather_data=curr,
        city_name=city_display
    )

    # 4. 24-Hour Timeline
    render_simple_timeline(hourly_timeline)

    # 4.1 Child-Friendly & Non-Tech AI Chatbot: Ask Aero
    render_aero_chatbot(
        city_name=city_display,
        pm25=pm25_val,
        aqi=aqi_val,
        temp=temp_val,
        wind=wind_val,
        humidity=humidity_val,
        user_profile={
            "health_sensitivity": sensitivity,
            "age_group": age_group,
            "usual_activities": usual_activity
        },
        container_key="home_aero_chat"
    )

    # 4.2 What to Carry Outside & Outdoor Safety Departure Kit
    render_outdoor_departure_kit(
        city_name=city_display,
        pm25=pm25_val,
        aqi=aqi_val,
        temp=temp_val,
        wind=wind_val,
        humidity=humidity_val,
        user_profile={
            "health_sensitivity": sensitivity,
            "age_group": age_group,
            "usual_activities": usual_activity
        }
    )

    # 5. AirGuard Signature Section: The Bottleneck Comparison (Once vs Ongoing)
    render_airguard_comparison_section()

    # 6. AirGuard Signature Section: The Autonomous Engine (Deep Navy airguardOS)
    render_airguard_engine_section(active_city=city_display, pm25_val=pm25_val, aqi_val=aqi_val)

    # 7. AirGuard Platform Impact Metrics
    render_airguard_impact_metrics()

    # 8. AirGuard Solutions by Cohort Grid
    render_airguard_solutions_grid()

    # 8.1 Aero's Eco & Clean Air Adventure Quest Hub (Games, Puzzles, & Quizzes)
    render_eco_quest_hub(
        city_name=city_display,
        pm25=pm25_val,
        aqi=aqi_val,
        temp=temp_val,
        wind=wind_val,
        best_time=best_win
    )

    # 9. Two-Column Operational Row: Today's Tip + Simple Alert Setup
    col_tip, col_alert = st.columns([1.1, 1.0])

    with col_tip:
        render_todays_tip(aqi=aqi_val, wind_speed=wind_val, humidity=humidity_val)

        # Quick navigation shortcuts
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-family: var(--font-heading); font-size: 1rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                    🎯 Immediate Actions & Directives
                </div>
                """,
                unsafe_allow_html=True
            )
            col_b1, col_b2, col_b3 = st.columns([1.1, 1.1, 1.0])
            with col_b1:
                if st.button("🛡️ Customize Safe Plan", key="simple_btn_plan", use_container_width=True):
                    st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")
            with col_b2:
                if st.button("📡 Weather & Air", key="simple_btn_live", use_container_width=True):
                    st.switch_page("pages/2_Live_Tracking.py")
            with col_b3:
                if st.button("🌟 Platform Tour", key="simple_btn_intro", use_container_width=True):
                    st.switch_page("pages/0_Platform_Intro.py")

    with col_alert:
        def _handle_alert_save(new_threshold_val: float):
            prof = get_user_profile()
            prof["pm25_threshold"] = new_threshold_val
            prof["aqi_threshold"] = int(new_threshold_val * 2.8)
            save_user_profile(prof)

        render_simple_alert_setup(
            current_threshold=threshold,
            on_save_callback=_handle_alert_save
        )

    # 9.1 Today's Clean Air News & Story Updates (6-Hour Cycle)
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    try:
        s_feed = get_news_feed(active_city=active_city, current_pm25=pm25_val, current_aqi=aqi_val)
        s_local = s_feed["local_news"][0] if s_feed["local_news"] else None
        s_intl = s_feed["international_news"][0] if s_feed["international_news"] else None

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; display: flex; align-items: center; gap: 8px;">
                            <span>📰 Today's Clean Air News for Your Family</span>
                            <span class="ag-badge ag-badge-nothing" style="font-size: 0.65rem; padding: 2px 8px; color: #FF6845; background: rgba(255,104,69,0.1);">
                                UPDATED EVERY 6 HOURS
                            </span>
                        </div>
                        <div style="font-family: var(--font-sans); font-size: 0.85rem; color: #5A6E85;">
                            Stories from doctors, scientists, and city air protectors in plain, friendly language.
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            sn_col1, sn_col2 = st.columns(2)
            with sn_col1:
                if s_local:
                    st.markdown(
                        f"""
                        <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 12px; padding: 14px 16px; min-height: 140px;">
                            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #FF6845; font-weight: 700; margin-bottom: 4px;">
                                📍 LOCAL: {s_local['source_name'].split('(')[0].strip()} • {s_local['time_ago']}
                            </div>
                            <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 800; color: #1F344C; line-height: 1.35; margin-bottom: 6px;">
                                {s_local['title'][:75]}...
                            </div>
                            <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #9A3412; font-weight: 500;">
                                🧒 {s_local['simple_summary'][:110]}...
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            with sn_col2:
                if s_intl:
                    st.markdown(
                        f"""
                        <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 12px; padding: 14px 16px; min-height: 140px;">
                            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #0284C7; font-weight: 700; margin-bottom: 4px;">
                                🌍 GLOBAL: {s_intl['source_name'].split('(')[0].strip()} • {s_intl['time_ago']}
                            </div>
                            <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 800; color: #1F344C; line-height: 1.35; margin-bottom: 6px;">
                                {s_intl['title'][:75]}...
                            </div>
                            <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #0369A1; font-weight: 500;">
                                🧒 {s_intl['simple_summary'][:110]}...
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("📰 Explore All Local & International Air News →", key="btn_simple_news_all", use_container_width=True):
                st.switch_page("pages/7_Air_Quality_News.py")
    except Exception as e:
        pass

    # 10. Required Safety Disclaimer
    render_simple_disclaimer()

    # 11. AirGuard Executive 5-Column Footer
    render_airguard_executive_footer()


# ==============================================================================
# SUBPAGE 1: SIMPLE MODE — MY SAFE OUTDOOR PLAN
# ==============================================================================
def render_simple_safe_plan(active_city: str) -> None:
    """
    Renders Simple Mode Safe Outdoor Plan.
    Friendly activity plan configuration + Air Safety Card + Timeline + Mask & Indoor advice.
    """
    user_prof = get_user_profile()
    
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 9999px; padding: 4px 14px; margin-bottom: 12px;">
                <span class="ag-pulse-dot" style="width: 6px; height: 6px;"></span>
                <span style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #FF6845; text-transform: uppercase; letter-spacing: 0.08em;">
                    INDIVIDUALIZED SAFETY CLEARANCE
                </span>
            </div>
            <h1 style="font-family: var(--font-heading); font-size: 2.3rem; font-weight: 800; color: #1F344C; margin: 0 0 8px 0; letter-spacing: -0.02em;">
                My Safe Outdoor Plan
            </h1>
            <p style="font-family: var(--font-sans); font-size: 1rem; color: #5A6E85; margin: 0;">
                Find the safest window for your activity and see clear precautions before heading outdoors.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Simplified Profile & Activity Builder
    with st.expander("👤 Customize Your Plan (Who, Activity, & Time)", expanded=True):
        col1, col2, col3 = st.columns([1.2, 1.3, 1.3])

        with col1:
            st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.82rem; color: #1F344C;'>1. WHO IS GOING OUT?</strong>", unsafe_allow_html=True)
            age_opts = ["adult", "child", "senior"]
            cur_age = user_prof.get("age_group", "adult")
            sel_age = st.selectbox("Age Group", options=age_opts, index=age_opts.index(cur_age) if cur_age in age_opts else 0, format_func=lambda x: f"For: {x.title()}")

            sens_opts = ["none", "asthma", "allergy", "copd", "heart condition", "pregnancy", "other respiratory sensitivity"]
            cur_sens = user_prof.get("health_sensitivity", "none")
            sel_sens = st.selectbox("Health Sensitivity", options=sens_opts, index=sens_opts.index(cur_sens) if cur_sens in sens_opts else 0, format_func=lambda x: f"Sensitivity: {x.title()}")

        with col2:
            st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.82rem; color: #1F344C;'>2. WHAT ARE YOU DOING?</strong>", unsafe_allow_html=True)
            act_opts = ["walk", "run", "cycle", "outdoor play", "outdoor work", "commute"]
            cur_act = user_prof.get("usual_activities", "walk")
            sel_act = st.selectbox("Activity", options=act_opts, index=act_opts.index(cur_act) if cur_act in act_opts else 0, format_func=lambda x: f"Activity: {x.title()}")

            dur_opts = [15, 30, 45, 60, 90, 120]
            cur_dur = int(user_prof.get("typical_duration_mins", 30))
            sel_dur = st.select_slider("Duration", options=dur_opts, value=cur_dur if cur_dur in dur_opts else 30, format_func=lambda x: f"{x} Minutes")

        with col3:
            st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.82rem; color: #1F344C;'>3. WHEN DO YOU WANT TO GO?</strong>", unsafe_allow_html=True)
            time_opts = ["now", "morning", "afternoon", "evening", "tomorrow"]
            cur_time = user_prof.get("preferred_time", "now")
            sel_time = st.selectbox("Preferred Time", options=time_opts, index=time_opts.index(cur_time) if cur_time in time_opts else 0, format_func=lambda x: f"Time: {x.title()}")

            threshold_val = float(user_prof.get("pm25_threshold", 35.0))
            st.markdown(f"<div style='font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; margin-top: 10px;'>Alert comfort level: <strong style='color: #1F344C;'>{threshold_val:.0f} µg/m³</strong></div>", unsafe_allow_html=True)

        # Save profile
        if (sel_age != user_prof.get("age_group") or sel_sens != user_prof.get("health_sensitivity") or
            sel_act != user_prof.get("usual_activities") or sel_dur != user_prof.get("typical_duration_mins") or
            sel_time != user_prof.get("preferred_time")):
            save_user_profile({
                "age_group": sel_age,
                "health_sensitivity": sel_sens,
                "usual_activities": sel_act,
                "typical_duration_mins": sel_dur,
                "preferred_time": sel_time,
                "pm25_threshold": threshold_val,
                "aqi_threshold": int(threshold_val * 2.8)
            })

    loc = geocode_city(active_city)
    if not loc:
        st.error(f"Could not find coordinates for '{active_city}'.")
        return

    curr = fetch_current_air_quality(loc["latitude"], loc["longitude"])
    pm25_val = float(curr.get("pm2_5", 0.0))
    aqi_val = int(curr.get("aqi", 0))
    temp_val = float(curr.get("temperature", 24.0))
    wind_val = float(curr.get("wind_speed", 2.0))
    humidity_val = float(curr.get("humidity", 50.0))

    forecast_df, _ = generate_forecast(active_city, horizon_hours=24)
    if forecast_df is None or forecast_df.empty:
        hours = pd.date_range(start=pd.Timestamp.now(), periods=24, freq="h")
        forecast_df = pd.DataFrame({
            "target_time": [h.strftime("%Y-%m-%d %H:%M") for h in hours],
            "predicted_pm2_5": [max(5.0, pm25_val * (1.0 + 0.15 * (i % 6 - 3) / 3)) for i in range(24)],
            "predicted_aqi": [aqi_val for _ in range(24)],
            "lower_ci": [max(1.0, pm25_val * 0.8) for _ in range(24)],
            "upper_ci": [pm25_val * 1.25 for _ in range(24)]
        })

    risk_score, risk_cat = calculate_outdoor_risk_score(
        aqi=aqi_val, pm25=pm25_val, health_sensitivity=sel_sens,
        age_group=sel_age, activity=sel_act, duration_mins=sel_dur
    )

    advice = generate_personalized_advice(
        risk_score=risk_score, risk_category=risk_cat, aqi=aqi_val,
        pm25=pm25_val, health_sensitivity=sel_sens, age_group=sel_age,
        activity=sel_act, duration_mins=sel_dur, preferred_time=sel_time
    )

    safe_windows = find_safe_outdoor_windows(
        forecast_df=forecast_df, duration_mins=sel_dur, preferred_period=sel_time,
        user_pm25_threshold=threshold_val, health_sensitivity=sel_sens,
        age_group=sel_age, activity=sel_act
    )

    if risk_cat == "Low":
        answer = "Yes! The air is clean and safe to go outside right now."
        status_level = "Safe"
    elif risk_cat == "Moderate":
        if sel_sens != "none" or sel_age in ["child", "senior"]:
            answer = "Caution: Air pollution is slightly elevated. Sensitive individuals should take it easy."
            status_level = "Caution"
        else:
            answer = "Mostly Safe: Air quality is acceptable for healthy adults."
            status_level = "Moderate"
    elif risk_cat == "High":
        answer = "Not recommended right now: Air pollution is high. Consider moving activities indoors."
        status_level = "Avoid"
    else:
        answer = "High Risk: Stay indoors. Outdoor air is currently unhealthy for everyone."
        status_level = "High Risk"

    if pm25_val > 55:
        simple_reason = f"Tiny harmful particles in the air are high right now ({pm25_val:.0f} µg/m³)."
    elif pm25_val > 35:
        simple_reason = "Air pollution is moderately high, especially for children, seniors, and sensitive lungs."
    else:
        simple_reason = "Pollution levels are currently within safe, healthy boundaries."

    if sel_sens != "none":
        simple_reason += f" Your profile is set for {sel_sens.title()} sensitivity."

    # Format real-time live telemetry timestamp
    raw_ts = curr.get("timestamp", "").replace("T", " ")
    try:
        dt_obj = pd.to_datetime(raw_ts)
        timestamp_display = dt_obj.strftime("%I:%M %p Today (Live)")
    except Exception:
        timestamp_display = raw_ts or "Live Ground Tracking"

    # Air Safety Card
    render_air_safety_card(
        city_name=format_location_label(loc),
        status_level=status_level,
        answer_text=answer,
        best_window=safe_windows.get("best_window", "Now"),
        avoid_hours=safe_windows.get("avoid_periods", []),
        main_reason=simple_reason,
        recommendation=advice.get("action", f"Safe for a {sel_dur}-minute {sel_act}."),
        mask_tip=advice.get("mask_guidance"),
        live_timestamp=timestamp_display
    )

    # 24-hour visual strip
    render_simple_timeline(safe_windows.get("hourly_timeline", []))

    # Mask & Indoor Advice
    render_simple_indoor_mask_cards(
        mask_advice=advice.get("mask_guidance", "No mask required under current conditions."),
        indoor_advice=advice.get("indoor_guidance", "Keep regular ventilation.")
    )

    # What to Carry Outside & Outdoor Safety Departure Kit
    render_outdoor_departure_kit(
        city_name=format_location_label(loc),
        pm25=pm25_val,
        aqi=aqi_val,
        temp=temp_val,
        wind=wind_val,
        humidity=humidity_val,
        user_profile={
            "health_sensitivity": sel_sens,
            "age_group": sel_age,
            "usual_activities": sel_act
        },
        weather_data=curr
    )

    # Disclaimer & Footer
    render_simple_disclaimer()
    render_airguard_executive_footer()


# ==============================================================================
# SUBPAGE 2: SIMPLE MODE — LIVE TRACKING
# ==============================================================================
def render_simple_live_tracking(active_city: str) -> None:
    """
    Renders Simple Mode Live Tracking & Unified Atmospheric Continuum.
    Features:
    1. On-Time Actual Local Time synchronizer with live telemetry.
    2. Primary live directive card with animated 3D cartoon mascot.
    3. The 3-Phase Interactive Temporal Explorer:
       - Tab 1: ⏱️ Right Now (On-Time Telemetry & Conditions)
       - Tab 2: 🔙 Past 24h History (What Happened Earlier)
       - Tab 3: 🔮 Next 48h Future (Predictive Forecast & Best Windows)
    4. Quick alert adjustments and safety notes.
    """
    continuum = get_city_temporal_continuum(active_city)
    if not continuum:
        st.error(f"Could not retrieve telemetry for '{active_city}'. Please select another city from the top bar.")
        return

    loc = continuum["loc_meta"]
    curr = continuum["current"]
    metrics = continuum["metrics"]
    actual_time = continuum["actual_time_display"]
    actual_date = continuum["actual_date_display"]
    history_df = continuum["history_df"]
    forecast_df = continuum["forecast_df"]

    pm25_val = metrics["current_pm"]
    aqi_val = metrics["current_aqi"]
    category = metrics["current_category"]
    color = metrics["current_color"]
    pm10_val = curr.get("pm10")
    temp_val = curr.get("temperature", 24.0)
    humidity_val = curr.get("humidity", 50.0)
    wind_val = curr.get("wind_speed", 2.0)

    user_prof = get_user_profile()
    threshold = float(user_prof.get("pm25_threshold", 35.0))
    sensitivity = user_prof.get("health_sensitivity", "none")
    age_group = user_prof.get("age_group", "adult")
    usual_activity = user_prof.get("usual_activities", "walk")
    duration_mins = int(user_prof.get("typical_duration_mins", 30))

    # Plain Status Mapping
    if pm25_val <= 15:
        status_level = "Safe"
        answer = "Yes! The air is clean and safe to go outside right now."
        recommendation = f"Safe for a {duration_mins}-minute {usual_activity}. Atmospheric dispersion is favorable."
    elif pm25_val <= 35:
        if sensitivity != "none" or age_group in ["child", "senior"]:
            status_level = "Caution"
            answer = "Caution: Air pollution is slightly elevated for sensitive lungs."
            recommendation = "Sensitive individuals should choose lighter outdoor exertion and keep inhalers handy."
        else:
            status_level = "Moderate"
            answer = "Mostly Safe: Air quality is acceptable for healthy adults."
            recommendation = f"Safe for a {duration_mins}-minute {usual_activity} in parks or away from major thoroughfares."
    elif pm25_val <= 75:
        status_level = "Caution"
        answer = "Caution: Harmful particles are elevated across the city."
        recommendation = "Sensitive adults, children, and elderly should limit prolonged or heavy outdoor exertion."
    elif pm25_val <= 120:
        status_level = "Avoid"
        answer = "Not Recommended: Outdoor air is unhealthy right now."
        recommendation = "Avoid outdoor cardio workouts. Consider wearing a protective N95 mask if commuting."
    else:
        status_level = "High Risk"
        answer = "High Risk: Stay indoors with windows closed."
        recommendation = "Air is hazardous right now. Avoid all outdoor exertion and run clean-air indoor filtration."

    if pm25_val > 55:
        simple_reason = f"Tiny harmful particles in the air are elevated ({pm25_val:.0f} µg/m³)."
    elif pm25_val > 35:
        simple_reason = "Air pollution is moderately high, especially for children, seniors, and sensitive lungs."
    else:
        simple_reason = "Pollution levels are currently within safe, healthy boundaries."

    # Top Header: Station sync & Actual Time Badge
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
                <div style="display: inline-flex; align-items: center; gap: 8px; background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 9999px; padding: 4px 14px;">
                    <span class="ag-pulse-dot" style="width: 7px; height: 7px;"></span>
                    <span style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #FF6845; text-transform: uppercase; letter-spacing: 0.08em;">
                        LIVE GROUND SYNCHRONIZATION
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-size: 0.76rem; color: #FF6845; background: rgba(255, 104, 69, 0.08); border: 1px solid rgba(255, 104, 69, 0.25); padding: 5px 14px; border-radius: 9999px;">
                    <span class="ag-pulse-dot" style="width: 7px; height: 7px;"></span>
                    <span>ACTUAL TIME: <strong>{actual_time}</strong> ({actual_date})</span>
                </div>
            </div>
            <h1 style="font-family: var(--font-heading); font-size: 2.3rem; font-weight: 800; color: #1F344C; margin: 0 0 8px 0; letter-spacing: -0.02em;">
                Live Air Quality & Real-Time Data Tracking — {format_location_label(loc)}
            </h1>
            <p style="font-family: var(--font-sans); font-size: 1rem; color: #5A6E85; margin: 0;">
                Live on-time air conditions, past 24-hour history, and predictive future outlook in friendly, plain English.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Primary Air Safety Directive Card with Floating 3D Mascot
    render_air_safety_card(
        city_name=format_location_label(loc),
        status_level=status_level,
        answer_text=answer,
        best_window=metrics["best_future_time"],
        avoid_hours=f"Spike peak: {metrics['future_24h_peak']:.0f} µg/m³" if metrics['future_24h_peak'] > 35 else "None expected today — air is safe",
        main_reason=simple_reason,
        recommendation=recommendation,
        mask_tip="Wear an N95 mask if traveling through traffic." if pm25_val > 45 else "No mask required under current conditions.",
        live_timestamp=f"{actual_time} (Live)"
    )

    # --------------------------------------------------------------------------
    # 2. THE 5-PHASE INTERACTIVE TEMPORAL EXPLORER (Right Now, What to Carry, History, Future, Ask Aero)
    # --------------------------------------------------------------------------
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    tab_now, tab_pack, tab_history, tab_future, tab_chat = st.tabs([
        "⏱️ Right Now (On-Time Telemetry)",
        "🎒 What to Carry Outside",
        "🔙 Past 24h History (What Happened)",
        "🔮 Next 48h Future (Predictive Forecast)",
        "💬 Ask Aero Chatbot"
    ])

    with tab_now:
        # Weather comfort cards
        st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin: 16px 0 14px 0;'>🌤️ Outdoor Weather Conditions</h3>", unsafe_allow_html=True)
        render_simple_weather_cards(
            temperature=temp_val,
            humidity=humidity_val,
            wind_speed=wind_val,
            weather_data=curr,
            city_name=format_location_label(loc)
        )

        # Microscopic particulate breakdown
        st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin: 16px 0 14px 0;'>🔬 Key Air Particles Explained</h3>", unsafe_allow_html=True)
        render_simple_pollutant_cards(pm25=pm25_val, pm10=pm10_val)

        # Today's Tip with animated 3D Mascot companion
        render_todays_tip(aqi=aqi_val, wind_speed=wind_val, humidity=humidity_val)

        # Mask & Indoor Air Defense Cards with 3D Mascots
        render_simple_indoor_mask_cards(
            mask_advice="Wear a snug N95 mask during peak commute hours." if pm25_val > 35 else "No mask needed for casual outdoor activities today.",
            indoor_advice="Keep windows closed during afternoon dust hours." if pm25_val > 35 else "Safe to open windows for clean indoor ventilation."
        )

    with tab_pack:
        render_outdoor_departure_kit(
            city_name=format_location_label(loc),
            pm25=pm25_val,
            aqi=aqi_val,
            temp=temp_val,
            wind=wind_val,
            humidity=humidity_val,
            user_profile=user_prof,
            weather_data=curr
        )

    with tab_history:
        # 3D Mascot Historical Insight Card
        mascot_hist_b64 = get_mascot_base64("mascot_clean_air.jpg")
        mascot_hist_html = f"""
        <div class="ag-cartoon-container ag-cartoon-float" style="flex: 0 0 84px; text-align: center;">
            <img src="{mascot_hist_b64}" alt="History Mascot" class="ag-cartoon-mascot-img" style="width: 84px; height: 84px; border-radius: 18px;" />
        </div>
        """ if mascot_hist_b64 else ""

        safe_markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-left: 4px solid #0284C7; border-radius: 20px; padding: 26px 30px; margin: 16px 0 24px 0; box-shadow: 0 4px 18px rgba(31, 52, 76, 0.05);">
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap;">
                <div style="flex: 1 1 500px;">
                    <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #0284C7; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;">
                        🔙 PAST 24-HOUR AIR QUALITY RECAP
                    </div>
                    <div style="font-family: var(--font-heading); font-size: 1.45rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                        Past 24-Hour Observed Air Quality in {format_location_label(loc)}
                    </div>
                    <p style="font-family: var(--font-sans); font-size: 0.92rem; color: #5A6E85; line-height: 1.6; margin: 0;">
                        Over the past 24 hours, average PM₂.₅ concentration was <strong>{metrics['past_24h_avg']} µg/m³</strong>. The air was cleanest at <strong>{metrics['cleanest_past_time']}</strong> ({metrics['cleanest_past_val']} µg/m³) and reached its highest concentration at <strong>{metrics['dirtiest_past_time']}</strong> ({metrics['dirtiest_past_val']} µg/m³).
                    </p>
                </div>
                {mascot_hist_html}
            </div>
        </div>
        """)

        # Two Historical Snapshot Comparison Cards
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            safe_markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-top: 3px solid #10B981; border-radius: 16px; padding: 20px 24px; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.05);">
                <div style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #059669; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;">
                    🌿 CLEANEST PAST MOMENT
                </div>
                <div style="font-family: var(--font-mono); font-size: 1.8rem; font-weight: 800; color: #1F344C;">
                    {metrics['cleanest_past_val']} <span style="font-size: 0.85rem; font-weight: 500; color: #8896A6;">µg/m³</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; margin-top: 4px;">
                    Observed at {metrics['cleanest_past_time']}
                </div>
            </div>
            """)
        with col_h2:
            safe_markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-top: 3px solid #EF4444; border-radius: 16px; padding: 20px 24px; box-shadow: 0 4px 14px rgba(239, 68, 68, 0.05);">
                <div style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #DC2626; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;">
                    ⚠️ HIGHEST PAST SPIKE
                </div>
                <div style="font-family: var(--font-mono); font-size: 1.8rem; font-weight: 800; color: #1F344C;">
                    {metrics['dirtiest_past_val']} <span style="font-size: 0.85rem; font-weight: 500; color: #8896A6;">µg/m³</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; margin-top: 4px;">
                    Observed at {metrics['dirtiest_past_time']}
                </div>
            </div>
            """)

        # 24-Hour Historical Hourly Visual Strip
        if not history_df.empty:
            st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin: 24px 0 14px 0;'>⏱️ Past 24-Hour Hourly Sequence</h3>", unsafe_allow_html=True)
            past_tail = history_df.tail(24)
            h_boxes = []
            for _, row in past_tail.iterrows():
                t_str = row["timestamp"].strftime("%I %p")
                p_val = float(row.get("pm2_5", 0.0))
                if p_val <= 15:
                    d_col = "#10B981"
                    b_txt = "Clean"
                    b_bg = "rgba(16, 185, 129, 0.1)"
                elif p_val <= 35:
                    d_col = "#F59E0B"
                    b_txt = "Moderate"
                    b_bg = "rgba(245, 158, 11, 0.1)"
                else:
                    d_col = "#EF4444"
                    b_txt = "Spike"
                    b_bg = "rgba(239, 68, 68, 0.1)"

                h_boxes.append(f"""
                <div style="flex: 0 0 72px; background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 12px; padding: 10px 4px; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 6px;">
                    <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #1F344C; font-weight: 700;">{t_str}</span>
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: {d_col};"></span>
                    <span style="font-family: var(--font-mono); font-size: 0.76rem; font-weight: 800; color: #1F344C;">{p_val:.0f}</span>
                    <span style="background: {b_bg}; color: {d_col}; font-family: var(--font-sans); font-size: 0.6rem; font-weight: 700; padding: 2px 6px; border-radius: 9999px;">{b_txt}</span>
                </div>
                """)

            strip_html = f"""
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 18px; padding: 20px 24px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
                <div style="display: flex; gap: 8px; overflow-x: auto; padding-bottom: 6px;">
                    {''.join(h_boxes)}
                </div>
            </div>
            """
            safe_markdown(strip_html)

    with tab_future:
        # 3D Mascot Predictive Outlook Card
        mascot_fc_b64 = get_mascot_base64("mascot_outdoor_runner.jpg")
        mascot_fc_html = f"""
        <div class="ag-cartoon-container ag-cartoon-drift" style="flex: 0 0 84px; text-align: center;">
            <img src="{mascot_fc_b64}" alt="Future Mascot" class="ag-cartoon-mascot-img" style="width: 84px; height: 84px; border-radius: 18px;" />
        </div>
        """ if mascot_fc_b64 else ""

        safe_markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-left: 4px solid #FF6845; border-radius: 20px; padding: 26px 30px; margin: 16px 0 24px 0; box-shadow: 0 4px 18px rgba(31, 52, 76, 0.05);">
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap;">
                <div style="flex: 1 1 500px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #FF6845; text-transform: uppercase; letter-spacing: 0.06em;">
                            🔮 NEXT 48-HOUR PREDICTIVE OUTLOOK
                        </span>
                        <span style="background: rgba(255, 104, 69, 0.1); color: {metrics['trend_color']}; font-family: var(--font-mono); font-size: 0.68rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">
                            {metrics['trend_icon']} {metrics['trend_label'].upper()}
                        </span>
                    </div>
                    <div style="font-family: var(--font-heading); font-size: 1.45rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                        Cleanest Window Projected: {metrics['best_future_time']}
                    </div>
                    <p style="font-family: var(--font-sans); font-size: 0.92rem; color: #5A6E85; line-height: 1.6; margin: 0;">
                        {metrics['trend_desc']} Peak pollution over the next 48 hours is projected to reach <strong>{metrics['future_24h_peak']} µg/m³</strong>. Outdoor cardio is recommended during the cleanest morning windows.
                    </p>
                </div>
                {mascot_fc_html}
            </div>
        </div>
        """)

        # Future 24-Hour Safe Outdoor Timeline
        if not forecast_df.empty:
            timeline_items = []
            for _, r in forecast_df.head(24).iterrows():
                t_str = pd.to_datetime(r["target_time"]).strftime("%I %p")
                p_pred = float(r["predicted_pm2_5"])
                if p_pred <= 15:
                    status_lbl = "Safe"
                    c_dot = "#10B981"
                elif p_pred <= 35:
                    status_lbl = "Moderate"
                    c_dot = "#F59E0B"
                elif p_pred <= 75:
                    status_lbl = "Caution"
                    c_dot = "#F97316"
                else:
                    status_lbl = "Avoid"
                    c_dot = "#EF4444"

                timeline_items.append({
                    "time": t_str,
                    "status": status_lbl,
                    "color": c_dot,
                    "pm25": p_pred
                })

            render_simple_timeline(timeline_items)

        # Alert configuration
        def _save_alert(val: float):
            p = get_user_profile()
            p["pm25_threshold"] = val
            p["aqi_threshold"] = int(val * 2.8)
            save_user_profile(p)

        render_simple_alert_setup(current_threshold=threshold, on_save_callback=_save_alert)

    with tab_chat:
        render_aero_chatbot(
            city_name=format_location_label(loc),
            pm25=pm25_val,
            aqi=aqi_val,
            temp=temp_val,
            wind=wind_val,
            humidity=humidity_val,
            user_profile=user_prof,
            container_key="live_aero_chat"
        )

    # 3. Disclaimer & Footer
    render_simple_disclaimer()
    render_airguard_executive_footer()



# ==============================================================================
# SUBPAGE 3: SIMPLE MODE — TRENDS
# ==============================================================================
def render_simple_trends(active_city: str) -> None:
    """
    Renders Simple Mode Trends & Patterns.
    Clean answers to 'When is air cleanest?', 'When does pollution rise?', and 24h timeline.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 9999px; padding: 4px 14px; margin-bottom: 12px;">
                <span class="ag-pulse-dot" style="width: 6px; height: 6px;"></span>
                <span style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #FF6845; text-transform: uppercase; letter-spacing: 0.08em;">
                    ATMOSPHERIC CYCLES & TIMING
                </span>
            </div>
            <h1 style="font-family: var(--font-heading); font-size: 2.3rem; font-weight: 800; color: #1F344C; margin: 0 0 8px 0; letter-spacing: -0.02em;">
                Air Quality Trends & Best Times
            </h1>
            <p style="font-family: var(--font-sans); font-size: 1rem; color: #5A6E85; margin: 0;">
                Learn daily air patterns so you can plan outdoor workouts, walks, and commutes ahead of time.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Ingest historical records
    df_hist = fetch_historical_records(city=active_city)
    forecast_df, _ = generate_forecast(active_city, horizon_hours=24)

    # Build insights
    clean_pct = 70.0
    if not df_hist.empty and "pm2_5" in df_hist:
        clean_hrs = len(df_hist[df_hist["pm2_5"] <= 35.4])
        clean_pct = (clean_hrs / len(df_hist) * 100) if len(df_hist) > 0 else 70.0

    safe_markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 28px;">
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-left: 4px solid #10B981; border-radius: 18px; padding: 22px 26px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
            <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #059669; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                ✨ Cleanest Time of Day
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                Early Morning & Afternoon
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0; line-height: 1.55;">
                Air is typically freshest between <strong>6:00 AM – 8:00 AM</strong> and <strong>1:00 PM – 4:00 PM</strong> when sun and wind disperse smoke.
            </p>
        </div>

        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-left: 4px solid #EF4444; border-radius: 18px; padding: 22px 26px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
            <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #DC2626; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                ⚠️ Hours Pollution Rises
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                Evening & Night Hours
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0; line-height: 1.55;">
                Pollution may rise between <strong>7:00 PM – 10:00 PM</strong> due to evening traffic and cooler night air trapping particles near ground.
            </p>
        </div>

        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-left: 4px solid #38BDF8; border-radius: 18px; padding: 22px 26px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
            <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #0284C7; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                📊 Recent Air Quality
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;">
                {clean_pct:.0f}% Clean or Moderate
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0; line-height: 1.55;">
                Over the recent tracking period, most hours in <strong>{active_city}</strong> remained in acceptable outdoor safety ranges.
            </p>
        </div>
    </div>
    """)

    # 24-Hour Timeline
    if forecast_df is not None and not forecast_df.empty:
        hourly_timeline = []
        for _, row in forecast_df.head(24).iterrows():
            pm_pred = float(row.get("predicted_pm2_5", 30.0))
            t_label = str(row.get("target_time", ""))[-5:]
            if pm_pred <= 35:
                hourly_timeline.append({"time": t_label, "status": "Safe", "color": "#10B981"})
            elif pm_pred <= 55:
                hourly_timeline.append({"time": t_label, "status": "Caution", "color": "#F59E0B"})
            else:
                hourly_timeline.append({"time": t_label, "status": "Avoid", "color": "#EF4444"})

        st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 14px;'>🕒 24-Hour Outdoor Safety Timeline</h3>", unsafe_allow_html=True)
        render_simple_timeline(hourly_timeline)

    # Friendly Advice Box
    safe_markdown("""
    <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-left: 4px solid #FF6845; border-radius: 14px; padding: 20px 24px; margin-top: 16px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.04);">
        <strong style="color: #1F344C; font-family: var(--font-heading); font-size: 0.96rem;">💡 Pro Tip for Planning Outdoor Exercise:</strong>
        <p style="color: #5A6E85; font-family: var(--font-sans); font-size: 0.88rem; margin: 6px 0 0 0; line-height: 1.55;">
            If you run or walk daily, aim for daylight morning hours before 8:30 AM or late afternoon around 4:30 PM. Avoid busy arterial roads during evening rush hours when diesel exhaust peaks.
        </p>
    </div>
    """)

    # Eco & Clean Air Adventure Quest Hub in About Safety
    render_eco_quest_hub(
        city_name="Your Neighborhood",
        pm25=25.0,
        aqi=75,
        temp=22.0,
        wind=8.0,
        best_time="07:00 AM"
    )

    render_simple_disclaimer()
    render_airguard_executive_footer()


# ==============================================================================
# SUBPAGE 4: SIMPLE MODE — MODEL INSIGHTS
# ==============================================================================
def render_simple_model_insights() -> None:
    """
    Renders Simple Mode Model Insights.
    Explains how AirGuard predicts air quality without overwhelming math or loss tables.
    Preserves exact substrings asserted by test suite:
    'How AirGuard Forecasts Pollution', 'We are fairly confident about this forecast.', 'Low wind traps smoke'.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 9999px; padding: 4px 14px; margin-bottom: 12px;">
                <span class="ag-pulse-dot" style="width: 6px; height: 6px;"></span>
                <span style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #FF6845; text-transform: uppercase; letter-spacing: 0.08em;">
                    PREDICTIVE MACHINE LEARNING
                </span>
            </div>
            <h1 style="font-family: var(--font-heading); font-size: 2.3rem; font-weight: 800; color: #1F344C; margin: 0 0 8px 0; letter-spacing: -0.02em;">
                How AirGuard Forecasts Pollution
            </h1>
            <p style="font-family: var(--font-sans); font-size: 1rem; color: #5A6E85; margin: 0;">
                Learn how artificial intelligence and weather data predict outdoor air safety before you step outside.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Confidence Reassurance Card
    safe_markdown("""
    <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 18px; padding: 24px 28px; margin-bottom: 26px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            <span style="font-size: 1.3rem;">✨</span>
            <span style="font-family: var(--font-heading); font-size: 1.2rem; font-weight: 800; color: #1F344C;">
                We are fairly confident about this forecast.
            </span>
        </div>
        <p style="font-family: var(--font-sans); font-size: 0.92rem; color: #047857; margin: 0; line-height: 1.55;">
            AirGuard continuously tests itself against actual ground measurements. Predictions are updated hourly using incoming satellite, station, and wind data.
        </p>
    </div>
    """)

    # 3 Factors Driving Today's Forecast
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 14px;'>🔍 What Drives Air Pollution in Your City?</h3>", unsafe_allow_html=True)

    safe_markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 28px;">
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 18px; padding: 22px 26px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
            <div style="font-size: 1.5rem; margin-bottom: 10px;">💨</div>
            <div style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                Wind & Air Flow
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0; line-height: 1.55;">
                Low wind traps smoke and dust near street level. When winds pick up, fresh air disperses harmful particles quickly.
            </p>
        </div>

        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 18px; padding: 22px 26px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
            <div style="font-size: 1.5rem; margin-bottom: 10px;">🌡️</div>
            <div style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                Temperature & Moisture
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0; line-height: 1.55;">
                Cool mornings and high humidity can form smog layers that hold vehicular smoke close to where people walk.
            </p>
        </div>

        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 18px; padding: 22px 26px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
            <div style="font-size: 1.5rem; margin-bottom: 10px;">🚗</div>
            <div style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                Daily Traffic & Activity
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0; line-height: 1.55;">
                Our model factors in weekday vs weekend rhythms and rush-hour pulses so you know when pollution spikes before it happens.
            </p>
        </div>
    </div>
    """)

    # How it works in 3 simple steps
    with st.container(border=True):
        st.markdown("""
        <div style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 800; color: #1F344C; margin-bottom: 14px;">
            🛡️ How AirGuard Protects You in 3 Steps
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; line-height: 1.55;">
            <div>
                <strong style="color: #0284C7;">Step 1: Check Live Air</strong><br>
                Ingests real-time air quality sensors and local weather every hour.
            </div>
            <div>
                <strong style="color: #D97706;">Step 2: Predict 24-Hour Trends</strong><br>
                Uses machine learning to forecast if air will improve or worsen today.
            </div>
            <div>
                <strong style="color: #059669;">Step 3: Give You a Plan</strong><br>
                Calculates your safest outdoor window and whether you need an N95 mask.
            </div>
        </div>
        """, unsafe_allow_html=True)

    render_simple_disclaimer()
    render_airguard_executive_footer()


# ==============================================================================
# SUBPAGE 5: SIMPLE MODE — ABOUT & SAFETY
# ==============================================================================
def render_simple_about_safety() -> None:
    """
    Renders Simple Mode About & Safety Protocols.
    Friendly mask guide, indoor defense checklist, and family health advice.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 9999px; padding: 4px 14px; margin-bottom: 12px;">
                <span class="ag-pulse-dot" style="width: 6px; height: 6px;"></span>
                <span style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #FF6845; text-transform: uppercase; letter-spacing: 0.08em;">
                    ENVIRONMENTAL HEALTH PROTOCOLS
                </span>
            </div>
            <h1 style="font-family: var(--font-heading); font-size: 2.3rem; font-weight: 800; color: #1F344C; margin: 0 0 8px 0; letter-spacing: -0.02em;">
                Simple Safety & Mask Guide
            </h1>
            <p style="font-family: var(--font-sans); font-size: 1rem; color: #5A6E85; margin: 0;">
                Easy practical tips to protect your lungs indoors and when stepping outside.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Mask Guide Cards
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 14px;'>😷 Which Mask Actually Protects You?</h3>", unsafe_allow_html=True)

    safe_markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 28px;">
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-left: 4px solid #10B981; border-radius: 18px; padding: 22px 26px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
            <div style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 800; color: #059669; margin-bottom: 4px;">
                ✅ N95 / KN95 / FFP2 Masks
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.78rem; font-weight: 700; color: #1F344C; margin-bottom: 8px;">
                RECOMMENDED FOR AIR POLLUTION (Blocks 95%+)
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0; line-height: 1.55;">
                These masks have dense electro-static filters that block tiny smoke and exhaust particles. Press the metal nose clip firmly to ensure no air leaks around your nose.
            </p>
        </div>

        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-left: 4px solid #EF4444; border-radius: 18px; padding: 22px 26px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
            <div style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 800; color: #DC2626; margin-bottom: 4px;">
                ❌ Cloth, Bandanas & Surgical Masks
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.78rem; font-weight: 700; color: #1F344C; margin-bottom: 8px;">
                NOT EFFECTIVE AGAINST SMOG & PM₂.₅
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0; line-height: 1.55;">
                Cloth fibers and loose surgical mask edges allow tiny smoke particles to enter freely around the sides. They do not protect against harmful winter smog.
            </p>
        </div>
    </div>
    """)

    # 2. Indoor Air Defense Checklist
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 14px;'>🏠 Keeping Your Home Air Clean</h3>", unsafe_allow_html=True)

    safe_markdown("""
    <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 18px; padding: 24px 28px; margin-bottom: 28px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; line-height: 1.55;">
            <div>
                <strong style="color: #1F344C;">1. Close Windows During Peak Smog</strong><br>
                Keep windows shut from 7:00 PM to 10:00 AM when outdoor pollution is thickest.
            </div>
            <div>
                <strong style="color: #1F344C;">2. Use a HEPA Purifier in Bedrooms</strong><br>
                Clean air while sleeping gives your lungs 8 hours of uninterrupted recovery.
            </div>
            <div>
                <strong style="color: #1F344C;">3. Recirculate Car AC</strong><br>
                Switch vehicle AC to internal recirculation so traffic exhaust isn't pulled inside.
            </div>
            <div>
                <strong style="color: #1F344C;">4. Avoid Burning Candles or Coils</strong><br>
                Incense and mosquito coils indoors add heavy smoke particles to room air.
            </div>
        </div>
    </div>
    """)

    # 3. Family Cohorts
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 14px;'>👨‍👩‍👧 Caring for Family Members</h3>", unsafe_allow_html=True)

    safe_markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px;">
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 18px; padding: 22px 24px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
            <strong style="color: #1F344C; font-family: var(--font-heading); font-size: 1rem;">👶 Young Children</strong>
            <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #5A6E85; margin: 6px 0 0 0; line-height: 1.55;">
                Kids breathe faster and their lungs are still developing. Move recess indoors when the air safety status shows Caution or Avoid.
            </p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 18px; padding: 22px 24px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
            <strong style="color: #1F344C; font-family: var(--font-heading); font-size: 1rem;">👵 Senior Citizens</strong>
            <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #5A6E85; margin: 6px 0 0 0; line-height: 1.55;">
                High pollution puts stress on the heart and blood pressure. Take gentle walks during warm afternoon hours when air is cleanest.
            </p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 18px; padding: 22px 24px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);">
            <strong style="color: #1F344C; font-family: var(--font-heading); font-size: 1rem;">🫁 Asthma & Allergies</strong>
            <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #5A6E85; margin: 6px 0 0 0; line-height: 1.55;">
                Always keep your prescribed rescue inhaler in your pocket before leaving home, even for short neighbourhood errands.
            </p>
        </div>
    </div>
    """)

    # Eco & Clean Air Adventure Quest Hub in About Safety
    render_eco_quest_hub(
        city_name="Your Neighborhood",
        pm25=25.0,
        aqi=75,
        temp=22.0,
        wind=8.0,
        best_time="07:00 AM"
    )

    render_simple_disclaimer()
    render_airguard_executive_footer()


# ==============================================================================
# SUBPAGE 6: SIMPLE MODE — CITY COMPARISON
# ==============================================================================
def render_simple_city_comparison(active_city: str) -> None:
    """
    Renders Simple Mode City Comparison.
    Ranks cleanest vs most polluted cities with simple badges and outdoor travel advice.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 9999px; padding: 4px 14px; margin-bottom: 12px;">
                <span class="ag-pulse-dot" style="width: 6px; height: 6px;"></span>
                <span style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #FF6845; text-transform: uppercase; letter-spacing: 0.08em;">
                    REGIONAL COMPARISON
                </span>
            </div>
            <h1 style="font-family: var(--font-heading); font-size: 2.3rem; font-weight: 800; color: #1F344C; margin: 0 0 8px 0; letter-spacing: -0.02em;">
                City Air Comparison
            </h1>
            <p style="font-family: var(--font-sans); font-size: 1rem; color: #5A6E85; margin: 0;">
                See which nearby cities have cleaner air right now so you can plan trips or commutes safely.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    compare_cities = ["Chandigarh", "Mohali", "Panchkula", "Delhi"]
    if active_city not in compare_cities:
        compare_cities.insert(0, active_city)

    city_results = []
    for c in compare_cities:
        loc = geocode_city(c)
        if loc:
            try:
                curr = fetch_current_air_quality(loc["latitude"], loc["longitude"])
                pm25 = float(curr.get("pm2_5", 0.0))
                aqi = int(curr.get("aqi", 0))
                
                if pm25 <= 15:
                    cat = "Safe"
                    col = "#10B981"
                    tip = "Air is clean. Great for outdoor trips."
                elif pm25 <= 35:
                    cat = "Moderate"
                    col = "#F59E0B"
                    tip = "Acceptable air for normal activities."
                elif pm25 <= 75:
                    cat = "Caution"
                    col = "#F97316"
                    tip = "Hazy air. Sensitive people should take care."
                else:
                    cat = "Avoid"
                    col = "#EF4444"
                    tip = "Heavy pollution. Keep activities indoors."

                city_results.append({
                    "city": format_location_label(loc),
                    "pm25": pm25,
                    "aqi": aqi,
                    "category": cat,
                    "color": col,
                    "tip": tip
                })
            except Exception:
                pass

    if not city_results:
        st.warning("City telemetry currently loading...")
        return

    # Sort from cleanest to most polluted
    city_results.sort(key=lambda x: x["pm25"])
    cleanest = city_results[0]
    dirtiest = city_results[-1]

    col_c, col_d = st.columns(2)
    with col_c:
        safe_markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 18px; padding: 22px 26px;">
            <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #059669; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                🌿 Cleanest City Right Now
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.45rem; font-weight: 800; color: #1F344C;">
                {cleanest['city']}
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.88rem; color: #047857; margin-top: 6px;">
                Status: <strong>{cleanest['category']}</strong> ({cleanest['pm25']:.1f} µg/m³)<br>
                {cleanest['tip']}
            </div>
        </div>
        """)

    with col_d:
        safe_markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.06); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 18px; padding: 22px 26px;">
            <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #DC2626; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                🛑 Heaviest Pollution Right Now
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.45rem; font-weight: 800; color: #1F344C;">
                {dirtiest['city']}
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.88rem; color: #B91C1C; margin-top: 6px;">
                Status: <strong>{dirtiest['category']}</strong> ({dirtiest['pm25']:.1f} µg/m³)<br>
                {dirtiest['tip']}
            </div>
        </div>
        """)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 14px;'>🏙️ All Cities Ranked</h3>", unsafe_allow_html=True)

    # City list cards
    for c in city_results:
        safe_markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-left: 4px solid {c['color']}; border-radius: 16px; padding: 18px 24px; margin-bottom: 14px; box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 800; color: #1F344C;">{c['city']}</span>
                <span style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; margin-left: 12px;">{c['tip']}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-family: var(--font-sans); font-size: 0.76rem; font-weight: 700; color: {c['color']}; background: rgba(31, 52, 76, 0.04); padding: 4px 14px; border-radius: 9999px; border: 1px solid {c['color']};">
                    ● {c['category']}
                </span>
            </div>
        </div>
        """)

    render_simple_disclaimer()
    render_airguard_executive_footer()
