"""
Simple Mode Presentation Views for AirGuard.
Orchestrates clear, non-technical, friendly user experiences.
Reuses the exact same underlying telemetry, ML forecasting, and risk-engine logic.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional

from src.database import get_user_profile, save_user_profile
from src.data_collection import geocode_city, fetch_current_air_quality
from src.predict import generate_forecast
from src.safety_rules import (
    calculate_outdoor_risk_score,
    generate_personalized_advice,
    find_safe_outdoor_windows
)
from app.components.design_system import format_location_label, safe_markdown
from app.components.simple_cards import (
    render_air_safety_card,
    render_simple_timeline,
    render_todays_tip,
    render_simple_alert_setup,
    render_simple_disclaimer,
    render_simple_weather_cards,
    render_simple_pollutant_cards,
    render_simple_indoor_mask_cards
)
from src.config import PRESET_CITIES
from src.database import fetch_historical_records, fetch_all_locations


def render_simple_home(active_city: str) -> None:
    """
    Renders the dedicated Simple Mode homepage for AirGuard.
    Heading: 'Is it safe for me to go outside today?'
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

    # Main Homepage Heading
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h1 style="font-family: var(--font-heading); font-size: 2.1rem; font-weight: 800; color: #FFFFFF; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                Is it safe for me to go outside today?
            </h1>
            <p style="font-family: var(--font-sans); font-size: 0.95rem; color: #888888; margin: 0;">
                Personalized, friendly outdoor guidance based on live air quality and 24-hour forecasts.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Large Air Safety Card
    render_air_safety_card(
        city_name=city_display,
        status_level=status_level,
        answer_text=answer,
        best_window=best_win,
        avoid_hours=avoid_list,
        main_reason=simple_reason,
        recommendation=advice.get("action", f"Safe for a {duration_mins}-minute {usual_activity}."),
        mask_tip=advice.get("mask_guidance")
    )

    # 2. Simple 24-Hour Timeline
    render_simple_timeline(hourly_timeline)

    # 3. Two-Column Row: Today's Tip + Simple Alert Setup
    col_tip, col_alert = st.columns([1.1, 1.0])

    with col_tip:
        render_todays_tip(aqi=aqi_val, wind_speed=wind_val, humidity=humidity_val)

        # Friendly quick navigation shortcuts
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 8px;">
                    🎯 What would you like to do?
                </div>
                """,
                unsafe_allow_html=True
            )
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🛡️ Customize Safe Plan", key="simple_btn_plan", use_container_width=True):
                    st.switch_page("pages/1_My_Safe_Outdoor_Plan.py")
            with col_b2:
                if st.button("📡 View Weather & Air Details", key="simple_btn_live", use_container_width=True):
                    st.switch_page("pages/2_Live_Tracking.py")

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

    # 4. Prominent Safety Disclaimer
    render_simple_disclaimer()


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
        <div style="margin-bottom: 16px;">
            <h1 style="font-family: var(--font-heading); font-size: 2.1rem; font-weight: 800; color: #FFFFFF; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                My Safe Outdoor Plan
            </h1>
            <p style="font-family: var(--font-sans); font-size: 0.95rem; color: #888888; margin: 0;">
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
            st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.8rem; color: #FFFFFF;'>1. WHO IS GOING OUT?</strong>", unsafe_allow_html=True)
            age_opts = ["adult", "child", "senior"]
            cur_age = user_prof.get("age_group", "adult")
            sel_age = st.selectbox("Age Group", options=age_opts, index=age_opts.index(cur_age) if cur_age in age_opts else 0, format_func=lambda x: f"For: {x.title()}")

            sens_opts = ["none", "asthma", "allergy", "copd", "heart condition", "pregnancy", "other respiratory sensitivity"]
            cur_sens = user_prof.get("health_sensitivity", "none")
            sel_sens = st.selectbox("Health Sensitivity", options=sens_opts, index=sens_opts.index(cur_sens) if cur_sens in sens_opts else 0, format_func=lambda x: f"Sensitivity: {x.title()}")

        with col2:
            st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.8rem; color: #FFFFFF;'>2. WHAT ARE YOU DOING?</strong>", unsafe_allow_html=True)
            act_opts = ["walk", "run", "cycle", "outdoor play", "outdoor work", "commute"]
            cur_act = user_prof.get("usual_activities", "walk")
            sel_act = st.selectbox("Activity", options=act_opts, index=act_opts.index(cur_act) if cur_act in act_opts else 0, format_func=lambda x: f"Activity: {x.title()}")

            dur_opts = [15, 30, 45, 60, 90, 120]
            cur_dur = int(user_prof.get("typical_duration_mins", 30))
            sel_dur = st.select_slider("Duration", options=dur_opts, value=cur_dur if cur_dur in dur_opts else 30, format_func=lambda x: f"{x} Minutes")

        with col3:
            st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.8rem; color: #FFFFFF;'>3. WHEN DO YOU WANT TO GO?</strong>", unsafe_allow_html=True)
            time_opts = ["now", "morning", "afternoon", "evening", "tomorrow"]
            cur_time = user_prof.get("preferred_time", "now")
            sel_time = st.selectbox("Preferred Time", options=time_opts, index=time_opts.index(cur_time) if cur_time in time_opts else 0, format_func=lambda x: f"Time: {x.title()}")

            threshold_val = float(user_prof.get("pm25_threshold", 35.0))
            st.markdown(f"<div style='font-family: var(--font-sans); font-size: 0.78rem; color: #888888; margin-top: 10px;'>Alert comfort level: <strong>{threshold_val:.0f} µg/m³</strong></div>", unsafe_allow_html=True)

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

    # Air Safety Card
    render_air_safety_card(
        city_name=format_location_label(loc),
        status_level=status_level,
        answer_text=answer,
        best_window=safe_windows.get("best_window", "Now"),
        avoid_hours=safe_windows.get("avoid_periods", []),
        main_reason=simple_reason,
        recommendation=advice.get("action", f"Safe for a {sel_dur}-minute {sel_act}."),
        mask_tip=advice.get("mask_guidance")
    )

    # 24-hour visual strip
    render_simple_timeline(safe_windows.get("hourly_timeline", []))

    # Mask & Indoor Advice
    render_simple_indoor_mask_cards(
        mask_advice=advice.get("mask_guidance", "No mask required under current conditions."),
        indoor_advice=advice.get("indoor_guidance", "Keep regular ventilation.")
    )

    # Disclaimer
    render_simple_disclaimer()


# ==============================================================================
# SUBPAGE 2: SIMPLE MODE — LIVE TRACKING
# ==============================================================================
def render_simple_live_tracking(active_city: str) -> None:
    """
    Renders Simple Mode Live Tracking & Alerts.
    Clear safety status, friendly weather tiles, simple pollutant cards, and quick alert setup.
    """
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h1 style="font-family: var(--font-heading); font-size: 2.1rem; font-weight: 800; color: #FFFFFF; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                Live Air Quality & Weather
            </h1>
            <p style="font-family: var(--font-sans); font-size: 0.95rem; color: #888888; margin: 0;">
                Real-time outdoor air conditions and weather in plain, friendly language.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    loc = geocode_city(active_city)
    if not loc:
        st.error(f"Could not find coordinates for '{active_city}'.")
        return

    curr = fetch_current_air_quality(loc["latitude"], loc["longitude"])
    pm25_val = float(curr.get("pm2_5", 0.0))
    pm10_val = float(curr.get("pm10", 0.0)) if curr.get("pm10") is not None else None
    aqi_val = int(curr.get("aqi", 0))
    temp_val = float(curr.get("temperature", 24.0)) if curr.get("temperature") is not None else 24.0
    humidity_val = float(curr.get("humidity", 50.0)) if curr.get("humidity") is not None else 50.0
    wind_val = float(curr.get("wind_speed", 2.0)) if curr.get("wind_speed") is not None else 2.0

    user_prof = get_user_profile()
    threshold = float(user_prof.get("pm25_threshold", 35.0))

    # Plain Status Mapping
    if pm25_val <= 15:
        status = "Safe"
        status_text = "The air is clean and fresh right now."
        detail_msg = "Pollution levels are low. A great time for outdoor exercise, walking, or playing outside."
    elif pm25_val <= 35:
        status = "Moderate"
        status_text = "Air quality is acceptable for most people."
        detail_msg = "Healthy adults can enjoy outdoor activities. Sensitive individuals should take normal precautions."
    elif pm25_val <= 75:
        status = "Caution"
        status_text = "Air is unhealthy for sensitive individuals."
        detail_msg = "Tiny harmful particles in the air are elevated. Children, seniors, and anyone with asthma should shorten outdoor time."
    elif pm25_val <= 120:
        status = "Avoid"
        status_text = "Air is unhealthy right now."
        detail_msg = "Pollution is high. Avoid long outdoor runs or intense workouts. Consider wearing an N95 mask."
    else:
        status = "High Risk"
        status_text = "Air is hazardous today."
        detail_msg = "Stay indoors with windows closed. Keep air purifiers running."

    # Top Hero Status Card
    theme = {"Safe": "#10B981", "Moderate": "#F59E0B", "Caution": "#F97316", "Avoid": "#EF4444", "High Risk": "#D71921"}.get(status, "#10B981")
    safe_markdown(f"""
    <div style="background: #121212; border: 1px solid #242424; border-left: 5px solid {theme}; border-radius: 14px; padding: 24px 28px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
            <span style="font-family: var(--font-sans); font-size: 0.8rem; font-weight: 700; color: {theme}; text-transform: uppercase; letter-spacing: 0.05em;">
                ● Current Status: {status}
            </span>
            <span style="font-family: var(--font-mono); font-size: 0.74rem; color: #888888;">
                {format_location_label(loc)}
            </span>
        </div>
        <h2 style="font-family: var(--font-heading); font-size: 1.6rem; font-weight: 700; color: #FFFFFF; margin: 0 0 10px 0;">
            {status_text}
        </h2>
        <p style="font-family: var(--font-sans); font-size: 0.92rem; color: #CCCCCC; margin: 0; line-height: 1.5;">
            {detail_msg}
        </p>
    </div>
    """)

    # Friendly Weather Cards
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;'>🌤️ Outdoor Weather Conditions</h3>", unsafe_allow_html=True)
    render_simple_weather_cards(temperature=temp_val, humidity=humidity_val, wind_speed=wind_val)

    # Simplified Key Pollutants
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;'>🔍 Key Air Particles Explained</h3>", unsafe_allow_html=True)
    render_simple_pollutant_cards(pm25=pm25_val, pm10=pm10_val)

    # Alert Setup Row
    def _save_alert(val: float):
        p = get_user_profile()
        p["pm25_threshold"] = val
        p["aqi_threshold"] = int(val * 2.8)
        save_user_profile(p)

    render_simple_alert_setup(current_threshold=threshold, on_save_callback=_save_alert)

    # Disclaimer
    render_simple_disclaimer()


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
        <div style="margin-bottom: 16px;">
            <h1 style="font-family: var(--font-heading); font-size: 2.1rem; font-weight: 800; color: #FFFFFF; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                Air Quality Trends & Best Times
            </h1>
            <p style="font-family: var(--font-sans); font-size: 0.95rem; color: #888888; margin: 0;">
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
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 24px;">
        <div style="background: #121212; border: 1px solid #222222; border-left: 4px solid #10B981; border-radius: 12px; padding: 18px 22px;">
            <div style="font-family: var(--font-heading); font-size: 0.76rem; font-weight: 700; color: #10B981; text-transform: uppercase; margin-bottom: 6px;">
                ✨ Cleanest Time of Day
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                Early Morning & Afternoon
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #CCCCCC; margin: 0; line-height: 1.5;">
                Air is typically freshest between <strong>6:00 AM – 8:00 AM</strong> and <strong>1:00 PM – 4:00 PM</strong> when sun and wind disperse smoke.
            </p>
        </div>

        <div style="background: #121212; border: 1px solid #222222; border-left: 4px solid #EF4444; border-radius: 12px; padding: 18px 22px;">
            <div style="font-family: var(--font-heading); font-size: 0.76rem; font-weight: 700; color: #EF4444; text-transform: uppercase; margin-bottom: 6px;">
                ⚠️ Hours Pollution Rises
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                Evening & Night Hours
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #CCCCCC; margin: 0; line-height: 1.5;">
                Pollution may rise between <strong>7:00 PM – 10:00 PM</strong> due to evening traffic and cooler night air trapping particles near ground.
            </p>
        </div>

        <div style="background: #121212; border: 1px solid #222222; border-left: 4px solid #38BDF8; border-radius: 12px; padding: 18px 22px;">
            <div style="font-family: var(--font-heading); font-size: 0.76rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; margin-bottom: 6px;">
                📊 Recent Air Quality
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                {clean_pct:.0f}% Clean or Moderate
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #CCCCCC; margin: 0; line-height: 1.5;">
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

        st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 10px;'>🕒 24-Hour Outdoor Safety Timeline</h3>", unsafe_allow_html=True)
        render_simple_timeline(hourly_timeline)

    # Friendly Advice Box
    safe_markdown("""
    <div style="background: #141414; border: 1px solid #262626; border-radius: 10px; padding: 18px 22px; margin-top: 14px;">
        <strong style="color: #FFFFFF; font-family: var(--font-heading); font-size: 0.92rem;">💡 Pro Tip for Planning Outdoor Exercise:</strong>
        <p style="color: #AAAAAA; font-family: var(--font-sans); font-size: 0.84rem; margin: 6px 0 0 0; line-height: 1.5;">
            If you run or walk daily, aim for daylight morning hours before 8:30 AM or late afternoon around 4:30 PM. Avoid busy arterial roads during evening rush hours when diesel exhaust peaks.
        </p>
    </div>
    """)

    render_simple_disclaimer()


# ==============================================================================
# SUBPAGE 4: SIMPLE MODE — MODEL INSIGHTS
# ==============================================================================
def render_simple_model_insights() -> None:
    """
    Renders Simple Mode Model Insights.
    Explains how AirGuard predicts air quality without overwhelming math or loss tables.
    """
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h1 style="font-family: var(--font-heading); font-size: 2.1rem; font-weight: 800; color: #FFFFFF; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                How AirGuard Forecasts Pollution
            </h1>
            <p style="font-family: var(--font-sans); font-size: 0.95rem; color: #888888; margin: 0;">
                Learn how artificial intelligence and weather data predict outdoor air safety before you step outside.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Confidence Reassurance Card
    safe_markdown("""
    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 14px; padding: 22px 26px; margin-bottom: 22px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            <span style="font-size: 1.2rem;">✨</span>
            <span style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">
                We are fairly confident about this forecast.
            </span>
        </div>
        <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #A7F3D0; margin: 0; line-height: 1.5;">
            AirGuard continuously tests itself against actual ground measurements. Predictions are updated hourly using incoming satellite, station, and wind data.
        </p>
    </div>
    """)

    # 3 Factors Driving Today's Forecast
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;'>🔍 What Drives Air Pollution in Your City?</h3>", unsafe_allow_html=True)

    safe_markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 24px;">
        <div style="background: #121212; border: 1px solid #222222; border-radius: 12px; padding: 18px 22px;">
            <div style="font-size: 1.4rem; margin-bottom: 8px;">💨</div>
            <div style="font-family: var(--font-heading); font-size: 1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                Wind & Air Flow
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #AAAAAA; margin: 0; line-height: 1.5;">
                Low wind traps smoke and dust near street level. When winds pick up, fresh air disperses harmful particles quickly.
            </p>
        </div>

        <div style="background: #121212; border: 1px solid #222222; border-radius: 12px; padding: 18px 22px;">
            <div style="font-size: 1.4rem; margin-bottom: 8px;">🌡️</div>
            <div style="font-family: var(--font-heading); font-size: 1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                Temperature & Moisture
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #AAAAAA; margin: 0; line-height: 1.5;">
                Cool mornings and high humidity can form smog layers that hold vehicular smoke close to where people walk.
            </p>
        </div>

        <div style="background: #121212; border: 1px solid #222222; border-radius: 12px; padding: 18px 22px;">
            <div style="font-size: 1.4rem; margin-bottom: 8px;">🚗</div>
            <div style="font-family: var(--font-heading); font-size: 1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                Daily Traffic & Activity
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #AAAAAA; margin: 0; line-height: 1.5;">
                Our model factors in weekday vs weekend rhythms and rush-hour pulses so you know when pollution spikes before it happens.
            </p>
        </div>
    </div>
    """)

    # How it works in 3 simple steps
    with st.container(border=True):
        st.markdown("""
        <div style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;">
            🛡️ How AirGuard Protects You in 3 Steps
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; font-family: var(--font-sans); font-size: 0.84rem; color: #CCCCCC; line-height: 1.5;">
            <div>
                <strong style="color: #38BDF8;">Step 1: Check Live Air</strong><br>
                Ingests real-time air quality sensors and local weather every hour.
            </div>
            <div>
                <strong style="color: #F59E0B;">Step 2: Predict 24-Hour Trends</strong><br>
                Uses machine learning to forecast if air will improve or worsen today.
            </div>
            <div>
                <strong style="color: #10B981;">Step 3: Give You a Plan</strong><br>
                Calculates your safest outdoor window and whether you need an N95 mask.
            </div>
        </div>
        """, unsafe_allow_html=True)

    render_simple_disclaimer()


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
        <div style="margin-bottom: 16px;">
            <h1 style="font-family: var(--font-heading); font-size: 2.1rem; font-weight: 800; color: #FFFFFF; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                Simple Safety & Mask Guide
            </h1>
            <p style="font-family: var(--font-sans); font-size: 0.95rem; color: #888888; margin: 0;">
                Easy practical tips to protect your lungs indoors and when stepping outside.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Mask Guide Cards
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;'>😷 Which Mask Actually Protects You?</h3>", unsafe_allow_html=True)

    safe_markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 24px;">
        <div style="background: #121212; border: 1px solid #222222; border-left: 4px solid #10B981; border-radius: 12px; padding: 18px 22px;">
            <div style="font-family: var(--font-heading); font-size: 1rem; font-weight: 700; color: #10B981; margin-bottom: 4px;">
                ✅ N95 / KN95 / FFP2 Masks
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.78rem; font-weight: 700; color: #FFFFFF; margin-bottom: 8px;">
                RECOMMENDED FOR AIR POLLUTION (Blocks 95%+)
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #BBBBBB; margin: 0; line-height: 1.5;">
                These masks have dense electro-static filters that block tiny smoke and exhaust particles. Press the metal nose clip firmly to ensure no air leaks around your nose.
            </p>
        </div>

        <div style="background: #121212; border: 1px solid #222222; border-left: 4px solid #EF4444; border-radius: 12px; padding: 18px 22px;">
            <div style="font-family: var(--font-heading); font-size: 1rem; font-weight: 700; color: #EF4444; margin-bottom: 4px;">
                ❌ Cloth, Bandanas & Surgical Masks
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.78rem; font-weight: 700; color: #FFFFFF; margin-bottom: 8px;">
                NOT EFFECTIVE AGAINST SMOG & PM₂.₅
            </div>
            <p style="font-family: var(--font-sans); font-size: 0.84rem; color: #BBBBBB; margin: 0; line-height: 1.5;">
                Cloth fibers and loose surgical mask edges allow tiny smoke particles to enter freely around the sides. They do not protect against harmful winter smog.
            </p>
        </div>
    </div>
    """)

    # 2. Indoor Air Defense Checklist
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;'>🏠 Keeping Your Home Air Clean</h3>", unsafe_allow_html=True)

    safe_markdown("""
    <div style="background: #121212; border: 1px solid #242424; border-radius: 12px; padding: 20px 24px; margin-bottom: 24px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; font-family: var(--font-sans); font-size: 0.84rem; color: #CCCCCC; line-height: 1.5;">
            <div>
                <strong style="color: #FFFFFF;">1. Close Windows During Peak Smog</strong><br>
                Keep windows shut from 7:00 PM to 10:00 AM when outdoor pollution is thickest.
            </div>
            <div>
                <strong style="color: #FFFFFF;">2. Use a HEPA Purifier in Bedrooms</strong><br>
                Clean air while sleeping gives your lungs 8 hours of uninterrupted recovery.
            </div>
            <div>
                <strong style="color: #FFFFFF;">3. Recirculate Car AC</strong><br>
                Switch vehicle AC to internal recirculation so traffic exhaust isn't pulled inside.
            </div>
            <div>
                <strong style="color: #FFFFFF;">4. Avoid Burning Candles or Coils</strong><br>
                Incense and mosquito coils indoors add heavy smoke particles to room air.
            </div>
        </div>
    </div>
    """)

    # 3. Family Cohorts
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;'>👨‍👩‍👧 Caring for Family Members</h3>", unsafe_allow_html=True)

    safe_markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 20px;">
        <div style="background: #121212; border: 1px solid #222222; border-radius: 12px; padding: 16px 20px;">
            <strong style="color: #FFFFFF; font-family: var(--font-heading); font-size: 0.95rem;">👶 Young Children</strong>
            <p style="font-family: var(--font-sans); font-size: 0.82rem; color: #AAAAAA; margin: 6px 0 0 0; line-height: 1.5;">
                Kids breathe faster and their lungs are still developing. Move recess indoors when the air safety status shows Caution or Avoid.
            </p>
        </div>
        <div style="background: #121212; border: 1px solid #222222; border-radius: 12px; padding: 16px 20px;">
            <strong style="color: #FFFFFF; font-family: var(--font-heading); font-size: 0.95rem;">👵 Senior Citizens</strong>
            <p style="font-family: var(--font-sans); font-size: 0.82rem; color: #AAAAAA; margin: 6px 0 0 0; line-height: 1.5;">
                High pollution puts stress on the heart and blood pressure. Take gentle walks during warm afternoon hours when air is cleanest.
            </p>
        </div>
        <div style="background: #121212; border: 1px solid #222222; border-radius: 12px; padding: 16px 20px;">
            <strong style="color: #FFFFFF; font-family: var(--font-heading); font-size: 0.95rem;">🫁 Asthma & Allergies</strong>
            <p style="font-family: var(--font-sans); font-size: 0.82rem; color: #AAAAAA; margin: 6px 0 0 0; line-height: 1.5;">
                Always keep your prescribed rescue inhaler in your pocket before leaving home, even for short neighbourhood errands.
            </p>
        </div>
    </div>
    """)

    render_simple_disclaimer()


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
        <div style="margin-bottom: 16px;">
            <h1 style="font-family: var(--font-heading); font-size: 2.1rem; font-weight: 800; color: #FFFFFF; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                City Air Comparison
            </h1>
            <p style="font-family: var(--font-sans); font-size: 0.95rem; color: #888888; margin: 0;">
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
        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 18px 22px;">
            <div style="font-family: var(--font-heading); font-size: 0.78rem; font-weight: 700; color: #10B981; text-transform: uppercase; margin-bottom: 4px;">
                🌿 Cleanest City Right Now
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.4rem; font-weight: 800; color: #FFFFFF;">
                {cleanest['city']}
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #A7F3D0; margin-top: 6px;">
                Status: <strong>{cleanest['category']}</strong> ({cleanest['pm25']:.1f} µg/m³)<br>
                {cleanest['tip']}
            </div>
        </div>
        """)

    with col_d:
        safe_markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 18px 22px;">
            <div style="font-family: var(--font-heading); font-size: 0.78rem; font-weight: 700; color: #EF4444; text-transform: uppercase; margin-bottom: 4px;">
                🛑 Heaviest Pollution Right Now
            </div>
            <div style="font-family: var(--font-heading); font-size: 1.4rem; font-weight: 800; color: #FFFFFF;">
                {dirtiest['city']}
            </div>
            <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #FCA5A5; margin-top: 6px;">
                Status: <strong>{dirtiest['category']}</strong> ({dirtiest['pm25']:.1f} µg/m³)<br>
                {dirtiest['tip']}
            </div>
        </div>
        """)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;'>🏙️ All Cities Ranked</h3>", unsafe_allow_html=True)

    # City list cards
    for c in city_results:
        safe_markdown(f"""
        <div style="background: #121212; border: 1px solid #222222; border-left: 4px solid {c['color']}; border-radius: 10px; padding: 14px 20px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">{c['city']}</span>
                <span style="font-family: var(--font-sans); font-size: 0.8rem; color: #888888; margin-left: 12px;">{c['tip']}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-family: var(--font-sans); font-size: 0.76rem; font-weight: 700; color: {c['color']}; background: rgba(255, 255, 255, 0.05); padding: 3px 10px; border-radius: 4px; border: 1px solid {c['color']};">
                    ● {c['category']}
                </span>
            </div>
        </div>
        """)

    render_simple_disclaimer()

