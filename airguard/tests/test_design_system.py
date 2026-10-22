"""
Unit tests for the Design System Foundation: tokens, badges, metrics, and SVG icons.
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.components.design_system import (
    render_badge,
    render_callout,
    render_hero_banner,
    ICONS,
    CSS_PATH
)


def test_css_tokens_exist():
    assert CSS_PATH.exists()
    content = CSS_PATH.read_text(encoding="utf-8")
    # Verify core design token definitions
    assert "--color-bg-base" in content
    assert "--color-bg-surface" in content
    assert "--color-brand-cyan" in content
    assert "--font-sans" in content
    assert "--font-mono" in content
    assert "--space-4" in content
    assert "--radius-lg" in content
    assert ":focus-visible" in content


def test_accessible_svg_icons():
    for name, svg in ICONS.items():
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert 'aria-hidden="true"' in svg


def test_render_badge():
    badge_html = render_badge("Good Condition", variant="good")
    assert "ag-badge-good" in badge_html
    assert "Good Condition" in badge_html


def test_render_callout():
    # Callout rendering function generates HTML string without crashing
    import io
    from unittest.mock import patch

    with patch("streamlit.markdown") as mock_st_md:
        render_callout("Warning", "High smog level", variant="alert")
        mock_st_md.assert_called_once()
        args, kwargs = mock_st_md.call_args
        assert "ag-callout" in args[0]
        assert "Warning" in args[0]
        assert "High smog level" in args[0]
