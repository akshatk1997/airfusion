"""
AirFusion Reusable Design System Component Library.
Provides centralized atomic components: badges, section headers,
metric tiles, callouts, hero banners, and accessible SVG icons.
"""

from __future__ import annotations

import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any, List

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
FONTS_PATH = ASSETS_DIR / "fonts.css"
CSS_PATH = ASSETS_DIR / "style.css"


def inject_foundation_styles() -> None:
    """
    Injects the typography and foundation stylesheet into the Streamlit DOM.
    Loads Plus Jakarta Sans and JetBrains Mono styles.
    """
    styles = []
    if FONTS_PATH.exists():
        try:
            with open(FONTS_PATH, "r", encoding="utf-8") as f:
                styles.append(f.read())
        except Exception:
            pass
    if CSS_PATH.exists():
        try:
            with open(CSS_PATH, "r", encoding="utf-8") as f:
                styles.append(f.read())
        except Exception:
            pass
    if styles:
        combined = "\n".join(styles)
        st.markdown(f"<style>{combined}</style>", unsafe_allow_html=True)


# ==============================================================================
# ACCESSIBLE VECTOR ICONS (INLINE SVG)
# ==============================================================================
ICONS = {
    "shield": """<svg aria-hidden="true" width="22" height="22" viewBox="0 0 64 64" fill="none"><defs><linearGradient id="icBg" x1="10" y1="6" x2="54" y2="58" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#0F1E2E"/><stop offset="100%" stop-color="#081018"/></linearGradient><linearGradient id="icBorder" x1="8" y1="6" x2="56" y2="58" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#38BDF8"/><stop offset="100%" stop-color="#FF6845"/></linearGradient><linearGradient id="icAir" x1="16" y1="16" x2="32" y2="46" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#38BDF8"/><stop offset="100%" stop-color="#0284C7"/></linearGradient><linearGradient id="icFusion" x1="48" y1="16" x2="32" y2="46" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#FFA07A"/><stop offset="100%" stop-color="#FF6845"/></linearGradient></defs><path d="M 32 6.5 C 43.5 6.5 52 10.5 52 23 C 52 40 40 52.5 32 57.5 C 24 52.5 12 40 12 23 C 12 10.5 20.5 6.5 32 6.5 Z" fill="url(#icBg)" stroke="url(#icBorder)" stroke-width="2.5" stroke-linejoin="round"/><path d="M 19 21.5 C 18.5 32.5 24 40.5 32 45.5 C 27.5 39.8 24.2 33 25.4 24.8 C 26.2 20.2 29 17.6 32 16.5 C 26 16.3 19.8 18.6 19 21.5 Z" fill="url(#icAir)"/><path d="M 45 21.5 C 45.5 32.5 40 40.5 32 45.5 C 36.5 39.8 39.8 33 38.6 24.8 C 37.8 20.2 35 17.6 32 16.5 C 38 16.3 44.2 18.6 45 21.5 Z" fill="url(#icFusion)"/><path d="M 32 23 L 34.5 29.5 L 41 31.5 L 34.5 33.5 L 32 40 L 29.5 33.5 L 23 31.5 L 29.5 29.5 Z" fill="#FFFFFF"/></svg>""",
    "ag_star": """<svg aria-hidden="true" width="28" height="28" viewBox="0 0 64 64" fill="none"><defs><linearGradient id="navBg" x1="10" y1="6" x2="54" y2="58" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#0F1E2E"/><stop offset="100%" stop-color="#081018"/></linearGradient><linearGradient id="navBorder" x1="8" y1="6" x2="56" y2="58" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#38BDF8"/><stop offset="50%" stop-color="#818CF8"/><stop offset="100%" stop-color="#FF6845"/></linearGradient><linearGradient id="navAir" x1="16" y1="16" x2="32" y2="46" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#BAE6FD"/><stop offset="50%" stop-color="#38BDF8"/><stop offset="100%" stop-color="#0284C7"/></linearGradient><linearGradient id="navFusion" x1="48" y1="16" x2="32" y2="46" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#FED7AA"/><stop offset="50%" stop-color="#FF6845"/><stop offset="100%" stop-color="#DC2626"/></linearGradient><radialGradient id="navCore" cx="32" cy="31.5" r="8" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#FFFFFF"/><stop offset="50%" stop-color="#38BDF8" stop-opacity="0.6"/><stop offset="100%" stop-color="#0284C7" stop-opacity="0"/></radialGradient></defs><path d="M 32 6.5 C 43.5 6.5 52 10.5 52 23 C 52 40 40 52.5 32 57.5 C 24 52.5 12 40 12 23 C 12 10.5 20.5 6.5 32 6.5 Z" fill="url(#navBg)" stroke="url(#navBorder)" stroke-width="2.5" stroke-linejoin="round"/><path d="M 32 10.5 C 41 10.5 48 13.8 48 23.5 C 48 37.8 38.5 48.5 32 53 C 25.5 48.5 16 37.8 16 23.5 C 16 13.8 23 10.5 32 10.5 Z" fill="none" stroke="rgba(255, 255, 255, 0.12)" stroke-width="1.2"/><path d="M 19 21.5 C 18.5 32.5 24 40.5 32 45.5 C 27.5 39.8 24.2 33 25.4 24.8 C 26.2 20.2 29 17.6 32 16.5 C 26 16.3 19.8 18.6 19 21.5 Z" fill="url(#navAir)"/><path d="M 45 21.5 C 45.5 32.5 40 40.5 32 45.5 C 36.5 39.8 39.8 33 38.6 24.8 C 37.8 20.2 35 17.6 32 16.5 C 38 16.3 44.2 18.6 45 21.5 Z" fill="url(#navFusion)"/><circle cx="32" cy="31.5" r="7" fill="url(#navCore)"/><path d="M 32 24.5 L 34.2 29.8 L 39.5 31.5 L 34.2 33.2 L 32 38.5 L 29.8 33.2 L 24.5 31.5 L 29.8 29.8 Z" fill="#FFFFFF" stroke="#BAE6FD" stroke-width="0.4"/><circle cx="32" cy="31.5" r="1.5" fill="#FFFFFF"/></svg>""",
    "airfusion_logo": """<svg aria-hidden="true" width="36" height="36" viewBox="0 0 64 64" fill="none"><defs><linearGradient id="brandBg" x1="10" y1="6" x2="54" y2="58" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#0F1E2E"/><stop offset="100%" stop-color="#081018"/></linearGradient><linearGradient id="brandBorder" x1="8" y1="6" x2="56" y2="58" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#38BDF8"/><stop offset="50%" stop-color="#818CF8"/><stop offset="100%" stop-color="#FF6845"/></linearGradient><linearGradient id="brandAir" x1="16" y1="16" x2="32" y2="46" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#BAE6FD"/><stop offset="50%" stop-color="#38BDF8"/><stop offset="100%" stop-color="#0284C7"/></linearGradient><linearGradient id="brandFusion" x1="48" y1="16" x2="32" y2="46" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#FED7AA"/><stop offset="50%" stop-color="#FF6845"/><stop offset="100%" stop-color="#DC2626"/></linearGradient><radialGradient id="brandCore" cx="32" cy="31.5" r="8" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#FFFFFF"/><stop offset="50%" stop-color="#38BDF8" stop-opacity="0.6"/><stop offset="100%" stop-color="#0284C7" stop-opacity="0"/></radialGradient></defs><path d="M 32 6.5 C 43.5 6.5 52 10.5 52 23 C 52 40 40 52.5 32 57.5 C 24 52.5 12 40 12 23 C 12 10.5 20.5 6.5 32 6.5 Z" fill="url(#brandBg)" stroke="url(#brandBorder)" stroke-width="2.5" stroke-linejoin="round"/><path d="M 32 10.5 C 41 10.5 48 13.8 48 23.5 C 48 37.8 38.5 48.5 32 53 C 25.5 48.5 16 37.8 16 23.5 C 16 13.8 23 10.5 32 10.5 Z" fill="none" stroke="rgba(255, 255, 255, 0.12)" stroke-width="1.2"/><path d="M 19 21.5 C 18.5 32.5 24 40.5 32 45.5 C 27.5 39.8 24.2 33 25.4 24.8 C 26.2 20.2 29 17.6 32 16.5 C 26 16.3 19.8 18.6 19 21.5 Z" fill="url(#brandAir)"/><path d="M 45 21.5 C 45.5 32.5 40 40.5 32 45.5 C 36.5 39.8 39.8 33 38.6 24.8 C 37.8 20.2 35 17.6 32 16.5 C 38 16.3 44.2 18.6 45 21.5 Z" fill="url(#brandFusion)"/><circle cx="32" cy="31.5" r="7" fill="url(#brandCore)"/><path d="M 32 24.5 L 34.2 29.8 L 39.5 31.5 L 34.2 33.2 L 32 38.5 L 29.8 33.2 L 24.5 31.5 L 29.8 29.8 Z" fill="#FFFFFF" stroke="#BAE6FD" stroke-width="0.4"/><circle cx="32" cy="31.5" r="1.5" fill="#FFFFFF"/></svg>""",
    "pulse": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>""",
    "wind": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/></svg>""",
    "temp": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>""",
    "droplet": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>""",
    "gauge": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg>""",
    "alert": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>""",
    "chart": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>""",
    "check": """<svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>""",
}


# ==============================================================================
# REUSABLE COMPONENTS
# ==============================================================================

def safe_markdown(html: str) -> None:
    """
    Renders raw HTML safely in Streamlit without CommonMark indented code block artifacts.
    Strips leading whitespace from every line and removes empty blank lines.
    """
    clean_html = "\n".join(line.strip() for line in html.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)


def format_location_label(loc: Optional[Dict[str, Any]]) -> str:
    """
    Formats a geographic location dictionary into a non-redundant string.
    Avoids duplicate city/state names (e.g. 'Chandigarh, Chandigarh').
    """
    if not loc:
        return ""
    city = loc.get("city") or loc.get("name") or ""
    state = loc.get("state")
    country = loc.get("country")
    parts = [city] if city else []
    if state and state.strip().lower() != city.strip().lower():
        parts.append(state.strip())
    if country and country.strip().lower() not in (city.strip().lower(), (state or "").strip().lower()):
        parts.append(country.strip())
    return ", ".join(parts)


def render_section_header(
    title: str,
    subtitle: Optional[str] = None,
    badge: Optional[str] = None
) -> None:
    """
    Renders standardized section title with clean typographic hierarchy.
    """
    badge_html = f"""<span class="ag-badge ag-badge-neutral" style="margin-bottom: 8px;">{badge}</span><br>""" if badge else ""
    sub_html = f"""<p class="ag-section-subtitle" style="color: #24384D; font-size: 0.90rem; font-weight: 500; margin: 0; line-height: 1.5;">{subtitle}</p>""" if subtitle else ""

    html = f"""
    <div class="ag-section-header" style="margin-bottom: 20px;">
        {badge_html}
        <h2 class="ag-section-title" style="font-family: var(--font-heading); font-size: 1.45rem; font-weight: 800; color: #1F344C; letter-spacing: -0.02em; margin: 0 0 4px 0;">{title}</h2>
        {sub_html}
    </div>
    """
    safe_markdown(html)


def render_badge(
    label: str,
    variant: str = "neutral",
    icon: Optional[str] = None
) -> str:
    """
    Returns HTML string for an accessible pill badge.
    Variants: 'good', 'moderate', 'sensitive', 'unhealthy', 'very-unhealthy', 'hazardous', 'neutral'
    """
    icon_html = f"""<span>{icon}</span>""" if icon else ""
    return f"""<span class="ag-badge ag-badge-{variant}">{icon_html}<span>{label}</span></span>"""


def render_metric_tile(
    label: str,
    value: Any,
    unit: str = "",
    delta: Optional[str] = None,
    delta_positive: bool = True,
    subtext: str = "",
    icon: Optional[str] = None
) -> None:
    """
    Renders an atomic metric tile with tabular mono typography,
    guaranteed unified card heights, and vertically centered icon alignment.
    """
    icon_html = f"""<span style="color: var(--color-brand-cyan); margin-right: 8px; display: inline-flex; align-items: center; justify-content: center; width: 16px; height: 16px;">{ICONS.get(icon, '')}</span>""" if icon else ""
    val_str = f"{value:.1f}" if isinstance(value, float) else str(value if value is not None else "--")

    delta_color = "#34D399" if delta_positive else "#F87171"
    delta_html = f"""<span style="color: {delta_color}; font-size: 0.74rem; font-weight: 700; margin-left: 8px; font-family: var(--font-mono);">{delta}</span>""" if delta else ""
    footer_html = f"""<div class="ag-metric-footer">{subtext}</div>""" if subtext else """<div class="ag-metric-footer" style="visibility: hidden;">--</div>"""

    html = f"""
    <div class="ag-metric-card">
        <div>
            <div class="ag-metric-label">
                {icon_html}<span>{label}</span>
            </div>
            <div style="display: flex; align-items: baseline; margin-top: 6px;">
                <span class="ag-metric-val">{val_str}</span>
                <span class="ag-metric-unit">{unit}</span>
                {delta_html}
            </div>
        </div>
        {footer_html}
    </div>
    """
    safe_markdown(html)


def render_callout(
    title: str,
    message: str,
    variant: str = "info",
    icon: Optional[str] = None
) -> None:
    """
    Renders accessible callout banner for notifications, alerts, or AI synthesis.
    Supports 'info', 'success', 'warning', and 'danger' variants.
    """
    icon_markup = ICONS.get(icon, ICONS["alert"]) if icon else ICONS["alert"]
    if variant == "info":
        border_color = "var(--color-brand-cyan)"
        bg_color = "rgba(56, 189, 248, 0.08)"
    elif variant == "success":
        border_color = "#10B981"
        bg_color = "rgba(16, 185, 129, 0.08)"
    elif variant == "warning":
        border_color = "#F59E0B"
        bg_color = "rgba(245, 158, 11, 0.08)"
    else:
        border_color = "#EF4444"
        bg_color = "rgba(239, 68, 68, 0.08)"

    html = f"""
    <div class="ag-callout" style="
        border-left: 4px solid {border_color};
        background: {bg_color};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.05), 0 10px 25px -5px rgba(0, 0, 0, 0.35);
        border-radius: var(--radius-md);
        padding: 16px 20px;
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    ">
        <div class="ag-callout-title" style="color: {border_color}; font-family: var(--font-heading); font-weight: 700; letter-spacing: 0.04em; margin-bottom: 6px; text-transform: uppercase;">
            <span style="display: flex; align-items: center;">{icon_markup}</span>
            <span>{title}</span>
        </div>
        <div class="ag-callout-body" style="font-family: var(--font-sans); font-size: var(--font-size-sm); color: var(--color-text-primary); line-height: 1.6;">
            {message}
        </div>
    </div>
    """
    safe_markdown(html)


def render_hero_banner(
    title: str,
    description: str,
    stat_value: Optional[str] = None,
    stat_label: Optional[str] = None,
    badge_text: Optional[str] = None
) -> None:
    """
    Renders visual hero banner with generous intentional whitespace and cinematic optical depth.
    """
    badge_html = f"""<span class="ag-badge ag-badge-neutral" style="margin-bottom: 12px;">{badge_text}</span>""" if badge_text else ""
    stat_html = ""
    if stat_value:
        stat_html = f"""
        <div style="text-align: right; min-width: 140px;">
            <div style="font-family: var(--font-mono); font-size: var(--font-size-3xl); font-weight: 800; color: var(--color-brand-cyan); line-height: 1; text-shadow: 0 0 20px var(--color-brand-cyan-glow);">
                {stat_value}
            </div>
            <div style="font-family: var(--font-mono); font-size: var(--font-size-xs); font-weight: 700; color: var(--color-text-secondary); text-transform: uppercase; margin-top: 6px; letter-spacing: 0.05em;">
                {stat_label or ""}
            </div>
        </div>
        """

    html = f"""
    <div class="ag-card ag-hero-banner" style="
        padding: 30px 36px;
        margin-bottom: 24px;
        background: radial-gradient(ellipse 85% 70% at 90% 15%, rgba(56, 189, 248, 0.12), transparent 70%), linear-gradient(135deg, rgba(17, 24, 39, 0.94) 0%, rgba(8, 12, 20, 0.98) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.1), 0 20px 45px -10px rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-radius: var(--radius-xl);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
            <div style="max-width: 700px;">
                {badge_html}
                <h1 style="margin: 0 0 8px 0; font-family: var(--font-heading); font-size: var(--font-size-2xl); font-weight: 800; color: var(--color-text-primary); letter-spacing: -0.025em; text-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);">
                    {title}
                </h1>
                <p style="margin: 0; font-family: var(--font-sans); font-size: var(--font-size-sm); color: var(--color-text-secondary); line-height: 1.6;">
                    {description}
                </p>
            </div>
            {stat_html}
        </div>
    </div>
    """
    safe_markdown(html)


def format_location_label(loc: dict | None, fallback: str = "Unknown Location") -> str:
    """
    Formats a geocoded location dictionary into a clean, non-redundant 'City, State, Country' string.
    Ensures city place name is ALWAYS shown prominently and never omitted.
    Deduplicates identical city and administrative region names (e.g., 'Chandigarh, Chandigarh' -> 'Chandigarh, India').
    """
    if not loc or not isinstance(loc, dict):
        return fallback

    # Extract city / place name from any common key variant
    city_name = str(loc.get("city") or loc.get("name") or "").strip()
    if not city_name:
        city_name = fallback

    # Extract state / province / administrative region
    state_name = str(loc.get("state") or loc.get("admin1") or loc.get("region") or "").strip()

    # Extract country
    country_name = str(loc.get("country") or "").strip()

    parts = [city_name]

    # Only include state if distinct from city
    if state_name and state_name.lower() != city_name.lower():
        parts.append(state_name)

    # Include country if distinct from both city and state
    if country_name and country_name.lower() != city_name.lower() and country_name.lower() != state_name.lower():
        parts.append(country_name)

    return ", ".join(parts)

