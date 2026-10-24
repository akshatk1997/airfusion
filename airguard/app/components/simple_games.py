"""
Interactive Games, Quizzes, & Eco Puzzles for Simple Mode.
Exclusively designed for non-technical users, kids, and families.
Features:
- Game 1: 'Pack My Clean Air Backpack' (interactive inventory evaluation against today's air).
- Game 2: 'Clean Air Detective: Mystery of the Hazy Hour' (story-driven deduction puzzle).
- Game 3: 'The Great Eco & Clean Air Trivia Quiz' (5-question educational trivia with immediate feedback).
- Game 4: 'Guess the Freshest Air Window' (prediction intuition game).
- Trophy Case & 3D Cartoon Achievement Badges (state-persisted).
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
import streamlit as st
from app.components.simple_cards import get_mascot_base64


def get_game_state() -> Dict[str, Any]:
    """Retrieves or initializes game state from st.session_state."""
    if "eco_game_state" not in st.session_state:
        st.session_state["eco_game_state"] = {
            "badges_unlocked": set(),
            "quiz_score": None,
            "quiz_answers": {},
            "detective_solved": False,
            "backpack_score": None,
            "hour_guess_made": False,
        }
    return st.session_state["eco_game_state"]


def render_eco_quest_hub(
    city_name: str,
    pm25: float,
    aqi: int,
    temp: float,
    wind: float,
    best_time: str
) -> None:
    """
    Renders the complete Aero's Eco & Clean Air Adventure Quest Hub.
    """
    state = get_game_state()
    mascot_clean = get_mascot_base64("mascot_clean_air.jpg")
    mascot_runner = get_mascot_base64("mascot_outdoor_runner.jpg")
    mascot_mask = get_mascot_base64("mascot_caution_mask.jpg")
    mascot_sanctuary = get_mascot_base64("mascot_indoor_sanctuary.jpg")

    # Header Card
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #FAF6F1 0%, #FFFFFF 100%); border: 1px solid #EBE6DF; border-left: 5px solid #10B981; border-radius: 20px; padding: 24px 28px; margin-bottom: 24px; box-shadow: 0 4px 18px rgba(31, 52, 76, 0.05);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <span style="font-size: 2.2rem;">🎮</span>
                    <div>
                        <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 9999px; padding: 3px 12px; margin-bottom: 6px;">
                            <span class="ag-pulse-dot" style="width: 6px; height: 6px; background: #10B981;"></span>
                            <span style="font-family: var(--font-heading); font-size: 0.7rem; font-weight: 800; color: #059669; text-transform: uppercase;">
                                ADVENTURE & LEARNING HUB
                            </span>
                        </div>
                        <h2 style="font-family: var(--font-heading); font-size: 1.55rem; font-weight: 800; color: #1F344C; margin: 0; line-height: 1.2;">
                            Aero's Clean Air Adventure Quest Hub
                        </h2>
                        <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 4px 0 0 0;">
                            Fun games, story mysteries, and eco quizzes to help kids and families learn air safety together!
                        </p>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-family: var(--font-heading); font-size: 0.8rem; font-weight: 800; background: #FFFFFF; border: 1px solid #EBE6DF; padding: 6px 14px; border-radius: 9999px; color: #1F344C; box-shadow: 0 2px 8px rgba(31, 52, 76, 0.05);">
                        🏆 Badges Unlocked: <strong style="color: #FF6845;">{len(state['badges_unlocked'])} / 4</strong>
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Tabs for the 4 Games + Trophy Case
    tab_pack, tab_detective, tab_quiz, tab_guess, tab_trophy = st.tabs([
        "🎒 Pack My Backpack Game",
        "🕵️ Clean Air Detective Mystery",
        "🌱 Eco & Clean Air Quiz",
        "💨 Guess Freshest Air Hour",
        "🏆 Trophy Case & Badges"
    ])

    # -------------------------------------------------------------------------
    # GAME 1: PACK MY BACKPACK GAME
    # -------------------------------------------------------------------------
    with tab_pack:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 20px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
                    <span style="font-size: 1.8rem;">🎒</span>
                    <div>
                        <div style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 800; color: #1F344C;">
                            Mini-Game: Pack for Today's Air in {city_name}
                        </div>
                        <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85;">
                            Current PM₂.₅ is <strong>{pm25:.0f} µg/m³</strong>. Select the right items from the rack to pack into your virtual adventure backpack!
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Inventory Rack Items
        rack_items = [
            ("mask", "😷 Clean-Air Snug Mask", "Essential if PM2.5 > 35"),
            ("water", "💧 Fresh Water Bottle", "Essential every single day!"),
            ("sunglasses", "🕶️ UV & Wind Sunglasses", "Shields eyes from blowing dust"),
            ("video_game", "🎮 Handheld Game Console", "Fun, but not an air-safety item!"),
            ("inhaler", "🫁 Pocket Asthma Inhaler", "Must-have if lungs are sensitive"),
            ("candy", "🍬 Jumbo Bag of Lollipops", "Yummy, but doesn't block micro-dust!"),
            ("saline", "🩹 Soothing Saline Eye Drops", "Calms red, itchy eyes"),
            ("scarf", "🧣 Cotton Scarf / Jacket", "Stops soot from settling on skin")
        ]

        st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.85rem; color: #1F344C;'>Select items to put into your bag:</strong>", unsafe_allow_html=True)
        col_r1, col_r2 = st.columns(2)
        selected_pack = []

        for idx, (item_id, item_label, item_hint) in enumerate(rack_items):
            target_col = col_r1 if idx < 4 else col_r2
            with target_col:
                checked = st.checkbox(f"{item_label} — {item_hint}", key=f"g1_item_{item_id}")
                if checked:
                    selected_pack.append(item_id)

        if st.button("🎒 Check My Backpack! 🚀", key="btn_check_backpack", use_container_width=True):
            # Calculate score
            score = 0
            feedback = []

            # Water is always required
            if "water" in selected_pack:
                score += 30
                feedback.append("✅ Great job packing water! It flushes swallowed dust specks safely down into your stomach.")
            else:
                feedback.append("❌ Oops! You forgot water. Hydration is essential to wash dust away from your throat.")

            # Mask evaluated based on PM2.5
            if pm25 > 35:
                if "mask" in selected_pack:
                    score += 35
                    feedback.append(f"✅ Superhero move! Because {city_name}'s air is slightly dusty today, your mask will block microscopic particles.")
                else:
                    feedback.append("⚠️ Watch out! Today's air has elevated dust; an N95 or snug mask is strongly recommended.")
            else:
                if "mask" in selected_pack:
                    score += 25
                    feedback.append("✅ Safe choice! The air is clean today, but carrying a mask in your pocket is great if traffic gets smoky.")
                else:
                    score += 35
                    feedback.append("✅ Smart deduction! Today's air is clean, so you don't necessarily need a mask for park strolls.")

            # Sunglasses or Saline
            if "sunglasses" in selected_pack or "saline" in selected_pack:
                score += 20
                feedback.append("✅ Eye protection ready! Sunglasses and saline drops keep itchy road grit out of sensitive eyes.")

            # Scarf or Inhaler
            if "inhaler" in selected_pack or "scarf" in selected_pack:
                score += 15
                feedback.append("✅ Extra defense! You packed protection for sensitive lungs and skin.")

            # Distractors penalty (playful)
            if "video_game" in selected_pack or "candy" in selected_pack:
                score = max(10, score - 5)
                feedback.append("😄 Tip: You packed treats or games! Fun for the bus ride, but they won't stop air pollution!")

            state["backpack_score"] = score
            if score >= 75:
                state["badges_unlocked"].add("Safety Pioneer")
                st.balloons()

            st.markdown(
                f"""
                <div style="background: {'#ECFDF5' if score >= 75 else '#FFFBEB'}; border: 1px solid {'#10B981' if score >= 75 else '#F59E0B'}; border-radius: 14px; padding: 18px 20px; margin-top: 14px;">
                    <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: {'#059669' if score >= 75 else '#B45309'}; margin-bottom: 6px;">
                        {'🎉 Backpack Score: ' + str(score) + '/100 — Safety Pioneer Certified!' if score >= 75 else '⏳ Backpack Score: ' + str(score) + '/100 — Almost Prepared!'}
                    </div>
                    <ul style="font-family: var(--font-sans); font-size: 0.85rem; color: #1F344C; margin: 0 0 0 16px; padding: 0; line-height: 1.5;">
                        {''.join(f'<li>{f}</li>' for f in feedback)}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

    # -------------------------------------------------------------------------
    # GAME 2: CLEAN AIR DETECTIVE MYSTERY
    # -------------------------------------------------------------------------
    with tab_detective:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 20px; margin-bottom: 16px;">
                <div style="display: flex; align-items: flex-start; gap: 14px;">
                    <span style="font-size: 2rem;">🕵️</span>
                    <div>
                        <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; margin-bottom: 4px;">
                            Episode 1: The Mystery of the 4:00 PM Haze Monster
                        </div>
                        <div style="font-family: var(--font-sans); font-size: 0.86rem; color: #5A6E85; line-height: 1.5;">
                            Pip the Sprout looked out the window in {city_name} at 4:00 PM and noticed the sky looked slightly hazy and smelled like warm asphalt. Aero the Cloud floated down with a magnifying glass. <em>"Detective, we need your help to find the culprit!"</em>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.9rem; color: #1F344C;'>Inspect the Clues:</strong>", unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)

        with col_c1:
            st.markdown(
                """
                <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 12px; padding: 14px;">
                    <div style="font-family: var(--font-heading); font-size: 0.85rem; font-weight: 800; color: #FF6845; margin-bottom: 4px;">🔍 CLUE #1: The Roadway</div>
                    <div style="font-family: var(--font-sans); font-size: 0.8rem; color: #5A6E85;">
                        Hundreds of cars, school buses, and delivery vans are stopped at traffic lights with their exhaust engines running.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_c2:
            st.markdown(
                """
                <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 12px; padding: 14px;">
                    <div style="font-family: var(--font-heading); font-size: 0.85rem; font-weight: 800; color: #0284C7; margin-bottom: 4px;">🔍 CLUE #2: The Anemometer</div>
                    <div style="font-family: var(--font-sans); font-size: 0.8rem; color: #5A6E85;">
                        The wind dial reads 1 km/h. Tree leaves are completely motionless—there is no fresh breeze blowing across the street.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_c3:
            st.markdown(
                """
                <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 12px; padding: 14px;">
                    <div style="font-family: var(--font-heading); font-size: 0.85rem; font-weight: 800; color: #F59E0B; margin-bottom: 4px;">🔍 CLUE #3: The Hot Sun</div>
                    <div style="font-family: var(--font-sans); font-size: 0.8rem; color: #5A6E85;">
                        The hot afternoon sun is beaming down intensely on the asphalt road, cooking the car exhaust fumes.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        detective_choice = st.radio(
            "Who is the main culprit causing the 4:00 PM haze?",
            options=[
                "Option A: The city birds were flapping their wings too fast",
                "Option B: Evening school/office traffic rush + calm wind trapping car exhaust",
                "Option C: Someone left their bedroom refrigerator door open",
                "Option D: The neighborhood trees were coughing"
            ],
            key="detective_choice"
        )

        if st.button("🔎 Submit Detective Deduction", key="btn_submit_detective", use_container_width=True):
            if "Option B" in detective_choice:
                state["detective_solved"] = True
                state["badges_unlocked"].add("Master Air Detective")
                st.balloons()
                st.markdown(
                    """
                    <div style="background: #ECFDF5; border: 1px solid #10B981; border-radius: 14px; padding: 18px 20px; margin-top: 14px;">
                        <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #059669; margin-bottom: 6px;">
                            🎉 Case Solved, Detective! You earned the 'Master Air Detective' Badge!
                        </div>
                        <div style="font-family: var(--font-sans); font-size: 0.86rem; color: #1F344C; line-height: 1.5;">
                            Brilliant deduction! When hundreds of vehicles idle during rush hour while the wind is completely still, warm car fumes have nowhere to blow away. The afternoon sun then turns those fumes into ground-level smog!
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="background: #FEF2F2; border: 1px solid #EF4444; border-radius: 14px; padding: 16px 20px; margin-top: 14px;">
                        <div style="font-family: var(--font-heading); font-size: 1rem; font-weight: 800; color: #B91C1C; margin-bottom: 4px;">
                            Not quite, detective! Look closely at Clues #1 and #2.
                        </div>
                        <div style="font-family: var(--font-sans); font-size: 0.84rem; color: #7F1D1D;">
                            Hint: What produces lots of exhaust pipes around 4:00 PM when parents pick kids up from school? Try again!
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # -------------------------------------------------------------------------
    # GAME 3: THE GREAT ECO & CLEAN AIR TRIVIA QUIZ
    # -------------------------------------------------------------------------
    with tab_quiz:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 20px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.8rem;">🌱</span>
                    <div>
                        <div style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 800; color: #1F344C;">
                            The Great Eco & Clean Air Family Quiz
                        </div>
                        <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85;">
                            5 quick questions to test your clean air wisdom! Can you score 5/5 and earn the Eco Champion Medal?
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Question 1
        st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.9rem; color: #1F344C;'>1. Who are Earth's giant living air-scrubber superheroes?</strong>", unsafe_allow_html=True)
        q1 = st.radio("Q1", ["Electric toaster ovens", "Trees and green houseplants", "Airplanes"], key="quiz_q1", label_visibility="collapsed")

        # Question 2
        st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.9rem; color: #1F344C;'>2. How small is a PM₂.₅ micro-dust particle compared to a strand of hair?</strong>", unsafe_allow_html=True)
        q2 = st.radio("Q2", ["About 30 times smaller than a hair strand", "Bigger than a basketball", "The exact size of a banana"], key="quiz_q2", label_visibility="collapsed")

        # Question 3
        st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.9rem; color: #1F344C;'>3. What is the best thing to drink when you spend time outdoors near dusty roads?</strong>", unsafe_allow_html=True)
        q3 = st.radio("Q3", ["Lots of clean water (flushes dust down throat safely)", "Sugary soda", "Ice cream milkshake"], key="quiz_q3", label_visibility="collapsed")

        # Question 4
        st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.9rem; color: #1F344C;'>4. What should you do if dust blows into your eyes and makes them itch?</strong>", unsafe_allow_html=True)
        q4 = st.radio("Q4", ["Rub them very hard with dirty fingers", "Splash cool water and place a cool damp cloth over eyes (never rub!)", "Stare directly into the sun"], key="quiz_q4", label_visibility="collapsed")

        # Question 5
        st.markdown("<strong style='font-family: var(--font-heading); font-size: 0.9rem; color: #1F344C;'>5. Where in your neighborhood is the air naturally the cleanest?</strong>", unsafe_allow_html=True)
        q5 = st.radio("Q5", ["Grassy municipal parks and tree-lined avenues", "Right next to an idling bus exhaust pipe", "Inside a dusty basement"], key="quiz_q5", label_visibility="collapsed")

        if st.button("🌱 Calculate My Eco Quiz Score!", key="btn_eval_quiz", use_container_width=True):
            correct_count = 0
            if "Trees and green houseplants" in q1:
                correct_count += 1
            if "30 times smaller" in q2:
                correct_count += 1
            if "Lots of clean water" in q3:
                correct_count += 1
            if "Splash cool water" in q4:
                correct_count += 1
            if "Grassy municipal parks" in q5:
                correct_count += 1

            state["quiz_score"] = correct_count
            if correct_count >= 4:
                state["badges_unlocked"].add("Eco Champion")
                st.balloons()

            st.markdown(
                f"""
                <div style="background: {'#ECFDF5' if correct_count >= 4 else '#FFFBEB'}; border: 1px solid {'#10B981' if correct_count >= 4 else '#F59E0B'}; border-radius: 14px; padding: 18px 20px; margin-top: 14px;">
                    <div style="font-family: var(--font-heading); font-size: 1.2rem; font-weight: 800; color: {'#059669' if correct_count >= 4 else '#B45309'}; margin-bottom: 4px;">
                        {'🏆 Score: ' + str(correct_count) + ' / 5 — Eco Champion Unlocked!' if correct_count >= 4 else '✨ Score: ' + str(correct_count) + ' / 5 — Good Effort!'}
                    </div>
                    <div style="font-family: var(--font-sans); font-size: 0.86rem; color: #1F344C;">
                        {'You are an absolute Clean Air Genius! Trees clean our air, water flushes dust, and cool cloths soothe our eyes!' if correct_count >= 4 else 'Review the questions and try again to score 5/5!'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # -------------------------------------------------------------------------
    # GAME 4: GUESS THE FRESHEST AIR WINDOW
    # -------------------------------------------------------------------------
    with tab_guess:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 16px; padding: 20px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.8rem;">💨</span>
                    <div>
                        <div style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 800; color: #1F344C;">
                            Predictive Intuition: Guess Today's Freshest Hour
                        </div>
                        <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85;">
                            Can your weather instinct beat AirGuard's machine learning model for {city_name}?
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        hours_labels = [f"{h:02d}:00 {'AM' if h < 12 else 'PM'}" for h in range(24)]
        user_guess = st.select_slider(
            "Slide to the hour you think has the cleanest, purest outdoor air today:",
            options=hours_labels,
            value="06:00 AM",
            key="slider_hour_guess"
        )

        if st.button("🎯 Reveal AI Model Verdict!", key="btn_eval_hour", use_container_width=True):
            state["hour_guess_made"] = True
            state["badges_unlocked"].add("Clean Air Futurist")
            st.markdown(
                f"""
                <div style="background: #F0FDF4; border: 1px solid #22C55E; border-radius: 14px; padding: 18px 20px; margin-top: 14px;">
                    <div style="font-family: var(--font-heading); font-size: 1.05rem; font-weight: 800; color: #15803D; margin-bottom: 6px;">
                        🎯 Your Guess: {user_guess} vs AI Model Forecast: {best_time}
                    </div>
                    <div style="font-family: var(--font-sans); font-size: 0.85rem; color: #1F344C; line-height: 1.5;">
                        AirGuard's machine learning forecast predicts that the purest air window in {city_name} is around <strong>{best_time}</strong> when atmospheric dispersion is highest. You earned the <strong>Clean Air Futurist</strong> badge!
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # -------------------------------------------------------------------------
    # TAB 5: TROPHY CASE & BADGES
    # -------------------------------------------------------------------------
    with tab_trophy:
        st.markdown("<h3 style='font-family: var(--font-heading); font-size: 1.2rem; font-weight: 800; color: #1F344C; margin: 12px 0 14px 0;'>🏆 Your 3D Clean Air Achievement Showcase</h3>", unsafe_allow_html=True)
        
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)

        badges_meta = [
            ("Safety Pioneer", "🎒", "Safety Pioneer", "Pack your backpack score to 75%+ in the Backpack Game.", "mascot_caution_mask.jpg"),
            ("Master Air Detective", "🕵️", "Master Detective", "Solve Episode 1 of the Haze Monster mystery.", "mascot_clean_air.jpg"),
            ("Eco Champion", "🌱", "Eco Champion Medal", "Score 4/5 or 5/5 on the Great Eco & Air Quiz.", "mascot_indoor_sanctuary.jpg"),
            ("Clean Air Futurist", "💨", "Futurist Explorer", "Test your weather intuition in the Freshest Hour game.", "mascot_outdoor_runner.jpg")
        ]

        cols = [col_t1, col_t2, col_t3, col_t4]
        for idx, (b_id, emoji_icon, b_title, b_desc, mascot_file) in enumerate(badges_meta):
            is_unlocked = b_id in state["badges_unlocked"]
            m_b64 = get_mascot_base64(mascot_file)
            img_tag = f"""<img src="{m_b64}" style="width: 56px; height: 56px; border-radius: 14px; object-fit: cover; margin-bottom: 8px; {'filter: grayscale(100%) opacity(40%);' if not is_unlocked else 'box-shadow: 0 6px 14px rgba(16, 185, 129, 0.25);'}" />""" if m_b64 else f"<div style='font-size: 2.2rem; margin-bottom: 8px;'>{emoji_icon}</div>"

            with cols[idx]:
                st.markdown(
                    f"""
                    <div style="background: {'#FFFFFF' if is_unlocked else '#F8FAFC'}; border: 2px solid {'#10B981' if is_unlocked else '#E2E8F0'}; border-radius: 16px; padding: 18px 14px; text-align: center; height: 100%; box-shadow: {'0 6px 16px rgba(16, 185, 129, 0.12)' if is_unlocked else 'none'};">
                        {img_tag}
                        <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 800; color: {'#1F344C' if is_unlocked else '#94A3B8'}; margin-bottom: 4px;">
                            {b_title}
                        </div>
                        <div style="font-family: var(--font-sans); font-size: 0.76rem; color: #5A6E85; margin-bottom: 10px; line-height: 1.35;">
                            {b_desc}
                        </div>
                        <span style="font-family: var(--font-mono); font-size: 0.68rem; font-weight: 700; padding: 3px 10px; border-radius: 9999px; background: {'#ECFDF5' if is_unlocked else '#E2E8F0'}; color: {'#059669' if is_unlocked else '#64748B'};">
                            {'UNLOCKED ✨' if is_unlocked else 'LOCKED 🔒'}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
