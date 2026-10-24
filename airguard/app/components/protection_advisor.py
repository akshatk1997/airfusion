"""
Protection Advisor UI Component for AirGuard — My Safe Outdoor Plan.
Renders practical, non-medical mask and indoor protection guidance,
along with prominent safety disclaimers.
"""

from __future__ import annotations

import streamlit as st
from typing import Dict, Any, List
from app.components.design_system import safe_markdown


def render_protection_protocol_card(
    mask_guidance: str,
    indoor_guidance: List[str],
    risk_category: str
) -> None:
    """
    Renders practical mask and indoor barrier protocols in Nothing OS style.
    """
    indoor_items = "".join([f"<li style='margin-bottom: 6px;'>{g}</li>" for g in indoor_guidance])

    badge_color = "#10B981" if risk_category in ["Low", "Moderate"] else ("#F97316" if risk_category == "High" else "#D71921")

    html = f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #EBE6DF;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(31, 52, 76, 0.05);
    ">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
            <div style="font-family: var(--font-heading); font-size: 0.85rem; font-weight: 800; color: #1F344C; text-transform: uppercase; letter-spacing: 0.05em;">
                🛡️ Protective Protocol & Indoor Defense
            </div>
            <span style="
                border: 1px solid {badge_color};
                color: {badge_color};
                font-family: var(--font-sans);
                font-size: 0.68rem;
                font-weight: 700;
                padding: 2px 10px;
                border-radius: 9999px;
                text-transform: uppercase;
            ">
                {risk_category} Level
            </span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 18px;">
            <!-- Mask Guidance -->
            <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 12px; padding: 18px 20px;">
                <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #1F344C; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                    😷 Respiratory Mask Protocol
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; line-height: 1.55;">
                    {mask_guidance}
                </div>
            </div>

            <!-- Indoor Precautions -->
            <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 12px; padding: 18px 20px;">
                <div style="font-family: var(--font-heading); font-size: 0.74rem; font-weight: 800; color: #1F344C; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                    🏠 Indoor & In-Vehicle Air Quality
                </div>
                <ul style="margin: 0; padding-left: 18px; font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; line-height: 1.55;">
                    {indoor_items}
                </ul>
            </div>
        </div>

        <!-- Visible Medical Disclaimer -->
        <div style="
            background: #FAF6F1;
            border: 1px solid #EBE6DF;
            border-left: 3px solid #FF6845;
            padding: 10px 14px;
            border-radius: 8px;
            font-family: var(--font-sans);
            font-size: 0.74rem;
            color: #5A6E85;
            line-height: 1.45;
        ">
            <strong style="color: #1F344C;">Disclaimer:</strong> AirGuard provides general environmental decision support based on outdoor sensor telemetry and numerical ML projections. It does not provide medical diagnosis, treatment, or individualized clinical advice. Users with respiratory or cardiac conditions should always adhere to their medical provider’s prescription plan.
        </div>
    </div>
    """
    safe_markdown(html)
