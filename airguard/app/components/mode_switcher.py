"""
Global Mode Switcher Component for AirGuard.
Manages user-controlled presentation modes ('Simple Mode' vs 'Technical Mode') in st.session_state.
Provides persistent state across page navigation, responsive sidebar and top-nav switchers,
and instant confirmation toast notifications.
"""

from __future__ import annotations

import streamlit as st

SIMPLE_MODE = "Simple Mode"
TECHNICAL_MODE = "Technical Mode"
MODE_OPTIONS = [SIMPLE_MODE, TECHNICAL_MODE]

MODE_DESCRIPTIONS = {
    SIMPLE_MODE: "Easy safety guidance for everyday outdoor decisions.",
    TECHNICAL_MODE: "Detailed air-quality analytics, forecasts, and model performance."
}

CONFIRMATION_MESSAGES = {
    SIMPLE_MODE: "Switched to Simple Mode: easy explanations and safety guidance.",
    TECHNICAL_MODE: "Switched to Technical Mode: full analytics, forecasts, and model details."
}


def init_view_mode() -> str:
    """
    Initializes view_mode in session state, defaulting to Simple Mode.
    Ensures persistent state across Streamlit page navigation.
    """
    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = SIMPLE_MODE
    if "_prev_view_mode" not in st.session_state:
        st.session_state["_prev_view_mode"] = st.session_state["view_mode"]
    if "global_view_mode_selector" not in st.session_state:
        st.session_state["global_view_mode_selector"] = st.session_state["view_mode"]
    return st.session_state["view_mode"]


def get_view_mode() -> str:
    """
    Returns the currently active view mode ('Simple Mode' or 'Technical Mode').
    """
    return init_view_mode()


def is_simple_mode() -> bool:
    """Returns True if current view mode is Simple Mode."""
    return get_view_mode() == SIMPLE_MODE


def is_technical_mode() -> bool:
    """Returns True if current view mode is Technical Mode."""
    return get_view_mode() == TECHNICAL_MODE


def set_view_mode(mode: str) -> None:
    """
    Programmatically sets the view mode and schedules confirmation feedback.
    """
    if mode in MODE_OPTIONS:
        prev = st.session_state.get("view_mode")
        st.session_state["view_mode"] = mode
        st.session_state["global_view_mode_selector"] = mode
        if prev != mode:
            st.session_state["_mode_switched_notice"] = CONFIRMATION_MESSAGES.get(mode)
            st.session_state["_prev_view_mode"] = mode


def _on_mode_change():
    """Callback fired when user interacts with the mode switcher widget."""
    selected = st.session_state.get("global_view_mode_selector", SIMPLE_MODE)
    prev = st.session_state.get("view_mode")
    st.session_state["view_mode"] = selected
    if selected != prev:
        st.session_state["_mode_switched_notice"] = CONFIRMATION_MESSAGES.get(selected)
        st.session_state["_prev_view_mode"] = selected


def render_mode_switcher(location: str = "sidebar") -> str:
    """
    Renders an accessible mode switcher in the sidebar.
    Uses st.session_state["view_mode"] with persistent session state.
    """
    init_view_mode()
    current_mode = st.session_state["view_mode"]

    if location == "sidebar":
        with st.sidebar:
            st.markdown(
                """
                <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #888888; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;">
                    👁️ VIEW MODE
                </div>
                """,
                unsafe_allow_html=True
            )

            idx = MODE_OPTIONS.index(current_mode) if current_mode in MODE_OPTIONS else 0
            selected = st.radio(
                "View mode",
                options=MODE_OPTIONS,
                index=idx,
                key="global_view_mode_selector",
                on_change=_on_mode_change,
                horizontal=True,
                label_visibility="collapsed"
            )
            st.session_state["view_mode"] = selected

            st.markdown(
                f"""
                <div style="font-size: 0.72rem; color: #777777; margin-top: 6px; margin-bottom: 12px; font-family: var(--font-sans); line-height: 1.4;">
                    {MODE_DESCRIPTIONS.get(selected, '')}
                </div>
                <hr style="border-color: #242424; margin: 4px 0 16px 0;">
                """,
                unsafe_allow_html=True
            )
            return selected

    return current_mode


def render_mode_banner() -> None:
    """
    Renders confirmation toast and an informative presentation badge at the top of the content area.
    """
    mode = get_view_mode()

    # Trigger toast on mode switch
    if "_mode_switched_notice" in st.session_state:
        notice = st.session_state.pop("_mode_switched_notice")
        try:
            st.toast(notice, icon="🔄")
        except Exception:
            pass

    # Informative presentation banner
    if mode == TECHNICAL_MODE:
        banner_html = """
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #101010;
            border: 1px solid #282828;
            border-left: 3px solid #38BDF8;
            border-radius: 8px;
            padding: 8px 14px;
            margin-bottom: 18px;
        ">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="color: #38BDF8; font-size: 0.85rem;">⚙️</span>
                <span style="font-family: var(--font-heading); font-size: 0.78rem; font-weight: 600; color: #CCCCCC;">
                    You are viewing <strong style="color: #FFFFFF;">Technical Mode</strong>: full analytics, forecasts, and model details.
                </span>
            </div>
            <span style="
                font-family: var(--font-mono);
                font-size: 0.65rem;
                padding: 2px 8px;
                border-radius: 9999px;
                background: rgba(56, 189, 248, 0.12);
                border: 1px solid #38BDF8;
                color: #38BDF8;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">
                ANALYTICAL DEPLOYMENT
            </span>
        </div>
        """
    else:
        banner_html = """
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #101010;
            border: 1px solid #282828;
            border-left: 3px solid #10B981;
            border-radius: 8px;
            padding: 8px 14px;
            margin-bottom: 18px;
        ">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="color: #10B981; font-size: 0.85rem;">🌿</span>
                <span style="font-family: var(--font-heading); font-size: 0.78rem; font-weight: 600; color: #CCCCCC;">
                    You are viewing <strong style="color: #FFFFFF;">Simple Mode</strong>: easy safety guidance for everyday outdoor decisions.
                </span>
            </div>
            <span style="
                font-family: var(--font-mono);
                font-size: 0.65rem;
                padding: 2px 8px;
                border-radius: 9999px;
                background: rgba(16, 185, 129, 0.12);
                border: 1px solid #10B981;
                color: #10B981;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">
                SIMPLIFIED VIEW
            </span>
        </div>
        """
    st.markdown(banner_html, unsafe_allow_html=True)
