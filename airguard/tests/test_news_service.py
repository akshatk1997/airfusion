"""
Unit and Integration Tests for AirGuard Environmental News & Intelligence Service.
Verifies automated 6-hour refresh cycles, SQLite persistence, local vs international
categorization, situational telemetry injection, search filters, and trusted source provenance.
"""

import pytest
import sqlite3
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.news_service import (
    init_news_db,
    get_sync_status,
    refresh_news_feed,
    get_news_feed,
    _inject_situational_bulletin,
    TRUSTED_SOURCES_REGISTRY,
    NEWS_SYNC_INTERVAL_HOURS
)


@pytest.fixture
def temp_db(tmp_path):
    """Provides a fresh temporary SQLite database connection for test isolation."""
    db_file = tmp_path / "test_airguard_news.db"
    conn = sqlite3.connect(str(db_file), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    init_news_db(conn)
    yield conn
    conn.close()


def test_init_news_db(temp_db):
    """Verifies that environmental_news and news_sync_metadata tables are properly created."""
    cursor = temp_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]
    assert "environmental_news" in tables
    assert "news_sync_metadata" in tables


def test_get_sync_status_initial(temp_db):
    """Tests that initial sync status correctly flags an update as due."""
    status = get_sync_status(temp_db)
    assert status["is_sync_due"] is True
    assert status["sync_interval_hours"] == NEWS_SYNC_INTERVAL_HOURS
    assert status["trusted_sources_count"] >= 8


def test_refresh_news_feed_population(temp_db):
    """Tests that refresh_news_feed populates the news corpus and updates the 6-hour sync metadata."""
    status = refresh_news_feed(active_city="Chandigarh", force=True, conn=temp_db)
    assert status["is_sync_due"] is False
    assert status["hours_remaining"] > 5.0
    assert "5h" in status["next_sync_in_str"] or "6h" in status["next_sync_in_str"]

    cursor = temp_db.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM environmental_news;")
    count = cursor.fetchone()["count"]
    assert count >= 10, f"Expected at least 10 news items, got {count}"


def test_get_news_feed_separation(temp_db):
    """Verifies clear separation between Area-Specific (Local) and International (Global) news."""
    feed = get_news_feed(active_city="Chandigarh", force_refresh=True, conn=temp_db)
    
    assert "local_news" in feed
    assert "international_news" in feed
    assert len(feed["local_news"]) > 0
    assert len(feed["international_news"]) > 0

    # Verify categories
    for art in feed["local_news"]:
        assert art["category"] == "local"
    for art in feed["international_news"]:
        assert art["category"] == "international"


def test_situational_bulletin_injection_high_pm25(temp_db):
    """Tests situational awareness: acute PM2.5 elevation generates a CRITICAL live situational bulletin."""
    now_dt = datetime.now()
    _inject_situational_bulletin(
        conn=temp_db,
        city="Delhi",
        pm25=185.0,
        aqi=340,
        now_dt=now_dt
    )

    cursor = temp_db.cursor()
    cursor.execute("SELECT * FROM environmental_news WHERE id = 'situational_bulletin_delhi';")
    row = cursor.fetchone()
    assert row is not None
    assert row["severity"] == "CRITICAL"
    assert "Delhi" in row["title"]
    assert "185.0" in row["title"]
    assert "superhero N95 mask" in row["simple_summary"]


def test_situational_bulletin_injection_clean_air(temp_db):
    """Tests situational awareness: clean air window generates a favorable MODERATE advisory."""
    now_dt = datetime.now()
    _inject_situational_bulletin(
        conn=temp_db,
        city="Chandigarh",
        pm25=18.5,
        aqi=45,
        now_dt=now_dt
    )

    cursor = temp_db.cursor()
    cursor.execute("SELECT * FROM environmental_news WHERE id = 'situational_bulletin_chandigarh';")
    row = cursor.fetchone()
    assert row is not None
    assert row["severity"] == "MODERATE"
    assert "Clear Atmospheric Window" in row["title"] or "Favorable" in row["title"]


