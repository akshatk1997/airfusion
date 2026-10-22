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
