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
CSS_PATH = ASSETS_DIR / "style.css"


def inject_foundation_styles() -> None:
    """
    Injects the design system stylesheet into the Streamlit DOM.
    """
    if CSS_PATH.exists():
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


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
    Renders an atomic metric tile with tabular mono typography.
    """
    icon_html = f"""<span style="color: var(--color-brand-cyan); margin-right: 6px;">{ICONS.get(icon, '')}</span>""" if icon else ""
    val_str = f"{value:.1f}" if isinstance(value, float) else str(value if value is not None else "--")

    delta_color = "#34D399" if delta_positive else "#F87171"
    delta_html = f"""<span style="color: {delta_color}; font-size: var(--font-size-xs); font-weight: 600; margin-left: 6px;">{delta}</span>""" if delta else ""
    footer_html = f"""<div class="ag-metric-footer">{subtext}</div>""" if subtext else ""

    html = f"""
    <div class="ag-metric-card">
        <div>
            <div class="ag-metric-label">
                {icon_html}{label}
            </div>
            <div style="display: flex; align-items: baseline;">
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
    <div class="ag-callout" style="border-left-color: {border_color}; background: {bg_color};">
        <div class="ag-callout-title" style="color: {border_color};">
            <span style="display: flex; align-items: center;">{icon_markup}</span>
            <span>{title}</span>
        </div>
        <div class="ag-callout-body">
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
    Renders visual hero banner with generous intentional whitespace.
    """
    badge_html = f"""<span class="ag-badge ag-badge-neutral" style="margin-bottom: 12px;">{badge_text}</span>""" if badge_text else ""
    stat_html = ""
    if stat_value:
        stat_html = f"""
        <div style="text-align: right; min-width: 140px;">
            <div style="font-family: var(--font-mono); font-size: var(--font-size-3xl); font-weight: 800; color: var(--color-brand-cyan); line-height: 1;">
                {stat_value}
            </div>
            <div style="font-size: var(--font-size-xs); font-weight: 700; color: var(--color-text-secondary); text-transform: uppercase; margin-top: 4px;">
                {stat_label or ""}
            </div>
        </div>
        """

    html = f"""
    <div class="ag-card" style="padding: 28px 32px; margin-bottom: 24px; background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(8, 12, 20, 0.95) 100%);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
            <div style="max-width: 680px;">
                {badge_html}
                <h1 style="margin: 0 0 8px 0; font-size: var(--font-size-2xl); font-weight: 800; color: var(--color-text-primary); letter-spacing: -0.02em;">
                    {title}
                </h1>
                <p style="margin: 0; font-size: var(--font-size-sm); color: var(--color-text-secondary); line-height: 1.55;">
                    {description}
                </p>
            </div>
            {stat_html}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def format_location_label(loc: dict | None) -> str:
    """
    Formats a geocoded location dictionary into a clean, non-redundant 'City, State, Country' string.
    Deduplicates identical city and administrative region names (e.g., 'Chandigarh, Chandigarh' -> 'Chandigarh, India').
    """
    if not loc or not isinstance(loc, dict):
        return "Unknown Location"
    name = str(loc.get("name", "")).strip()
    admin1 = str(loc.get("admin1", "")).strip() if loc.get("admin1") else ""
    country = str(loc.get("country", "")).strip() if loc.get("country") else ""

    parts = [name] if name else []
    if admin1 and admin1.lower() != name.lower():
        parts.append(admin1)
    if country:
        parts.append(country)

    return ", ".join(parts) if parts else (name or "Unknown Location")

