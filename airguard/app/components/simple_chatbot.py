"""
Child-Friendly & Non-Tech AI Chatbot Component: 'Aero — Your Clean Air Buddy ☁️'
Exclusively for Simple Mode in AirGuard.
Features:
- Friendly, encouraging, short, easy-to-understand answers (2-3 sentences max).
- Storytelling analogies (dust monsters, sunshine smog, superhero air shield, tree scrubbers).
- Real-time city telemetry awareness (current PM2.5, AQI, weather, user profile).
- Pre-populated quick-tap prompt buttons for kids and parents.
- Full interactive conversation history stored in st.session_state.
"""

from __future__ import annotations

import re
from typing import Dict, Any, List, Optional
import streamlit as st

from app.components.simple_cards import get_mascot_base64
from app.components.design_system import safe_markdown


# Default curated child/family friendly prompt questions
CURATED_PROMPTS = [
    "⚽ Can I play soccer outside right now?",
    "🎒 What should I pack in my schoolbag today?",
    "🤧 My throat tickles and eyes burn — what should I do?",
    "🐕 Is it safe to walk my dog outside?",
    "😷 Do I need to wear a mask today?",
    "🌱 How do trees and houseplants clean the air?",
    "📖 Tell me a fun bedtime story about clean air!",
    "🧐 What is PM2.5 in simple words?"
]


