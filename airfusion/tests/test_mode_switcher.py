"""
Unit tests for the AirFusion Mode Switcher component and presentation mode state.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.components.mode_switcher import (
    SIMPLE_MODE,
    TECHNICAL_MODE,
    MODE_OPTIONS,
    CONFIRMATION_MESSAGES,
    init_view_mode,
    get_view_mode,
    set_view_mode,
    is_simple_mode,
    is_technical_mode,
)


def test_mode_switcher_defaults():
    mock_session = {}
    with patch("streamlit.session_state", mock_session):
        mode = init_view_mode()
        assert mode == SIMPLE_MODE
        assert get_view_mode() == SIMPLE_MODE
        assert is_simple_mode() is True
        assert is_technical_mode() is False


def test_mode_switcher_toggle_to_technical():
    mock_session = {"view_mode": SIMPLE_MODE}
    with patch("streamlit.session_state", mock_session):
        set_view_mode(TECHNICAL_MODE)
        assert mock_session["view_mode"] == TECHNICAL_MODE
        assert get_view_mode() == TECHNICAL_MODE
        assert is_technical_mode() is True
        assert is_simple_mode() is False
        assert mock_session.get("_mode_switched_notice") == CONFIRMATION_MESSAGES[TECHNICAL_MODE]


def test_mode_switcher_toggle_back_to_simple():
    mock_session = {"view_mode": TECHNICAL_MODE}
    with patch("streamlit.session_state", mock_session):
        set_view_mode(SIMPLE_MODE)
        assert mock_session["view_mode"] == SIMPLE_MODE
        assert get_view_mode() == SIMPLE_MODE
        assert is_simple_mode() is True
        assert is_technical_mode() is False
        assert mock_session.get("_mode_switched_notice") == CONFIRMATION_MESSAGES[SIMPLE_MODE]
