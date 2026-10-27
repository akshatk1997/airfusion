"""
Global Mode Switcher Component for AirFusion.
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
                <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;">
                    👁️ VIEW MODE
                </div>
                """,
                unsafe_allow_html=True
            )

            idx = MODE_OPTIONS.index(current_mode) if current_mode in MODE_OPTIONS else 0
            if st.session_state.get("global_view_mode_selector") != current_mode:
                try:
                    st.session_state["global_view_mode_selector"] = current_mode
                except Exception:
                    pass
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
                <div style="font-size: 0.74rem; color: #94A3B8; margin-top: 6px; margin-bottom: 12px; font-family: var(--font-sans); line-height: 1.4;">
                    {MODE_DESCRIPTIONS.get(selected, '')}
                </div>
                <hr style="border-color: rgba(255, 255, 255, 0.08); margin: 4px 0 16px 0;">
                """,
                unsafe_allow_html=True
            )
            return selected

    return current_mode


def render_mode_banner() -> None:
    """
    Renders confirmation toast and an elegant, unobtrusive presentation indicator.
    """
    mode = get_view_mode()

    # Trigger toast on mode switch
    if "_mode_switched_notice" in st.session_state:
        notice = st.session_state.pop("_mode_switched_notice")
        try:
            st.toast(notice, icon="🔄")
        except Exception:
            pass

    # Clean AirFusion professional status hint
    if mode == TECHNICAL_MODE:
        banner_html = """
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #FFFFFF;
            border: 1px solid #EBE6DF;
            border-left: 4px solid #FF6845;
            border-radius: 12px;
            padding: 10px 18px;
            margin-bottom: 16px;
            box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);
        ">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="color: #FF6845; font-size: 0.95rem;">⚙️</span>
                <span style="font-family: var(--font-heading); font-size: 0.84rem; font-weight: 600; color: #1F344C;">
                    Technical Mode active: full multi-pollutant telemetry, forecasting models, and statistical diagnostics.
                </span>
            </div>
            <span style="font-family: var(--font-mono); font-size: 0.68rem; color: #FF6845; font-weight: 700; letter-spacing: 0.05em; background: rgba(255, 104, 69, 0.08); padding: 3px 10px; border-radius: 9999px;">
                RESEARCH & ANALYTICS
            </span>
        </div>
        """
    else:
        banner_html = """
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #FFFFFF;
            border: 1px solid #EBE6DF;
            border-left: 4px solid #10B981;
            border-radius: 12px;
            padding: 10px 18px;
            margin-bottom: 16px;
            box-shadow: 0 4px 16px rgba(31, 52, 76, 0.04);
        ">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="color: #10B981; font-size: 0.95rem;">🌿</span>
                <span style="font-family: var(--font-heading); font-size: 0.84rem; font-weight: 600; color: #1F344C;">
                    Simple Mode active: actionable safety guidance and personalized outdoor windows for everyday decisions.
                </span>
            </div>
            <span style="font-family: var(--font-mono); font-size: 0.68rem; color: #059669; font-weight: 700; letter-spacing: 0.05em; background: rgba(16, 185, 129, 0.08); padding: 3px 10px; border-radius: 9999px;">
                DECISION SUPPORT
            </span>
        </div>
        """
    st.markdown(banner_html, unsafe_allow_html=True)