def generate_aero_response(
    user_query: str,
    city_name: str,
    pm25: float,
    aqi: int,
    temp: float,
    wind: float,
    humidity: float,
    user_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Generates a child-friendly, storytelling response from Aero the Cloud.
    Maintains zero technical jargon, 2-3 short sentences, warm analogies,
    actionable tips, and tailored advice for ANY user query.
    Returns dict with:
      - 'answer': short, warm explanation (2-3 sentences)
      - 'tip': short actionable takeaway for kids/parents
      - 'mascot': mascot filename to display
    """
    q = (user_query or "").lower().strip()
    prof = user_profile or {}
    sensitivity = prof.get("health_sensitivity", "none")
    age = prof.get("age_group", "adult")
    is_sensitive = sensitivity != "none" or age in ["child", "senior"]

    # 1. GREETINGS, IDENTITY & CAPABILITY
    if any(k in q for k in ["hi", "hello", "hey", "who are you", "what can you do", "help me", "good morning", "good evening"]):
        return {
            "answer": (
                f"Hello there! I'm Aero, your friendly Clean Air Buddy ☁️✨! "
                f"Right now in {city_name}, the air is {temp:.0f}°C with a dust level of {pm25:.0f} specks. "
                f"I'm here to tell you when it's safe to play, what to pack in your bag, or how to soothe any coughs!"
            ),
            "tip": "Tip: Ask me 'Can I play outside?', 'What to pack?', or 'Why do my eyes sting?'!",
            "mascot": "mascot_clean_air.jpg"
        }

    # 2. SENSITIVE GROUPS: BABIES, INFANTS, PREGNANCY, GRANDPARENTS, ASTHMA
    if any(k in q for k in ["baby", "infant", "newborn", "toddler", "stroller", "pregnant", "pregnancy", "grandma", "grandpa", "elderly", "senior", "asthma", "inhaler", "wheez", "allergy"]):
        if pm25 > 35:
            return {
                "answer": (
                    f"Extra gentle care is needed for sensitive lungs in {city_name} today! "
                    f"Babies, grandparents, and friends with asthma breathe more dust per breath, so it's safest to stay in a cozy indoor room with an air purifier running. "
                    f"Keep inhalers and warm drinks close by!"
                ),
                "tip": "Tip: Keep stroller covers on if you must take a baby outside near busy roads.",
                "mascot": "mascot_caution_mask.jpg"
            }
        else:
            return {
                "answer": (
                    f"Good news for sensitive lungs in {city_name}! The air is peaceful and mild right now ({pm25:.0f} specks). "
                    f"A gentle 20-minute walk in a quiet tree-filled park is wonderful for health—just stay away from smoky car tailpipes!"
                ),
                "tip": "Tip: Bring your water bottle and take gentle strolls on grassy paths.",
                "mascot": "mascot_clean_air.jpg"
            }

    # 3. OUTDOOR ACTIVITIES, RUNNING, CYCLING, SPORTS & RECESS
    if any(k in q for k in ["play", "soccer", "football", "cricket", "run", "jog", "cycle", "bike", "outside", "playground", "park", "recess", "walk", "stroll", "gym", "exercise"]):
        if pm25 <= 15:
            return {
                "answer": f"Hooray! The air in {city_name} is squeaky clean and fresh right now (only {pm25:.0f} dust specks)! You can run, kick the soccer ball, and play at the playground as much as you like!",
                "tip": "Tip: Take a big gulp of fresh air and have fun outdoors today!",
                "mascot": "mascot_outdoor_runner.jpg"
            }
        elif pm25 <= 35:
            if is_sensitive:
                return {
                    "answer": f"You can play outside in {city_name}, but let's take it a little gentler! Since your lungs are a bit sensitive, choose fun games that don't make you breathe super hard, and drink plenty of water.",
                    "tip": "Tip: Green grassy parks have much fresher air than streets with cars!",
                    "mascot": "mascot_clean_air.jpg"
                }
            else:
                return {
                    "answer": f"Yes, you can go outside and play in {city_name}! The air is mostly nice and clear. Just remember to bring your water bottle to keep your throat happy.",
                    "tip": "Tip: Stick to parks and tree-lined paths away from busy roads.",
                    "mascot": "mascot_outdoor_runner.jpg"
                }
        elif pm25 <= 75:
            return {
                "answer": f"Caution, little explorer! The invisible dust monsters in {city_name} are floating around in higher numbers ({pm25:.0f} specks) right now. It's best to play outdoor games for just 20–30 minutes, or enjoy fun indoor Lego and board games!",
                "tip": "Tip: If you do go out, wear your cool superhero mask to block the dust!",
                "mascot": "mascot_caution_mask.jpg"
            }
        else:
            return {
                "answer": f"Uh-oh! The air in {city_name} is very dusty and unhappy today ({pm25:.0f} dust specks). The best superhero move right now is staying inside your cozy indoor fort where the air is safe and pure!",
                "tip": "Tip: Keep windows closed and build a fun blanket fortress indoors!",
                "mascot": "mascot_indoor_sanctuary.jpg"
            }

    # 3. WHAT TO PACK / SCHOOLBAG / BACKPACK / GEAR
    if any(k in q for k in ["pack", "bag", "schoolbag", "backpack", "bring", "carry", "take with", "bottle", "gear", "supplies"]):
        pack_items = ["a tall bottle of fresh water", "sunglasses to block ground dust"]
        if pm25 > 25:
            pack_items.append("a snug clean-air mask (like an N95 or soft kid-shield)")
        if is_sensitive:
            pack_items.append("your pocket rescue inhaler or allergy drops")
        pack_items.append("a clean handkerchief or wet wipe")

        items_str = ", ".join(pack_items)
        return {
            "answer": f"Ready for an outdoor adventure in {city_name}? Make sure your backpack has: {items_str}! Water keeps your throat moist, and sunglasses stop dusty grit from blowing into your eyes.",
            "tip": "Aero's Rule: Water flushes dust specks down your tummy where they can't tickle your lungs!",
            "mascot": "mascot_clean_air.jpg"
        }

    # 4. SYMPTOMS & FIRST AID REMEDIES (THROAT, EYES, COUGH, SNEEZE)
    if any(k in q for k in ["throat", "cough", "itch", "scratch", "burn", "eye", "sting", "watery", "sneeze", "headache", "chest", "breath", "sick", "hurt"]):
        return {
            "answer": (
                "Oh no, let's soothe those tickles right away! First, splash cool water on your face and place a clean, cool damp washcloth gently over your eyes—never rub them! "
                "Next, sip warm water with a spoonful of sweet honey to coat your throat like a warm blanket, and rest inside."
            ),
            "tip": "Aero's Comfort Remedy: Breathe warm steam from a warm mug or shower, and rest in your cozy room with windows closed.",
            "mascot": "mascot_indoor_sanctuary.jpg"
        }

    # 5. MASKS & FACE SHIELDS
    if any(k in q for k in ["mask", "n95", "cloth", "surgical", "face cover", "shield", "wear"]):
        if pm25 > 50:
            return {
                "answer": f"Yes! Wearing a snug mask (like an N95 or a soft filtered kid mask) is like giving your nose a magical shield. It traps 95% of invisible dust ninjas before they can tickle your breathing pipes!",
                "tip": "Tip: Make sure the mask fits snugly over both your nose and chin with no big gaps.",
                "mascot": "mascot_caution_mask.jpg"
            }
        elif pm25 > 25:
            return {
                "answer": f"The air in {city_name} is okay, but if you're running fast near busy roads or feeling sensitive, popping on your light mask is a smart superhero move!",
                "tip": "Tip: Keep a clean spare mask zipped inside your schoolbag.",
                "mascot": "mascot_clean_air.jpg"
            }
        else:
            return {
                "answer": f"Good news! The air in {city_name} is sparkling clean ({pm25:.0f} specks), so you don't need a mask right now. Breathe deep and enjoy the fresh breeze!",
                "tip": "Tip: Still keep one in your backpack just in case you pass smoky traffic later.",
                "mascot": "mascot_clean_air.jpg"
            }

    # 7. INDOOR AIR SANCTUARY, BEDROOM & WINDOWS
    if any(k in q for k in ["indoor", "house", "home", "room", "window", "purifier", "hepa", "bedroom", "close window", "open window", "ac", "fan", "filter"]):
        if pm25 > 45:
            return {
                "answer": (
                    f"To make your home a clean air fortress in {city_name}, keep doors and windows shut tight to block outside dust. "
                    f"Turn on your bedroom air cleaner or HEPA filter, and avoid burning candles, incense, or frying food with doors open!"
                ),
                "tip": "Tip: Air out your room only in the bright afternoon (1:00–3:00 PM) when the sun has warmed up the breeze.",
                "mascot": "mascot_indoor_sanctuary.jpg"
            }
        else:
            return {
                "answer": (
                    f"The outside air in {city_name} is fresh right now ({pm25:.0f} specks)! "
                    f"Open up your windows for 30 minutes to welcome in cool fresh oxygen and flush out stale indoor air!"
                ),
                "tip": "Tip: Cross-ventilation (opening opposite windows) cleans room air in just 15 minutes.",
                "mascot": "mascot_clean_air.jpg"
            }

    # 8. NATURE, TREES & HOUSEPLANTS
    if any(k in q for k in ["tree", "plant", "nature", "garden", "leaf", "snake plant", "spider plant", "areca", "clean air", "help the air"]):
        return {
            "answer": "Trees and houseplants are earth's giant green air scrubbers! While we breathe in oxygen and breathe out carbon, plants do the magical opposite—their leaves catch dust and drink in pollutants, breathing out delicious fresh oxygen for us all day long!",
            "tip": "Aero's Eco Mission: Adopt a Snake Plant or Spider Plant in your bedroom—they clean the air while you sleep!",
            "mascot": "mascot_clean_air.jpg"
        }

    # 9. PETS & ANIMALS
    if any(k in q for k in ["dog", "cat", "pet", "puppy", "kitten", "walk dog"]):
        if pm25 > 55:
            return {
                "answer": f"Furry friends breathe much closer to the ground where dust settles! Since {city_name}'s air is dusty ({pm25:.0f} specks), keep doggy potty walks short (5-10 minutes) and wipe their paws with a damp cloth when you get back inside.",
                "tip": "Tip: Play tug-of-war or ball rolling in the living room today instead of long runs!",
                "mascot": "mascot_caution_mask.jpg"
            }
        else:
            return {
                "answer": f"Your furry buddy will love a walk today! The air in {city_name} is safe and comfortable. Head to a grassy dog park or tree-lined lawn for sniffing fun!",
                "tip": "Tip: Bring a collapsible water dish so your pup stays hydrated too!",
                "mascot": "mascot_clean_air.jpg"
            }

    # 10. WEATHER, RAIN, FOG & SMOG
    if any(k in q for k in ["weather", "rain", "fog", "smog", "sun", "wind", "cold", "hot", "storm"]):
        if "rain" in q:
            return {
                "answer": f"Rain is nature's giant power shower! When water droplets tumble from the sky over {city_name}, they grab dust specks and pull them straight down to the soil, leaving the sky sparkling clean!",
                "tip": "Tip: The air immediately after a nice rain shower is the freshest air of the entire week!",
                "mascot": "mascot_clean_air.jpg"
            }
        else:
            return {
                "answer": (
                    f"In {city_name} right now, the temperature is {temp:.0f}°C with a wind speed of {wind:.0f} km/h and humidity around {humidity:.0f}%. "
                    f"Early morning chilly air often traps dust near the ground like a cold lid, but afternoon sunshine helps float it away!"
                ),
                "tip": "Tip: The sunniest hours of the afternoon are usually the cleanest hours to step outside.",
                "mascot": "mascot_clean_air.jpg"
            }

    # 11. FOOD & HEALTHY LUNGS
    if any(k in q for k in ["food", "drink", "eat", "turmeric", "honey", "orange", "carrot", "nutrition", "milk", "water"]):
        return {
            "answer": (
                "Eating colorful foods gives your lungs superhero shields! "
                "Sweet orange carrots and citrus fruits like oranges have Vitamin A and C that repair breathing passages, while warm golden turmeric milk soothes irritation like a warm blanket!"
            ),
            "tip": "Aero's Power Snack: Drink 4-6 glasses of fresh water daily to wash away throat dust specks.",
            "mascot": "mascot_clean_air.jpg"
        }

    # 12. NEWS & TODAY'S ALERTS
    if any(k in q for k in ["news", "headline", "alert", "directive", "bulletin", "today", "report", "government", "rules"]):
        return {
            "answer": (
                f"Today in clean air news for {city_name}: Environmental teams and doctors are watching our breezes closely! "
                f"Green canopy projects around lakes and parks are actively soaking up dust, and metro transit is running extra trips. "
                f"Check out our full Air Quality Newsroom on Page 7 for all the latest stories from verified clean air protectors!"
            ),
            "tip": "Tip: You can read child-safe news summaries updated every 6 hours in our News tab!",
            "mascot": "mascot_clean_air.jpg"
        }

    # 13. BEDTIME STORY / FUN STORY
    if any(k in q for k in ["story", "bedtime", "tale", "adventure", "fairy"]):
        return {
            "answer": f"Once upon a time in {city_name}, a cheerful cloud named Aero floated over the city with a tiny green sprout friend named Pip! Whenever smoky traffic tried to rise into the sky, Pip would wiggle his leaves and call upon the Gentle Mountain Breeze. Together, they puffed away the gray dust, turning the sky into a shimmering ocean of clean blue air where children could play safely under the stars!",
            "tip": "The Moral: When we plant trees and take care of the breeze, the sky smiles right back at us!",
            "mascot": "mascot_clean_air.jpg"
        }

    # 14. PM2.5 & AQI EXPLANATION
    if any(k in q for k in ["pm2.5", "pm25", "aqi", "particle", "micro", "what is", "mean", "dust speck"]):
        return {
            "answer": f"Imagine taking a single strand of your hair and slicing it into 30 tiny microscopic pieces—that's how tiny PM2.5 dust specks are! Right now in {city_name}, there are {pm25:.0f} of these little specks per breath. When the number is low, your lungs feel happy and breezy!",
            "tip": "Easy Rule: Under 30 is Clean & Green, 30-60 is Caution Yellow, and over 60 means Dust Alert!",
            "mascot": "mascot_clean_air.jpg"
        }

    # 15. GRATITUDE, GOODBYE & CLOSING
    if any(k in q for k in ["thank", "bye", "goodbye", "awesome", "great", "love", "good job", "cool"]):
        return {
            "answer": (
                f"You're so very welcome, friend! I love helping you and your family breathe happy in {city_name}. "
                f"Drink a nice sip of water, stay safe, and give your lungs a big superhero high-five! ☁️✨"
            ),
            "tip": "Tip: I'm always floating here on the bottom right if you need me again!",
            "mascot": "mascot_clean_air.jpg"
        }

    # 16. COMPREHENSIVE CONTEXTUAL SITUATIONAL FALLBACK
    return {
        "answer": (
            f"Hi friend! In {city_name} right now, the air is {temp:.0f}°C with a pleasant {wind:.0f} km/h breeze and a particle level of {pm25:.0f} (AQI {aqi}). "
            f"{'Conditions are nice and clear for outdoor fun!' if pm25 <= 35 else 'Take it gentle outside today and keep your water bottle handy!'} "
            f"I'm always right here to guide your outdoor adventures, bag packing, or home air fortress!"
        ),
        "tip": "Tip: You can tap any of the quick prompt buttons for instant advice on playing, packing, or masks!",
        "mascot": "mascot_clean_air.jpg"
    }


def render_aero_chatbot(
    city_name: str,
    pm25: float,
    aqi: int,
    temp: float,
    wind: float,
    humidity: float,
    user_profile: Optional[Dict[str, Any]] = None,
    container_key: str = "aero_chat"
) -> None:
    """
    Renders the child-friendly Aero AI Chatbot widget with speech bubbles,
    quick prompt pills, and interactive text input.
    """
    # Initialize session state chat history
    session_key = f"{container_key}_history"
    if session_key not in st.session_state:
        st.session_state[session_key] = [
            {
                "sender": "aero",
                "text": f"Hi there! I'm Aero, your Clean Air Buddy! ☁️✨ The air in {city_name} is currently {temp:.0f}°C with a dust level of {pm25:.0f}. Ask me anything about playing outside, what to pack, or how to stay safe!",
                "tip": "Tap any question below or type your own!",
                "mascot": "mascot_clean_air.jpg"
            }
        ]

    # Container Card with Soft Warm Glow
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #EBE6DF; border-top: 4px solid #FF6845; border-radius: 20px; padding: 22px 24px; margin-bottom: 24px; box-shadow: 0 6px 20px rgba(255, 104, 69, 0.06);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.8rem;">☁️</span>
                    <div>
                        <div style="font-family: var(--font-heading); font-size: 1.25rem; font-weight: 800; color: #1F344C; margin: 0; line-height: 1.2;">
                            Ask Aero — Your Clean Air Buddy
                        </div>
                        <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #5A6E85;">
                            Friendly, bite-sized answers for kids, parents, and everyday outdoor decisions.
                        </div>
                    </div>
                </div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 9999px; padding: 3px 12px;">
                    <span class="ensur-pulse-dot" style="width: 6px; height: 6px; background: #10B981;"></span>
                    <span style="font-family: var(--font-heading); font-size: 0.7rem; font-weight: 800; color: #059669; text-transform: uppercase;">
                        Aero is Listening & Ready!
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Quick Prompt Buttons Row
    st.markdown("<div style='font-family: var(--font-heading); font-size: 0.82rem; font-weight: 800; color: #1F344C; margin-bottom: 8px;'>💡 Quick Questions Kids & Parents Ask:</div>", unsafe_allow_html=True)
    
    # 2 rows of prompt buttons
    p_cols1 = st.columns(4)
    for idx, prompt_text in enumerate(CURATED_PROMPTS[:4]):
        with p_cols1[idx]:
            if st.button(prompt_text, key=f"btn_prompt_1_{idx}_{container_key}", use_container_width=True):
                # Trigger Aero response
                resp = generate_aero_response(
                    user_query=prompt_text,
                    city_name=city_name,
                    pm25=pm25,
                    aqi=aqi,
                    temp=temp,
                    wind=wind,
                    humidity=humidity,
                    user_profile=user_profile
                )
                st.session_state[session_key].append({"sender": "user", "text": prompt_text})
                st.session_state[session_key].append({
                    "sender": "aero",
                    "text": resp["answer"],
                    "tip": resp["tip"],
                    "mascot": resp["mascot"]
                })
                st.rerun()

    p_cols2 = st.columns(4)
    for idx, prompt_text in enumerate(CURATED_PROMPTS[4:]):
        with p_cols2[idx]:
            if st.button(prompt_text, key=f"btn_prompt_2_{idx}_{container_key}", use_container_width=True):
                resp = generate_aero_response(
                    user_query=prompt_text,
                    city_name=city_name,
                    pm25=pm25,
                    aqi=aqi,
                    temp=temp,
                    wind=wind,
                    humidity=humidity,
                    user_profile=user_profile
                )
                st.session_state[session_key].append({"sender": "user", "text": prompt_text})
                st.session_state[session_key].append({
                    "sender": "aero",
                    "text": resp["answer"],
                    "tip": resp["tip"],
                    "mascot": resp["mascot"]
                })
                st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. Render Chat History Stream
    chat_box = st.container(height=360, border=True)
    with chat_box:
        for msg in st.session_state[session_key]:
            if msg["sender"] == "user":
                safe_markdown(
                    f'<div style="display: flex; justify-content: flex-end; margin-bottom: 12px;"><div style="background: linear-gradient(135deg, #FF6845 0%, #FF8665 100%); color: #FFFFFF; padding: 10px 16px; border-radius: 18px 18px 4px 18px; max-width: 80%; font-family: var(--font-sans); font-size: 0.9rem; font-weight: 500; box-shadow: 0 4px 12px rgba(255, 104, 69, 0.2);">{msg["text"]}</div></div>'
                )
            else:
                mascot_file = msg.get("mascot", "mascot_clean_air.jpg")
                mascot_b64 = get_mascot_base64(mascot_file)
                mascot_img_html = f'<img src="{mascot_b64}" style="width: 44px; height: 44px; border-radius: 12px; object-fit: cover; border: 2px solid #FFFFFF; box-shadow: 0 4px 10px rgba(31, 52, 76, 0.1);" />' if mascot_b64 else '☁️'
                tip_box = f'<div style="background: #FAF6F1; border-left: 3px solid #FF6845; padding: 6px 12px; border-radius: 6px; margin-top: 8px; font-family: var(--font-sans); font-size: 0.78rem; color: #1F344C; font-weight: 600;">{msg.get("tip", "")}</div>' if msg.get("tip") else ""

                safe_markdown(
                    f'<div style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 14px;"><div style="flex: 0 0 44px;">{mascot_img_html}</div><div style="background: #FFFFFF; border: 1px solid #EBE6DF; padding: 12px 16px; border-radius: 4px 18px 18px 18px; max-width: 82%; font-family: var(--font-sans); font-size: 0.9rem; color: #1F344C; line-height: 1.45; box-shadow: 0 3px 10px rgba(31, 52, 76, 0.04);"><div style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #FF6845; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Aero the Clean Air Buddy</div><div>{msg["text"]}</div>{tip_box}</div></div>'
                )

    # 3. Interactive Question Input Box
    with st.form(key=f"aero_input_form_{container_key}", clear_on_submit=True):
        col_in, col_btn, col_clear = st.columns([3.8, 1.1, 0.9])
        with col_in:
            user_input = st.text_input(
                "Ask Aero anything about today's air, packing, or playing outside:",
                placeholder="Type here (e.g. 'Can my 6-year-old ride bike now?', 'What if my eyes hurt?')...",
                label_visibility="collapsed"
            )
        with col_btn:
            submitted = st.form_submit_button("Ask Aero ☁️", use_container_width=True)
        with col_clear:
            clear_clicked = st.form_submit_button("Clear 🔄", use_container_width=True)

        if clear_clicked:
            st.session_state[session_key] = [
                {
                    "sender": "aero",
                    "text": f"Fresh start! I'm ready for your questions about {city_name}'s air and outdoor safety! ☁️✨",
                    "tip": "Ask me anything or choose a question above!",
                    "mascot": "mascot_clean_air.jpg"
                }
            ]
            st.rerun()

        if submitted and user_input.strip():
            resp = generate_aero_response(
                user_query=user_input,
                city_name=city_name,
                pm25=pm25,
                aqi=aqi,
                temp=temp,
                wind=wind,
                humidity=humidity,
                user_profile=user_profile
            )
            st.session_state[session_key].append({"sender": "user", "text": user_input})
            st.session_state[session_key].append({
                "sender": "aero",
                "text": resp["answer"],
                "tip": resp["tip"],
                "mascot": resp["mascot"]
            })
            st.rerun()
