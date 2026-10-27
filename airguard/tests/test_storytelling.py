"""
Unit and Integration Tests for Simple Mode Storytelling & Everyday Terminology Decoder.
Verifies structure, data integrity, analogies, and dynamic mood calculation.
"""

import pytest
import sys
from pathlib import Path

# Add project root and airfusion to sys.path
TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT.parent))

from app.components.simple_storytelling import (
    CLEAN_AIR_STORY_CHAPTERS,
    EVERYDAY_TERMS_CATALOG
)
from app.components.simple_cards import compute_guardian_mood_state


def test_story_chapters_structure():
    """Verify all 4 clean air story chapters have complete family-friendly content."""
    assert len(CLEAN_AIR_STORY_CHAPTERS) == 4
    required_keys = {"id", "number", "title", "subtitle", "mascot", "hero_badge", "badge_color", "analogy", "story", "takeaways", "voice_script"}
    for chap in CLEAN_AIR_STORY_CHAPTERS:
        for k in required_keys:
            assert k in chap, f"Chapter {chap.get('number')} missing key {k}"
        assert len(chap["title"]) > 5
        assert len(chap["analogy"]) > 10
        assert len(chap["story"]) > 50
        assert len(chap["takeaways"]) >= 2
        assert len(chap["voice_script"]) > 20


def test_everyday_terms_catalog_structure():
    """Verify all 14 decoded everyday terms are complete and contain plain-English analogies."""
    assert len(EVERYDAY_TERMS_CATALOG) == 14
    required_keys = {
        "term", "technical_name", "plain_name", "category", "category_label",
        "badge_color", "icon", "analogy", "what_it_is", "why_it_matters", "action_rule"
    }
    valid_categories = {"pollutants", "weather", "standards", "gear", "rules"}
    for term in EVERYDAY_TERMS_CATALOG:
        for k in required_keys:
            assert k in term, f"Term {term.get('term')} missing key {k}"
        assert term["category"] in valid_categories, f"Invalid category for term {term['term']}"
        assert len(term["analogy"]) > 10, f"Missing or brief analogy for {term['term']}"
        assert len(term["plain_name"]) > 3
        assert len(term["action_rule"]) > 10


def test_guardian_dynamic_mood_clean():
    """Verify live cartoon guardians respond with clean mood state under safe air."""
    mood = compute_guardian_mood_state(
        city_name="Chandigarh",
        pm25=12.0,
        aqi=40,
        status_level="safe",
        temp=22.0,
        humidity=45.0,
        wind=9.0
    )
    assert mood["mood_id"] == "clean"
    assert "JOYFUL" in mood["mood_title"].upper() or "VIBRANT" in mood["mood_title"].upper()
    assert mood["status_color"] == "#10B981"
    assert "aero" in mood
    assert "flash" in mood
    assert "nova" in mood
    assert "haven" in mood
    assert "TRICITY" in mood["regional_tag"] or "Shivalik" in mood["regional_lore"]


def test_guardian_dynamic_mood_severe_inversion():
    """Verify live cartoon guardians respond with protective shield under high smog and inversion."""
    mood = compute_guardian_mood_state(
        city_name="Delhi-NCR",
        pm25=210.0,
        aqi=380,
        status_level="hazard",
        temp=12.0,
        humidity=88.0,
        wind=1.5
    )
    assert mood["mood_id"] == "severe"
    assert "HAZARD" in mood["mood_title"].upper() or "LOCKDOWN" in mood["mood_title"].upper()
    assert mood["status_color"] in ["#DC2626", "#EF4444"]
    assert mood["is_cold_inversion"] is True
    assert "trapping" in mood["weather_desc"].lower() or "ceiling" in mood["weather_desc"].lower()
    assert "DELHI" in mood["regional_tag"].upper() or "Indo-Gangetic" in mood["regional_lore"]


def test_guardian_mood_preview_override():
    """Verify interactive mood preview switcher overrides live telemetry for testing all 4 moods."""
    for preview_key in ["clean", "moderate", "smog", "severe"]:
        mood = compute_guardian_mood_state(
            city_name="Tokyo",
            pm25=20.0,
            aqi=50,
            status_level="safe",
            preview_mood=preview_key
        )
        assert mood["mood_id"] == preview_key
