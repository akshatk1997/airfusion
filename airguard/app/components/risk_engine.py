"""
Risk Engine UI Component for AirGuard — My Safe Outdoor Plan.
Renders risk gauge cards, transparent rationale breakdowns,
and composite risk category indicators with Plus Jakarta Sans & JetBrains Mono typography.
"""

from __future__ import annotations

import streamlit as st
from typing import Dict, Any, Optional
from app.components.design_system import safe_markdown


def render_risk_score_card(
    risk_score: int,
    risk_category: str,
    reason: str,
    action: str
) -> None:
    """
    Renders high-impact Nothing OS risk evaluation card with score meter,
    crisp category badge, and transparent 'why' explanation.
    """
    if risk_category == "Low":
        cat_color = "#10B981"
        cat_bg = "rgba(16, 185, 129, 0.12)"
    elif risk_category == "Moderate":
        cat_color = "#F59E0B"
        cat_bg = "rgba(245, 158, 11, 0.12)"
    elif risk_category == "High":
        cat_color = "#F97316"
        cat_bg = "rgba(249, 115, 22, 0.12)"
    else: # Very High
        cat_color = "#D71921"
        cat_bg = "rgba(215, 25, 33, 0.15)"

    pct = min(100, max(5, risk_score))

    html = f"""
    <div style="
        background: #121212;
        border: 1px solid #242424;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: none;
    ">
        <div style="display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 20px; margin-bottom: 16px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <span style="
                        background: {cat_bg};
                        border: 1px solid {cat_color};
                        color: {cat_color};
                        font-family: var(--font-sans);
                        font-size: 0.76rem;
                        font-weight: 700;
                        padding: 3px 12px;
                        border-radius: 9999px;
                        letter-spacing: 0.05em;
                        text-transform: uppercase;
                    ">
                        ● {risk_category} Risk
                    </span>
                    <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #777777; text-transform: uppercase; letter-spacing: 0.05em;">
                        Personal Outdoor Risk Score
                    </span>
                </div>
                <div style="font-family: var(--font-heading); font-size: 1.45rem; font-weight: 700; color: #FFFFFF; line-height: 1.3;">
                    {action}
                </div>
            </div>
            <div style="text-align: right; min-width: 100px;">
                <div style="font-family: var(--font-mono); font-size: 3.8rem; font-weight: 800; line-height: 0.9; color: {cat_color};">
                    {risk_score}
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #777777; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 4px;">
                    Out of 100
                </div>
            </div>
        </div>

        <!-- Risk Progress Bar -->
        <div style="margin-bottom: 16px;">
            <div style="height: 6px; background: #202020; border-radius: 9999px; position: relative;">
                <div style="
                    width: {pct}%;
                    height: 100%;
                    background: {cat_color};
                    border-radius: 9999px;
                    transition: width 0.5s ease;
                "></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.68rem; font-family: var(--font-mono); color: #666666; margin-top: 6px;">
                <span>0 Low</span>
                <span>25</span>
                <span>50 Moderate</span>
                <span>75 High</span>
                <span>100 Very High</span>
            </div>
        </div>

        <!-- Transparent 'Why' Rationale -->
        <div style="
            background: #181818;
            border-left: 3px solid {cat_color};
            border-radius: 8px;
            padding: 12px 16px;
            font-family: var(--font-sans);
            font-size: 0.82rem;
            color: #CCCCCC;
            line-height: 1.5;
        ">
            <b style="color: #FFFFFF;">Why:</b> {reason}
        </div>
    </div>
    """
    safe_markdown(html)
