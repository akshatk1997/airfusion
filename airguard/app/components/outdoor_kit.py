"""
Outdoor Departure Kit, Packing Checklist, & Symptom Soothers for Simple Mode.
Exclusively designed for non-technical users, kids, and families.
Features:
- Dynamic 'What to Carry Outside' checklist evaluated against real-time air telemetry.
- Interactive backpack packing meter where users can check off items before heading out.
- Real-life outdoor situation precautions (traffic lights, playground recess, dog walks, jog times).
- Doctor-approved home comfort soothing remedies (itchy throat, burning eyes, cough, headache) in plain English.
- Clear red-flag medical safety guidance without confusing jargon.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
import streamlit as st
from app.components.simple_cards import get_mascot_base64


def render_outdoor_departure_kit(
    city_name: str,
    pm25: float,
    aqi: int,
    temp: float,
    wind: float,
    humidity: float,
    user_profile: Optional[Dict[str, Any]] = None
) -> None:
    """
    Renders the dynamic 'What to Carry Today & Outdoor Survival Kit'
    with interactive checklist and symptom soothers.
    """
    prof = user_profile or {}
    sensitivity = prof.get("health_sensitivity", "none")
    age = prof.get("age_group", "adult")
    activity = prof.get("usual_activities", "walk")
    is_sensitive = sensitivity != "none" or age in ["child", "senior"]

    mascot_runner = get_mascot_base64("mascot_outdoor_runner.jpg")
    mascot_mask = get_mascot_base64("mascot_caution_mask.jpg")
    mascot_sanctuary = get_mascot_base64("mascot_indoor_sanctuary.jpg")

    # Header section
    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 20px; padding: 24px 28px; margin-bottom: 24px; box-shadow: 0 4px 18px rgba(31, 52, 76, 0.05);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="font-size: 2.2rem;">🎒</div>
                    <div>
                        <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(255, 104, 69, 0.08); border: 1px solid rgba(255, 104, 69, 0.25); border-radius: 9999px; padding: 3px 12px; margin-bottom: 6px;">
                            <span class="ensur-pulse-dot" style="width: 6px; height: 6px; background: #FF6845;"></span>
                            <span style="font-family: var(--font-heading); font-size: 0.7rem; font-weight: 800; color: #FF6845; text-transform: uppercase;">
                                SMART DEPARTURE KIT — {city_name}
                            </span>
                        </div>
                        <h2 style="font-family: var(--font-heading); font-size: 1.5rem; font-weight: 800; color: #1F344C; margin: 0; line-height: 1.2;">
                            What to Carry Outside & Outdoor Safety Kit
                        </h2>
                        <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 4px 0 0 0;">
                            Live recommendations tailored to today's {temp:.0f}°C temperature, {wind:.0f} km/h breeze, and air condition.
                        </p>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------------------------------
    # PART 1: INTERACTIVE BACKPACK PACKING CHECKLIST
    # -------------------------------------------------------------------------
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.2rem; font-weight: 800; color: #1F344C; margin: 16px 0 12px 0;'>🎒 Your Superhero Outdoor Backpack Checklist</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0 0 14px 0;'>Check off each item before leaving your doorstep so you're 100% protected against outdoor air hazards!</p>", unsafe_allow_html=True)

    # Determine recommended status for each item
    # 1. Mask
    if pm25 > 55:
        mask_need = "🔴 Essential Today"
        mask_desc = f"Air pollution is high ({pm25:.0f} µg/m³). Pack a snug N95 or well-fitting mask to keep micro-dust out of your lungs."
        mask_default = True
    elif pm25 > 35:
        mask_need = "🟡 Recommended"
        mask_desc = "Air is slightly elevated. Highly recommended if walking near traffic, waiting at bus stops, or if you have sensitive lungs."
        mask_default = is_sensitive
    else:
        mask_need = "🟢 Optional"
        mask_desc = "Air is clean! Mask is not required unless you are sensitive to dust or walking through smoky street corners."
        mask_default = False

    # 2. Water
    water_desc = "Hydration is your secret weapon! Drinking water keeps your throat moist and flushes swallowed dust specks safely down into your stomach."

    # 3. Sunglasses
    sunglass_desc = "Wraparound sunglasses shield your eyes from drying winds, blowing street grit, and UV sunshine smog."

    # 4. Saline drops
    saline_desc = "Gentle saline eye drops rinse itchy soot out of your eyes without harsh rubbing. Great to keep in a side pocket."

    # 5. Inhaler / Meds
    if is_sensitive:
        inhaler_need = "🔴 Must-Have for Sensitive Lungs"
        inhaler_desc = f"Your profile is set for {sensitivity.title()} sensitivity. Always keep your doctor-prescribed rescue inhaler in your pocket or bag."
    else:
        inhaler_need = "🟢 Routine Precaution"
        inhaler_desc = "If you or anyone in your group has allergies or breathing sensitivities, verify comfort medicines before heading out."

    # 6. Light scarf / jacket
    jacket_desc = "A light windbreaker or cotton scarf keeps road soot and pollen off your neck, hair, and clothing."

    # Render checklist in two columns
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <strong style="font-family: var(--font-heading); font-size: 0.95rem; color: #1F344C;">😷 1. Clean-Air Protective Mask</strong>
                    <span style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700; color: {'#D71921' if pm25 > 55 else ('#D97706' if pm25 > 35 else '#059669')};">{mask_need}</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; margin-bottom: 10px;">{mask_desc}</div>
                """,
                unsafe_allow_html=True
            )
            item_mask = st.checkbox("Packed my clean-air mask in my bag", value=mask_default, key="pack_mask")

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <strong style="font-family: var(--font-heading); font-size: 0.95rem; color: #1F344C;">💧 2. Fresh Water Bottle</strong>
                    <span style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700; color: #059669;">🟢 Essential Every Day</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; margin-bottom: 10px;">{water_desc}</div>
                """,
                unsafe_allow_html=True
            )
            item_water = st.checkbox("Packed my filled water bottle", value=True, key="pack_water")

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <strong style="font-family: var(--font-heading); font-size: 0.95rem; color: #1F344C;">🕶️ 3. Wind & UV Sunglasses</strong>
                    <span style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700; color: #059669;">🟢 Eye Shield</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; margin-bottom: 10px;">{sunglass_desc}</div>
                """,
                unsafe_allow_html=True
            )
            item_glasses = st.checkbox("Packed sunglasses for eye protection", value=False, key="pack_glasses")

    with col_c2:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <strong style="font-family: var(--font-heading); font-size: 0.95rem; color: #1F344C;">🫁 4. Prescribed Inhaler / Allergy Comfort</strong>
                    <span style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700; color: {'#D71921' if is_sensitive else '#5A6E85'};">{inhaler_need}</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; margin-bottom: 10px;">{inhaler_desc}</div>
                """,
                unsafe_allow_html=True
            )
            item_inhaler = st.checkbox("Packed inhaler / allergy medicine (if needed)", value=is_sensitive, key="pack_inhaler")

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <strong style="font-family: var(--font-heading); font-size: 0.95rem; color: #1F344C;">🩹 5. Soothing Saline Eye Drops</strong>
                    <span style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700; color: #059669;">🟢 Relief Kit</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; margin-bottom: 10px;">{saline_desc}</div>
                """,
                unsafe_allow_html=True
            )
            item_saline = st.checkbox("Packed gentle saline eye/nose drops", value=False, key="pack_saline")

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <strong style="font-family: var(--font-heading); font-size: 0.95rem; color: #1F344C;">🧥 6. Light Outer Layer / Scarf</strong>
                    <span style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700; color: #059669;">🟢 Dust Barrier</span>
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85; margin-bottom: 10px;">{jacket_desc}</div>
                """,
                unsafe_allow_html=True
            )
            item_jacket = st.checkbox("Wearing/packed light jacket or cotton scarf", value=True, key="pack_jacket")

    # Live Packing Readiness Score
    packed_count = sum([item_mask, item_water, item_glasses, item_inhaler, item_saline, item_jacket])
    pct_packed = int((packed_count / 6) * 100)

    st.markdown(
        f"""
        <div style="background: {'#ECFDF5' if pct_packed >= 65 else '#FFFBEB'}; border: 1px solid {'rgba(16, 185, 129, 0.3)' if pct_packed >= 65 else 'rgba(245, 158, 11, 0.3)'}; border-radius: 14px; padding: 14px 20px; margin: 16px 0 28px 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.5rem;">{'🎉' if pct_packed >= 65 else '🎒'}</span>
                <div>
                    <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 800; color: {'#059669' if pct_packed >= 65 else '#B45309'};">
                        Backpack Readiness: {packed_count} of 6 Items Packed ({pct_packed}%)
                    </div>
                    <div style="font-family: var(--font-sans); font-size: 0.8rem; color: #5A6E85;">
                        {'You are super prepared to step outside with full confidence!' if pct_packed >= 65 else 'Pack a couple more items to ensure full protection against outdoor dust.'}
                    </div>
                </div>
            </div>
            <div style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 700; background: #FFFFFF; border: 1px solid #EBE6DF; padding: 4px 12px; border-radius: 9999px; color: #1F344C;">
                DEPARTURE STATUS: {'CLEARED FOR OUTDOORS ✅' if pct_packed >= 65 else 'PACKING IN PROGRESS ⏳'}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------------------------------
    # PART 2: REAL-LIFE OUTDOOR PRECAUTIONS (Roads, Playgrounds, Pets, Exertion)
    # -------------------------------------------------------------------------
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.2rem; font-weight: 800; color: #1F344C; margin: 16px 0 12px 0;'>🛡️ Real-Life Outdoor Situations: How to Stay Protected</h3>", unsafe_allow_html=True)

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    with col_s1:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-top: 3px solid #FF6845; border-radius: 14px; padding: 18px 16px; height: 100%; box-shadow: 0 4px 12px rgba(31, 52, 76, 0.04);">
                <div style="font-size: 1.8rem; margin-bottom: 8px;">🚦</div>
                <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                    Busy Roads & Traffic
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.8rem; color: #5A6E85; line-height: 1.45;">
                    Stay 6 feet back from street curbs when waiting for traffic lights. Bus and truck exhaust pipes shoot fumes at bumper height where children breathe!
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_s2:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-top: 3px solid #10B981; border-radius: 14px; padding: 18px 16px; height: 100%; box-shadow: 0 4px 12px rgba(31, 52, 76, 0.04);">
                <div style="font-size: 1.8rem; margin-bottom: 8px;">🏫</div>
                <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                    School & Playgrounds
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.8rem; color: #5A6E85; line-height: 1.45;">
                    Play on grass rather than bare dry dirt. After recess, have kids splash cool water on face and wash hands to remove settled particles.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_s3:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-top: 3px solid #0284C7; border-radius: 14px; padding: 18px 16px; height: 100%; box-shadow: 0 4px 12px rgba(31, 52, 76, 0.04);">
                <div style="font-size: 1.8rem; margin-bottom: 8px;">🐕</div>
                <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                    Dog & Pet Walking
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.8rem; color: #5A6E85; line-height: 1.45;">
                    Dogs sniff close to ground soot. Choose grassy neighborhood parks over paved streets, and gently wipe paws and coat with a damp towel upon return.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_s4:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-top: 3px solid #8B5CF6; border-radius: 14px; padding: 18px 16px; height: 100%; box-shadow: 0 4px 12px rgba(31, 52, 76, 0.04);">
                <div style="font-size: 1.8rem; margin-bottom: 8px;">🌳</div>
                <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 800; color: #1F344C; margin-bottom: 6px;">
                    Green Park Advantage
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.8rem; color: #5A6E85; line-height: 1.45;">
                    Tree-lined avenues and municipal parks have up to 25% cleaner air! Leaves naturally trap soot particles and release oxygen.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------------------------------------------------------
    # PART 3: DOCTOR-APPROVED SYMPTOM SOOTHERS & HOME FIRST-AID (Zero Jargon)
    # -------------------------------------------------------------------------
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.2rem; font-weight: 800; color: #1F344C; margin: 16px 0 12px 0;'>💊 Symptom Soothers & Home First-Aid (What to Do If You Feel Uncomfortable)</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0 0 14px 0;'>Simple, safe, doctor-approved comfort measures to soothe irritation caused by outdoor dust and air pollution.</p>", unsafe_allow_html=True)

    col_med1, col_med2 = st.columns(2)

    with col_med1:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 20px; margin-bottom: 14px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.04);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <span style="font-size: 1.6rem;">🗣️</span>
                    <div>
                        <div style="font-family: var(--font-heading); font-size: 1rem; font-weight: 800; color: #1F344C;">
                            Itchy or Scratchy Throat
                        </div>
                        <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #FF6845; font-weight: 700;">
                            SOOTHING STEP 1
                        </div>
                    </div>
                </div>
                <ul style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; margin: 0 0 0 18px; padding: 0; line-height: 1.55;">
                    <li><strong>Warm Honey Water:</strong> Stir 1 teaspoon of pure honey into a warm mug of water. Honey naturally coats and calms throat nerve endings.</li>
                    <li><strong>Warm Salt-Water Gargle:</strong> For older kids and adults, mix 1/2 teaspoon of salt in warm water and gargle for 30 seconds to flush soot particles.</li>
                    <li><strong>Frequent Small Sips:</strong> Keep water moving down your throat so dust doesn't linger.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 20px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.04);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <span style="font-size: 1.6rem;">🫁</span>
                    <div>
                        <div style="font-family: var(--font-heading); font-size: 1rem; font-weight: 800; color: #1F344C;">
                            Dry Cough & Chest Heaviness
                        </div>
                        <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #059669; font-weight: 700;">
                            SOOTHING STEP 2
                        </div>
                    </div>
                </div>
                <ul style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; margin: 0 0 0 18px; padding: 0; line-height: 1.55;">
                    <li><strong>Steam Inhalation:</strong> Breathe warm moist steam from a warm shower or a bowl of hot water for 5–10 minutes to loosen airway tightness.</li>
                    <li><strong>Clean Air Room Retreat:</strong> Rest in a closed bedroom with doors and windows shut and an air cleaner or gentle fan running.</li>
                    <li><strong>Prescribed Rescue Inhaler:</strong> If diagnosed with asthma or reactive airway, follow your doctor's plan for using your rescue inhaler.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_med2:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 20px; margin-bottom: 14px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.04);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <span style="font-size: 1.6rem;">👁️</span>
                    <div>
                        <div style="font-family: var(--font-heading); font-size: 1rem; font-weight: 800; color: #1F344C;">
                            Burning or Watery Red Eyes
                        </div>
                        <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #0284C7; font-weight: 700;">
                            SOOTHING STEP 3
                        </div>
                    </div>
                </div>
                <ul style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; margin: 0 0 0 18px; padding: 0; line-height: 1.55;">
                    <li><strong>DO NOT Rub Your Eyes:</strong> Rubbing pushes microscopic dust grains into the sensitive cornea and makes itching 10x worse!</li>
                    <li><strong>Cool Damp Cloth Compress:</strong> Fold a clean washcloth soaked in cool water and place it gently over closed eyes for 5 minutes.</li>
                    <li><strong>Preservative-Free Saline Drops:</strong> Rinse eyes with gentle lubricating eye drops to wash out trapped soot.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 20px; box-shadow: 0 4px 14px rgba(31, 52, 76, 0.04);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <span style="font-size: 1.6rem;">🤕</span>
                    <div>
                        <div style="font-family: var(--font-heading); font-size: 1rem; font-weight: 800; color: #1F344C;">
                            Smog Headache & Tiredness
                        </div>
                        <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #8B5CF6; font-weight: 700;">
                            SOOTHING STEP 4
                        </div>
                    </div>
                </div>
                <ul style="font-family: var(--font-sans); font-size: 0.84rem; color: #5A6E85; margin: 0 0 0 18px; padding: 0; line-height: 1.55;">
                    <li><strong>Big Glass of Cold Water:</strong> Air pollution increases mild dehydration; drink 2 full glasses of water right away.</li>
                    <li><strong>Dim Room Rest:</strong> Close curtains and rest your eyes for 20 minutes away from digital screens.</li>
                    <li><strong>Avoid Heavy Chores:</strong> Give your body a rest and avoid doing intense outdoor cleaning or lifting while the air is dirty.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Red Flag Medical Warning Card
    st.markdown(
        """
        <div style="background: #FEF2F2; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 14px; padding: 16px 20px; margin-top: 20px; display: flex; align-items: flex-start; gap: 14px;">
            <span style="font-size: 1.6rem; line-height: 1;">🚨</span>
            <div>
                <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 800; color: #991B1B; margin-bottom: 4px;">
                    When to Ask an Adult / Seek Immediate Medical Attention
                </div>
                <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #7F1D1D; line-height: 1.5;">
                    If someone experiences severe difficulty breathing, cannot finish a sentence without gasping, has bluish lips or fingernails, feels chest tightness or pain, or if asthma rescue inhaler does not provide relief within 15 minutes, seek emergency medical care immediately.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
