"""
AirGuard Reusable Design System Component Library.
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
    "shield": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>""",
    "pulse": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>""",
    "wind": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/></svg>""",
    "temp": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>""",
    "droplet": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>""",
    "gauge": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg>""",
    "alert": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>""",
    "chart": """<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>""",
    "check": """<svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>"""
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
    sub_html = f"""<p class="ag-section-subtitle">{subtitle}</p>""" if subtitle else ""

    html = f"""
    <div class="ag-section-header">
        {badge_html}
        <h2 class="ag-section-title">{title}</h2>
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