def test_news_search_and_severity_filters(temp_db):
    """Tests search queries and severity filtering on news feeds."""
    get_news_feed(active_city="Chandigarh", force_refresh=True, conn=temp_db)

    # Search for "Copernicus"
    feed_cams = get_news_feed(active_city="Chandigarh", search_query="Copernicus", conn=temp_db)
    assert any("Copernicus" in a["title"] or "Copernicus" in a["source_name"] for a in feed_cams["international_news"])

    # Filter for CRITICAL only
    feed_crit = get_news_feed(active_city="Chandigarh", severity_filter="CRITICAL", conn=temp_db)
    for art in feed_crit["local_news"] + feed_crit["international_news"]:
        assert art["severity"] == "CRITICAL"


def test_trusted_sources_registry():
    """Ensures trusted sources registry contains tier-1 regulatory authorities and research agencies."""
    keys = list(TRUSTED_SOURCES_REGISTRY.keys())
    assert "CPCB" in keys
    assert "WHO" in keys
    assert "COPENICUS" in keys
    assert "NASA" in keys
    assert "EPA" in keys
    assert "REUTERS" in keys

    for s_key, data in TRUSTED_SOURCES_REGISTRY.items():
        assert "name" in data
        assert "credibility" in data
        assert "url" in data
        assert data["url"].startswith("http")


def test_dual_mode_content_completeness(temp_db):
    """Verifies that all articles contain both Simple Mode (friendly) and Technical Mode (scientific) content."""
    feed = get_news_feed(active_city="Chandigarh", force_refresh=True, conn=temp_db)
    all_articles = feed["local_news"] + feed["international_news"]
    
    for art in all_articles:
        # Simple Mode requirements
        assert len(art["simple_summary"]) > 10
        assert art["read_time_mins"] >= 1
        assert len(art["action_items_list"]) >= 1

        # Technical Mode requirements
        assert len(art["technical_analysis"]) > 20
        assert art["source_credibility"] != ""
        assert art["source_url"].startswith("http")


def test_expanded_regional_coverage_and_web_news_suite(temp_db):
    """
    Verifies the expanded regional coverage across Kolkata, Jaipur, Lucknow,
    and checks the public/index.html web news wire structure (sorting, filtering, refresh).
    """
    from src.news_service import _generate_curated_news_corpus
    from datetime import datetime
    from pathlib import Path

    corpus = _generate_curated_news_corpus(datetime.now())
    city_scopes = set(c.get("city_scope") for c in corpus)
    assert "Kolkata" in city_scopes
    assert "Jaipur" in city_scopes
    assert "Lucknow" in city_scopes
    assert "Delhi" in city_scopes
    assert "Mumbai" in city_scopes
    assert "Bengaluru" in city_scopes
    assert "Chandigarh" in city_scopes
    assert "GLOBAL" in city_scopes

    # Verify web single page index.html features
    root_dir = Path(__file__).resolve().parent.parent.parent
    index_html = root_dir / "public" / "index.html"
    assert index_html.exists()

    with open(index_html, "r", encoding="utf-8") as f:
        html = f.read()

    # News database, refresh wire and categorization
    assert "NEWS_DATABASE" in html
    assert "news-live-wire-bar" in html
    assert "refreshNewsWire" in html
    assert "setNewsAreaFilter" in html
    assert "setNewsTopicFilter" in html
    assert "setNewsSortOrder" in html
    assert "setNewsSearchQuery" in html
    assert "getRelativeTimeStr" in html
    assert "generateSituationalAlert" in html

    # Expanded 8-video suite
    assert "who_pulmonary" in html
    assert "esa_sentinel" in html
    assert "nasa_atmospheric" in html
    assert "epa_clean_air" in html
    assert "cpcb_ncap_mission" in html
    assert "lancet_pediatric_lungs" in html
    assert "unep_air_we_breathe" in html
    assert "inversion_physics_dw" in html

