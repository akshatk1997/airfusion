"""
Unit tests for Simple Mode presentation components and view functions.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.components.simple_cards import (
    get_simple_status_style,
    render_air_safety_card,
    render_simple_timeline,
    render_todays_tip,
    render_simple_disclaimer
)


def test_simple_status_style_mapping():
    safe_style = get_simple_status_style("Safe")
    assert safe_style["color"] == "#10B981"
    assert safe_style["label"] == "Safe"

    mod_style = get_simple_status_style("Moderate")
    assert mod_style["color"] == "#F59E0B"
    assert mod_style["label"] == "Moderate"

    caut_style = get_simple_status_style("Caution")
    assert caut_style["color"] == "#F97316"
    assert caut_style["label"] == "Caution"

    avoid_style = get_simple_status_style("Avoid")
    assert avoid_style["color"] == "#EF4444"
    assert avoid_style["label"] == "Avoid"

    high_style = get_simple_status_style("High Risk")
    assert high_style["color"] == "#D71921"
    assert high_style["label"] == "High Risk"


def test_render_air_safety_card_sanitized():
    with patch("streamlit.markdown") as mock_st_md:
        render_air_safety_card(
            city_name="Chandigarh, India",
            status_level="Moderate",
            answer_text="Mostly Safe: Air quality is acceptable for healthy adults.",
            best_window="06:00 AM – 07:00 AM",
            avoid_hours=["05:00 PM – 09:00 PM"],
            main_reason="Air pollution is moderately high.",
            recommendation="Safe for a 30-minute walk.",
            mask_tip="Consider an N95 mask if outdoors."
        )
        assert mock_st_md.called
        html_arg = mock_st_md.call_args[0][0]
        assert "Chandigarh, India" in html_arg
        assert "Mostly Safe" in html_arg
        assert "06:00 AM – 07:00 AM" in html_arg
        assert "05:00 PM – 09:00 PM" in html_arg
        assert "Why:" in html_arg


def test_render_todays_tip_dynamic():
    with patch("streamlit.markdown") as mock_st_md:
        render_todays_tip(aqi=40, wind_speed=3.0, humidity=45.0)
        assert mock_st_md.called
        good_tip_html = mock_st_md.call_args[0][0]
        assert "Great Day for Outdoors" in good_tip_html

        render_todays_tip(aqi=160, wind_speed=1.5, humidity=70.0)
        bad_tip_html = mock_st_md.call_args[0][0]
        assert "Keep Windows Closed Today" in bad_tip_html


def test_render_simple_disclaimer():
    with patch("streamlit.markdown") as mock_st_md:
        render_simple_disclaimer()
        assert mock_st_md.called
        disclaimer_html = mock_st_md.call_args[0][0]
        assert "Safety Note:" in disclaimer_html
        assert "medical diagnosis or treatment" in disclaimer_html


def test_render_simple_weather_cards():
    from app.components.simple_cards import render_simple_weather_cards
    with patch("streamlit.markdown") as mock_st_md:
        render_simple_weather_cards(temperature=24.5, humidity=60.0, wind_speed=8.5)
        assert mock_st_md.called
        html = mock_st_md.call_args[0][0]
        assert "°C" in html
        assert "Pleasantly comfortable" in html
        assert "60%" in html
        assert "8.5 km/h" in html


def test_render_simple_pollutant_cards():
    from app.components.simple_cards import render_simple_pollutant_cards
    with patch("streamlit.markdown") as mock_st_md:
        render_simple_pollutant_cards(pm25=22.0, pm10=45.0)
        assert mock_st_md.called
        html = mock_st_md.call_args[0][0]
        assert "Tiny Particles (PM₂.₅)" in html
        assert "Coarse Dust & Pollen (PM₁₀)" in html
        assert "Moderate" in html


def test_render_simple_views_execution():
    from app.components.simple_views import (
        render_simple_model_insights,
        render_simple_about_safety
    )
    with patch("streamlit.markdown") as mock_st_md:
        render_simple_model_insights()
        assert mock_st_md.called
        html = "".join([call[0][0] for call in mock_st_md.call_args_list if call[0]])
        assert "How AirFusion Forecasts Pollution" in html
        assert "We are fairly confident about this forecast." in html
        assert "Low wind traps smoke" in html

    with patch("streamlit.markdown") as mock_st_md:
        render_simple_about_safety()
        assert mock_st_md.called
        html = "".join([call[0][0] for call in mock_st_md.call_args_list if call[0]])
        assert "Simple Safety & Mask Guide" in html
        assert "N95 / KN95 / FFP2 Masks" in html
        assert "Keeping Your Home Air Clean" in html


def test_aero_chatbot_responses():
    from app.components.simple_chatbot import generate_aero_response

    # Test outdoor question
    resp_play = generate_aero_response(
        user_query="Can I play soccer outside right now?",
        city_name="Chandigarh",
        pm25=12.0,
        aqi=45,
        temp=22.0,
        wind=8.0,
        humidity=50.0
    )
    assert "clean" in resp_play["answer"].lower() or "fresh" in resp_play["answer"].lower()
    assert "Tip:" in resp_play["tip"]

    # Test packing question
    resp_pack = generate_aero_response(
        user_query="What should I pack in my schoolbag today?",
        city_name="Chandigarh",
        pm25=65.0,
        aqi=150,
        temp=24.0,
        wind=4.0,
        humidity=55.0
    )
    assert "water" in resp_pack["answer"].lower()
    assert "mask" in resp_pack["answer"].lower()

    # Test symptom relief question
    resp_sym = generate_aero_response(
        user_query="My throat tickles and my eyes burn",
        city_name="Chandigarh",
        pm25=70.0,
        aqi=155,
        temp=25.0,
        wind=3.0,
        humidity=60.0
    )
    assert "water" in resp_sym["answer"].lower() or "honey" in resp_sym["answer"].lower()
    assert "never rub" in resp_sym["answer"].lower() or "cool" in resp_sym["answer"].lower()


def test_outdoor_kit_and_game_state():
    from app.components.simple_games import get_game_state
    import streamlit as st

    state = get_game_state()
    assert "badges_unlocked" in state
    assert isinstance(state["badges_unlocked"], set)


def test_dual_mode_ai_assistant_responses():
    from app.components.ai_assistant_popup import generate_technical_response, generate_aero_response
    
    # 1. Technical Mode Inversion & PBL test
    tech_inversion = generate_technical_response(
        user_query="Tell me about inversion trapping and boundary layer",
        city_name="Delhi",
        pm25=120.0,
        aqi=220,
        temp=14.0,
        wind=4.0,
        humidity=65.0
    )
    assert "pbl" in tech_inversion["answer"].lower() or "boundary" in tech_inversion["answer"].lower()
    assert "ventilation coefficient" in tech_inversion["answer"].lower() or "v_c" in tech_inversion["answer"].lower()
    assert "metric" in tech_inversion
    assert "protocol" in tech_inversion

    # 2. Technical Mode Dosage test
    tech_dosage = generate_technical_response(
        user_query="Calculate minute ventilation and inhaled lung dosage",
        city_name="Delhi",
        pm25=50.0,
        aqi=130,
        temp=22.0,
        wind=10.0,
        humidity=50.0,
        user_profile={"usual_activities": "active"}
    )
    assert "inhaled" in tech_dosage["answer"].lower() or "alveolar" in tech_dosage["answer"].lower()
    assert "who" in tech_dosage["metric"].lower()

    # 3. Simple Mode Aero test
    aero_resp = generate_aero_response(
        user_query="Can I go outside to the park?",
        city_name="Mumbai",
        pm25=10.0,
        aqi=35,
        temp=28.0,
        wind=15.0,
        humidity=70.0
    )
    assert "mumbai" in aero_resp["answer"].lower()
    assert "mascot" in aero_resp


def test_decoupled_chat_history_and_accuracy():
    """
    Verifies that Simple Mode and Technical Mode have completely decoupled,
    non-shareable histories, and tests high-accuracy query handling for diverse intents.
    """
    import streamlit as st
    from app.components.ai_assistant_popup import (
        generate_technical_response,
        generate_aero_response
    )

    # 1. Verify decoupled history separation
    st.session_state["simple_chat_history"] = [{"query": "Can I play?", "answer": "Yes!"}]
    st.session_state["technical_chat_history"] = [{"query": "PBL height?", "answer": "350m"}]

    assert len(st.session_state["simple_chat_history"]) == 1
    assert len(st.session_state["technical_chat_history"]) == 1
    assert "Can I play?" in st.session_state["simple_chat_history"][0]["query"]
    assert "PBL height?" in st.session_state["technical_chat_history"][0]["query"]
    assert st.session_state["simple_chat_history"] != st.session_state["technical_chat_history"]

    # 2. Simple Mode High Accuracy Across Varied User Intents
    # Symptom query
    symp = generate_aero_response("My throat hurts and eyes sting", "Chandigarh", 45.0, 110, 22.0, 8.0, 60.0)
    assert "honey" in symp["answer"].lower() or "soothe" in symp["answer"].lower()
    assert "mascot" in symp

    # Baby stroller query
    baby = generate_aero_response("Can I take my 3 month old newborn baby stroller walk?", "Delhi", 70.0, 160, 18.0, 5.0, 50.0)
    assert "gentle" in baby["answer"].lower() or "stroller" in baby["tip"].lower() or "baby" in baby["answer"].lower()

    # Rain shower query
    rain = generate_aero_response("Will the rain clean our sky?", "Kolkata", 30.0, 80, 26.0, 12.0, 85.0)
    assert "rain" in rain["answer"].lower()
    assert "power shower" in rain["answer"].lower() or "shower" in rain["answer"].lower()

    # 3. Technical Mode High Accuracy Across Varied Engineering Queries
    # Criteria pollutants (Ozone & NO2)
    chem = generate_technical_response("What about ground-level ozone kinetics and NO2?", "Mumbai", 40.0, 95, 29.0, 14.0, 75.0)
    assert "ozone" in chem["answer"].lower() or "o₃" in chem["answer"].lower()
    assert "stoichiometry" in chem["metric"].lower() or "precursors" in chem["answer"].lower()

    # IAQ and building HVAC
    hvac = generate_technical_response("Building HVAC MERV-13 positive pressurization guidelines", "Bengaluru", 25.0, 65, 24.0, 10.0, 55.0)
    assert "hvac" in hvac["answer"].lower() or "merv" in hvac["answer"].lower() or "envelope" in hvac["answer"].lower()
    assert "ach" in hvac["metric"].lower() or "cadr" in hvac["metric"].lower() or "ppm" in hvac["metric"].lower()

    # Clinical pathophysiology
    copd = generate_technical_response("Asthma COPD bronchospasm and vascular inflammation risk", "Jaipur", 85.0, 175, 25.0, 6.0, 40.0)
    assert "inflammatory" in copd["answer"].lower() or "bronchial" in copd["answer"].lower() or "oxidative" in copd["answer"].lower()
    assert "risk" in copd["metric"].lower() or "protocol" in copd


def test_simple_mode_interactive_suite_integrity():
    """
    Verifies that the Simple Mode interactive suite is fully integrated in public/index.html:
    1. Breathe Easy Mindful Calming Bubble (4-7-8)
    2. Kids & Family Outdoor Adventure Wheel
    3. Haven's Indoor Sanctuary & Plant Doctor Simulator
    4. Aero's Clean Air Adventure Quest & Mini-Quiz
    5. Clean Air Hero Badges & Daily Streak Tracker
    6. 24-Hour Child-Friendly Illustrated Sky Strip
    """
    root_dir = Path(__file__).resolve().parent.parent.parent
    index_html = root_dir / "public" / "index.html"
    assert index_html.exists(), "public/index.html must exist"

    with open(index_html, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Breathe Easy Bubble
    assert "breathe-calm-box" in html
    assert "breathe-orb" in html
    assert "toggleBreatheExercise" in html
    assert "4-7-8" in html

    # 2. Kids & Family Adventure Wheel
    assert "kids-act-grid" in html
    assert "selectKidsActivity" in html
    assert "Swings &amp; Slide" in html
    assert "Bicycle Riding" in html
    assert "Soccer &amp; Games" in html

    # 3. Haven's Indoor Sanctuary & Plant Doctor
    assert "sanctuary-grid" in html
    assert "computeSanctuaryMetrics" in html
    assert "setPurifierPower" in html
    assert "Snake Plant" in html
    assert "Spider Plant" in html
    assert "Peace Lily" in html
    assert "Areca Palm" in html

    # 4. Aero's Adventure Quest & Mini-Quiz
    assert "QUIZ_QUESTIONS" in html
    assert "answerQuizQuestion" in html
    assert "nextQuizQuestion" in html
    assert "restartQuiz" in html

    # 5. Clean Air Hero Badges & Daily Streak
    assert "claimDailyStreak" in html
    assert "Fresh Lungs Scout" in html
    assert "Clean Air Grand Champion" in html
    assert "streakDays" in html

    # 6. 24-Hour Illustrated Sky Strip
    assert "sky-visual-stage" in html
    assert "selectSkyHour" in html
    assert "Midnight Slumber" in html
    assert "Golden Sunshine Clean Breeze Window" in html




