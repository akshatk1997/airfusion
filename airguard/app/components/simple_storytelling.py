"""
AirFusion Simple Mode Storytelling & Everyday Terminology Decoder Module.
Translates complex atmospheric physics, pulmonary medicine, and environmental science
into warm, engaging, illustrated stories and plain-English real-world analogies.
"""

from typing import Optional, Dict, Any, List
import streamlit as st
from app.components.design_system import safe_markdown
from app.components.simple_cards import get_mascot_base64


# ==============================================================================
# 1. THE 4-CHAPTER CLEAN AIR STORYBOOK (FAMILY & CHILD FRIENDLY)
# ==============================================================================

CLEAN_AIR_STORY_CHAPTERS = [
    {
        "id": "chapter_1_invisible_world",
        "number": "CHAPTER 1",
        "title": "The Invisible Kingdom: The Secret Life of Air Particles",
        "subtitle": "Why you cannot always trust your eyes alone to tell if air is safe to breathe.",
        "mascot": "mascot_clean_air.jpg",
        "hero_badge": "☁️ AERO'S DISCOVERY",
        "badge_color": "#10B981",
        "analogy": "A strand of your hair is like a giant redwood tree compared to PM2.5, which is like a tiny ladybug sitting on a leaf!",
        "story": """
Every single day, you and your family take about twenty thousand breaths. Most of the time, the air looks clear, bright, and invisible. But look closer! Suspended in that gentle breeze is a microscopic world bustling with invisible specks.

Some of these specks are natural and harmless—like plant pollen or droplets of morning dew. But other specks are born from car tailpipes, smoky factories, and cooking stoves. Scientists call the tiniest of these specks **PM2.5**. They are so unbelievably small that about thirty of them could fit across the width of a single hair on your head!

Because they are microscopic, your nose hairs cannot catch them. When you take a deep breath, these tiny travelers slip all the way down into your lungs and whisper into your bloodstream. That is why our friendly cloud scout, **Aero**, floats high above your city with laser eyes—so you never have to guess what is floating in your air!
        """,
        "takeaways": [
            "You cannot judge air pollution by clear blue skies alone; the most dangerous particles are invisible.",
            "PM2.5 particles are so tiny that thirty of them fit across one strand of human hair.",
            "Checking AirFusion before stepping outside tells you what your eyes cannot see."
        ],
        "voice_script": "Chapter 1: The Invisible Kingdom. Did you know you take about twenty thousand breaths every day? Even when the sky looks clear, millions of invisible microscopic particles are floating around. The tiniest particles are called PM 2.5, and thirty of them can fit across a single strand of your hair! That is why our scout Aero uses smart sensors to check the air for your family!"
    },
    {
        "id": "chapter_2_four_guardians",
        "number": "CHAPTER 2",
        "title": "Meet the Four Guardians: Aero, Flash, Nova & Haven",
        "subtitle": "How four friendly teammates turn complicated scientific numbers into easy everyday choices.",
        "mascot": "airfusion_3d_cartoon_panoramic.jpg",
        "hero_badge": "🛡️ THE AIRFUSION TEAM",
        "badge_color": "#FF6845",
        "analogy": "Think of the guardians like a weather squad for your lungs: a scout, a runner, a shield, and a cozy fort!",
        "story": """
When environmental scientists look at air quality, they see complicated chemical formulas like micrograms per cubic meter and parts per billion. That can sound like another language! That is why AirFusion created the **Four Clean Air Fusionians** to translate the science into simple teamwork:

• **Aero the Cloud Scout**: Floating high in the sky, Aero sniffs the breeze 24/7. When the air is pure, Aero glows with green sparkles. When smoke drifts in, Aero sounds a gentle heads-up so you know what is coming.

• **Flash the Safe Window Navigator**: Flash loves to run, jump, and play outside! Flash checks the hourly air forecast to find the golden sunshine window when traffic smoke has blown away, telling you: "Run now! The track is wide open!"

• **Nova the Protective Shield**: Nova cares deeply for sensitive lungs, little children, and grandmas. When pollution spikes, Nova holds up a glowing shield and reminds you to wear a cozy N95 mask so your airways stay safe.

• **Haven the Sanctuary Dome**: Haven watches over your home and school. When outside air gets dusty, Haven whispers: "Close the windows and turn on your air filter! Your home is a peaceful, clean air fortress!"
        """,
        "takeaways": [
            "Aero scouts the invisible air across rooftop sensors.",
            "Flash finds the best hours of the day for sports, jogs, and park visits.",
            "Nova protects children, elderly family members, and sensitive asthma lungs.",
            "Haven keeps your indoor bedroom and living room 99.4% clean and purified."
        ],
        "voice_script": "Chapter 2: Meet the Four Guardians. Science can sound tricky with words like micrograms, so our four guardians make it easy! Aero scouts the sky. Flash finds the cleanest hours to play outside. Nova gives personalized mask advice for sensitive lungs. And Haven keeps your indoor home air pure and safe!"
    },
    {
        "id": "chapter_3_secret_rhythm",
        "number": "CHAPTER 3",
        "title": "The Magic Sun & The Pot Lid: How Weather Changes Air",
        "subtitle": "Why morning air is often very different from afternoon air, and how the sky breathes.",
        "mascot": "news_satellite_atmosphere.jpg",
        "hero_badge": "🌤️ ATMOSPHERIC MYSTERY",
        "badge_color": "#0284C7",
        "analogy": "Imagine boiling soup with a glass lid on top. Chilly winter mornings put a cold lid on our city, trapping smoke down low until the sunshine lifts the lid!",
        "story": """
Have you ever wondered why the air sometimes smells smoky at breakfast time, but smells fresh and breezy by lunchtime? The secret lies in how the sky breathes!

During cold winter nights, the ground cools off very quickly. A layer of cold air gets trapped right beneath a blanket of warmer air up above. Scientists call this a **Thermal Inversion**, but you can think of it like an **invisible glass pot lid** placed over your whole town! 

Because the cold air cannot rise, all the morning car exhaust, truck fumes, and chimney smoke get trapped down on street level where we walk and play. But then, something wonderful happens: the morning sun rises! As golden sunlight warms up the ground, the warm air begins to float upward, breaking the pot lid and opening the sky! By 10:00 AM, fresh winds sweep in and flush the dirty air away like clean water down a stream.

That is why Flash often advises waiting until mid-morning before going on vigorous runs in winter!
        """,
        "takeaways": [
            "Cold winter mornings trap vehicle exhaust close to the ground like a lid on a pot.",
            "Solar heating after 9:30 AM warms the ground, breaking the lid and blowing smoke away.",
            "Planning your outdoor workouts after mid-morning protects your lungs from stagnant dawn smog."
        ],
        "voice_script": "Chapter 3: The Magic Sun and the Pot Lid. Ever wonder why winter mornings feel smokier than afternoons? On chilly mornings, cold air acts like an invisible pot lid trapping car exhaust on street level! But once the warm sun rises after 9 AM, it lifts the lid and allows clean breezes to blow the smoke away! That is the secret rhythm of the sky!"
    },
    {
        "id": "chapter_4_family_action",
        "number": "CHAPTER 4",
        "title": "A Day in the Life: Simple Habits for Clean Breathing",
        "subtitle": "Four easy, stress-free decisions every family can make every single day.",
        "mascot": "real_family_outdoor_walk.jpg",
        "hero_badge": "🏡 EVERYDAY HABITS",
        "badge_color": "#8B5CF6",
        "analogy": "Taking care of your air is just like checking if you need an umbrella before leaving the house!",
        "story": """
Living with clean air does not mean staying locked inside or being scared of the outdoors. It is simply about knowing the smart moments to enjoy the fresh breeze and the right moments to take quick, easy precautions:

1. **The Morning Air Check**: Before tying your shoes or sending kids to school, open AirFusion on your phone for five seconds. Check the big smiley color badge: Green means go wild! Orange or Red means take your mask along!

2. **The Window Rhythm**: In the afternoon when the sun is bright and breezes are blowing, open your windows on opposite sides of the house to let fresh oxygen sweep through. Close windows during rush-hour traffic when cars are honking outside.

3. **The Leafy Route**: When walking to the market or riding bicycles, take the scenic tree-lined side streets and public parks. Big green trees catch dust on their leaves like nature's giant vacuum cleaner!

4. **The Bedroom Sanctuary**: Keep plants like Snake Plants or Areca Palms in your bedroom, and run a quiet HEPA purifier while you sleep. Your lungs work hard all day; night is when they repair and recharge in pure, clean air!
        """,
        "takeaways": [
            "Check AirFusion for 5 seconds every morning, just like checking the weather for rain.",
            "Open windows for cross-ventilation during sunny afternoon dispersion hours.",
            "Walk along tree-lined park paths instead of busy highway traffic corridors.",
            "Sleep in a clean bedroom sanctuary with good indoor air filtration."
        ],
        "voice_script": "Chapter 4: Simple Habits for Clean Breathing. Keeping your family healthy is as easy as checking for rain! Check AirFusion every morning. Open windows when breezes are fresh. Walk through green tree lined parks. And sleep peacefully in a clean indoor sanctuary! Together, we protect every breath you take!"
    }
]


# ==============================================================================
# 2. THE EVERYDAY AIR DECODER (PLAIN-ENGLISH TERMINOLOGY CATALOG)
# ==============================================================================

EVERYDAY_TERMS_CATALOG = [
    {
        "term": "PM₂.₅",
        "technical_name": "Particulate Matter ≤ 2.5 Micrometers",
        "plain_name": "Microscopic Soot & Dust Specks",
        "category": "pollutants",
        "category_label": "🧪 The Pollutants",
        "badge_color": "#EF4444",
        "icon": "🔬",
        "analogy": "Imagine a single strand of human hair. You could line up 30 PM₂.₅ particles across its tiny thickness!",
        "what_it_is": "Microscopic solid bits and liquid droplets floating in the air, created by vehicle exhaust, power plants, burning trash, and wood smoke.",
        "why_it_matters": "Because they are microscopic, they slip past your nose hairs, travel deep into your lung air sacs (alveoli), and can enter your bloodstream, causing tiredness, coughing, or heart strain.",
        "action_rule": "When PM₂.₅ is higher than 35 µg/m³, wear a snug N95 mask outdoors and run your indoor air purifier on high."
    },
    {
        "term": "PM₁₀",
        "technical_name": "Particulate Matter ≤ 10 Micrometers",
        "plain_name": "Visible Road Dust, Pollen & Sand",
        "category": "pollutants",
        "category_label": "🧪 The Pollutants",
        "badge_color": "#F59E0B",
        "icon": "💨",
        "analogy": "Like fine beach sand or flour dust flying into the air when you clap your hands together.",
        "what_it_is": "Coarser dust particles kicked up by car tires on dry roads, construction sites, cement factories, agricultural plowing, and flower pollen.",
        "why_it_matters": "These particles get caught in your nose, throat, and upper airways, causing sneezing, runny nose, itchy red eyes, and coughing fits.",
        "action_rule": "Rinse your face with cool water after coming inside on dusty days; keep windows facing dusty roads closed."
    },
    {
        "term": "AQI",
        "technical_name": "Air Quality Index (0 to 500 Scale)",
        "plain_name": "The Air Health Thermometer",
        "category": "standards",
        "category_label": "📊 Indices & Benchmarks",
        "badge_color": "#10B981",
        "icon": "🌡️",
        "analogy": "Just like 37°C means a healthy body and 40°C means a high fever, an AQI of 30 means fresh mountain air, while an AQI of 250 means the sky has a severe pollution fever!",
        "what_it_is": "A standardized color-coded scale from 0 to 500 created by health scientists to tell you how clean or polluted the outdoor air is in one single number.",
        "why_it_matters": "Green (0–50) = Pristine air; Yellow (51–100) = Acceptable; Orange (101–150) = Sensitive lungs take care; Red (151–200) = Unhealthy for all; Purple/Maroon (>200) = Dangerous emergency.",
        "action_rule": "Treat AQI like the weather: Green means go outside freely; Red means move your workouts indoors and seal doors."
    },
    {
        "term": "Thermal Inversion",
        "technical_name": "Nocturnal Temperature Inversion Layer",
        "plain_name": "The Cold Air Pot Lid",
        "category": "weather",
        "category_label": "🌤️ Weather & Atmospheric Physics",
        "badge_color": "#3B82F6",
        "icon": "🍲",
        "analogy": "Imagine boiling soup in a pot with a cold glass lid on top. The steam cannot escape and bounces off the lid!",
        "what_it_is": "On cold winter nights, the ground chills rapidly, leaving a cold air blanket trapped underneath a warmer layer above. This warm layer acts like an airtight lid over your entire city.",
        "why_it_matters": "All the car exhaust, factory smoke, and morning cooking fumes cannot rise up, so they stay trapped right down on the streets where you walk, causing sharp morning smog spikes.",
        "action_rule": "In winter months, wait until the sun warms the earth and 'lifts the lid' (usually after 9:30 AM) before going for vigorous outdoor morning runs."
    },
    {
        "term": "NO₂",
        "technical_name": "Nitrogen Dioxide",
        "plain_name": "Vehicle & Diesel Tailpipe Gas",
        "category": "pollutants",
        "category_label": "🧪 The Pollutants",
        "badge_color": "#EA580C",
        "icon": "🚗",
        "analogy": "The sharp, bitter-smelling reddish gas you notice when standing directly behind a rumbling diesel bus.",
        "what_it_is": "A toxic gas formed whenever fossil fuels (petrol, diesel, gas, coal) burn at very high engine temperatures.",
        "why_it_matters": "NO₂ inflames the lining of your breathing tubes, worsening asthma symptoms and increasing childhood susceptibility to respiratory infections.",
        "action_rule": "Walk on tree-lined neighborhood streets and park paths instead of jogging directly beside crowded arterial highways."
    },
    {
        "term": "O₃",
        "technical_name": "Tropospheric Ground-Level Ozone",
        "plain_name": "Sun-Baked Summer Smog",
        "category": "pollutants",
        "category_label": "🧪 The Pollutants",
        "badge_color": "#D97706",
        "icon": "☀️",
        "analogy": "Remember: 'Good up high in space, bad down nearby in our lungs!' It protects Earth high in the stratosphere, but stings our lungs down on street level.",
        "what_it_is": "Ozone is not emitted directly from tailpipes; it gets 'cooked' when hot summer sunlight bakes vehicle exhaust and chemical fumes together.",
        "why_it_matters": "Breathing ground ozone feels like getting a mild sunburn inside your lungs! It causes chest tightness, shortness of breath, and throat scratchiness.",
        "action_rule": "In hot summer heatwaves, plan your outdoor walks and runs during the cool early morning or late dusk when sunlight is low."
    },
    {
        "term": "SO₂",
        "technical_name": "Sulfur Dioxide",
        "plain_name": "Industrial Coal & Factory Fumes",
        "category": "pollutants",
        "category_label": "🧪 The Pollutants",
        "badge_color": "#8B5CF6",
        "icon": "🏭",
        "analogy": "The sharp, choking smell of a freshly struck sulfur match multiplied a thousand times.",
        "what_it_is": "A pungent gas released when industrial power plants burn sulfur-rich coal or when crude oil is refined.",
        "why_it_matters": "Causes immediate throat tightness and wheezing, and mixes with atmospheric moisture to form acid rain.",
        "action_rule": "Check if your city is downwind of coal power generation clusters; stay indoors when industrial alerts are broadcast."
    },
    {
        "term": "CO",
        "technical_name": "Carbon Monoxide",
        "plain_name": "The Odorless Invisible Gas",
        "category": "pollutants",
        "category_label": "🧪 The Pollutants",
        "badge_color": "#64748B",
        "icon": "⚠️",
        "analogy": "A silent, invisible ghost gas that has zero smell, zero color, and zero taste.",
        "what_it_is": "Produced when fuels burn without enough oxygen—such as idling vehicle engines, gas stoves, generators, and wood charcoal braziers.",
        "why_it_matters": "When inhaled, CO glues itself to your red blood cells, blocking them from carrying life-giving oxygen to your brain and heart.",
        "action_rule": "Never run a car engine or petrol generator inside a closed garage, and ensure gas water heaters have exterior exhaust pipes."
    },
    {
        "term": "PBL",
        "technical_name": "Planetary Boundary Layer Height",
        "plain_name": "The Sky's Breathing Room Height",
        "category": "weather",
        "category_label": "🌤️ Weather & Atmospheric Physics",
        "badge_color": "#0284C7",
        "icon": "📏",
        "analogy": "Imagine a bedroom with a magical ceiling that rises to 2,000 meters high at noon, and drops down to 200 meters at bedtime!",
        "what_it_is": "The thickness of the lowest layer of the atmosphere where human beings live and breathe. Daytime sunshine lifts the ceiling; nighttime cooling lowers it.",
        "why_it_matters": "When the ceiling is high (sunny afternoons), smoke has lots of room to disperse and dilute. When the ceiling is low (chilly nights), smoke is squished close to the ground.",
        "action_rule": "AirFusion automatically tracks boundary layer height to predict when pollution will clear out each day."
    },
    {
        "term": "Ventilation Coeff.",
        "technical_name": "Ventilation Coefficient (V_c = PBL × Wind)",
        "plain_name": "The City Flushing Power",
        "category": "weather",
        "category_label": "🌤️ Weather & Atmospheric Physics",
        "badge_color": "#059669",
        "icon": "🌀",
        "analogy": "Like opening a window and turning on a giant ceiling fan at the same time to blow stale air out of a kitchen.",
        "what_it_is": "A number calculated by multiplying how high the sky is by how fast the wind is blowing. It measures how effectively the atmosphere cleans itself.",
        "why_it_matters": "V_c > 6,000 m²/s means the atmosphere is rapidly flushing away city pollution; V_c < 2,000 m²/s means stagnant air and dangerous smog accumulation.",
        "action_rule": "Look for the 'Breezy Ventilation' badge on AirFusion for the safest outdoor running windows."
    },
    {
        "term": "N95 / FFP2",
        "technical_name": "Electrostatic Particulate Respirator",
        "plain_name": "The Micro-Filter Magnet Mask",
        "category": "gear",
        "category_label": "🛡️ Masks & Safety Equipment",
        "badge_color": "#FF6845",
        "icon": "😷",
        "analogy": "A cloth bandana is like a tennis racket trying to catch sand grains; an N95 is like an electric magnet that grabs 95% of tiny microscopic soot particles!",
        "what_it_is": "A certified close-fitting mask made from electrostatically charged polypropylene micro-fibers.",
        "why_it_matters": "Filters out particles as small as 0.3 micrometers, preventing hazardous combustion soot from reaching your delicate lung alveoli.",
        "action_rule": "Ensure the mask forms a tight seal around your nose bridge and chin; a loose mask with gaps lets 50% of dirty air sneak inside."
    },
    {
        "term": "HEPA",
        "technical_name": "High-Efficiency Particulate Air Filter",
        "plain_name": "The Hospital-Grade Room Sieve",
        "category": "gear",
        "category_label": "🛡️ Masks & Safety Equipment",
        "badge_color": "#06B6D4",
        "icon": "🏡",
        "analogy": "An ultra-dense maze of microscopic glass threads so tangled that dust particles get trapped like flies in a spiderweb.",
        "what_it_is": "A mechanical air filter standard certifying that 99.97% of all airborne particles down to 0.3 micrometers are trapped.",
        "why_it_matters": "Removes pet dander, dust mites, pollen, and outdoor traffic soot from your bedroom air while you sleep.",
        "action_rule": "Place your HEPA purifier in the bedroom where you spend 8 continuous hours breathing; replace filters every 6 to 12 months."
    },
    {
        "term": "GRAP",
        "technical_name": "Graded Response Action Plan",
        "plain_name": "Emergency Smog Action Curfews",
        "category": "rules",
        "category_label": "🏛️ Regulations & Directives",
        "badge_color": "#DC2626",
        "icon": "📜",
        "analogy": "Like emergency fire drill alarms for entire cities. When smog reaches danger levels, strict rules immediately turn on!",
        "what_it_is": "A set of legally binding emergency measures in regions like Delhi-NCR activated by the Commission for Air Quality Management (CAQM).",
        "why_it_matters": "Stage 1 (Poor) triggers dust vacuuming; Stage 2 (Very Poor) halts diesel generator sets; Stage 3 (Severe) bans older diesel cars & construction; Stage 4 (Severe+) closes schools and halts diesel trucks.",
        "action_rule": "Check AirFusion's News tab for live GRAP enforcement updates to avoid traffic fines and know school closures."
    },
    {
        "term": "CAAQMS",
        "technical_name": "Continuous Ambient Air Quality Monitoring Station",
        "plain_name": "Government Sentry Rooftop Towers",
        "category": "rules",
        "category_label": "🏛️ Regulations & Directives",
        "badge_color": "#7C3AED",
        "icon": "📡",
        "analogy": "High-tech rooftop guard posts equipped with laser spectrometers and automated sensors monitoring the air 24 hours a day.",
        "what_it_is": "Government-operated monitoring stations (managed by CPCB, EPA, DEFRA) that continuously analyze ambient air and feed data to AirFusion.",
        "why_it_matters": "Provides gold-standard, calibrated, tamper-proof air quality data so your decisions are based on real scientific ground truth.",
        "action_rule": "AirFusion automatically synchronizes with the nearest CAAQMS tower to your current GPS or chosen city location."
    }
]


# ==============================================================================
# 3. COMPONENT RENDERERS
# ==============================================================================

def render_simple_storytelling_section(
    city_name: str = "Active Sector",
    aqi_val: int = 45,
    pm25_val: float = 18.0
) -> None:
    """
    Renders an illustrated, engaging, 4-chapter clean air storybook in Simple Mode.
    Translates complex atmospheric physics into inspiring, memorable, family-friendly narratives.
    """
    safe_markdown("""
    <!-- Audio Narration Script -->
    <script>
    function narrateStoryChapter(chapterNum, title, scriptText) {
        if (!('speechSynthesis' in window)) {
            console.log("Speech synthesis is not supported in your browser.");
            return;
        }
        window.speechSynthesis.cancel();
        let u = new SpeechSynthesisUtterance(scriptText);
        let voices = window.speechSynthesis.getVoices();
        let naturalVoice = voices.find(v => (
            v.name.includes('Natural') ||
            v.name.includes('Google') ||
            v.name.includes('Jenny') ||
            v.name.includes('Samantha') ||
            v.name.includes('Zira') ||
            v.lang.startsWith('en')
        ));
        if (naturalVoice) u.voice = naturalVoice;
        u.pitch = 1.04;
        u.rate = 0.94;
        window.speechSynthesis.speak(u);
    }
    function stopStoryNarration() {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
    }
    </script>
    """)

    with st.container(border=True):
        header_html = f"""
        <div style="margin-bottom: 16px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.10); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 9999px; padding: 4px 14px; margin-bottom: 8px;">
                <span style="font-size: 0.9rem;">📖</span>
                <span style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #059669; text-transform: uppercase; letter-spacing: 0.08em;">
                    THE CLEAN AIR STORYBOOK • TRANSLATING SCIENCE FOR FAMILIES
                </span>
            </div>
            <h2 style="font-family: var(--font-heading); font-size: 1.45rem; font-weight: 800; color: #1F344C; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                Understanding Your Air: A 4-Chapter Clean Air Adventure
            </h2>
            <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0; line-height: 1.55;">
                Explore how the invisible sky breathes over {city_name}, meet your four clean air fusionians, and discover simple, stress-free habits to protect every breath your family takes.
            </p>
        </div>
        """
        safe_markdown(header_html)

        # Tabbed Chapters
        chap_tabs = st.tabs([
            "☁️ Ch 1: Invisible Kingdom",
            "🛡️ Ch 2: Four Guardians",
            "🌤️ Ch 3: Magic Sun & Pot Lid",
            "🏡 Ch 4: Family Action Plan"
        ])

        for idx, tab in enumerate(chap_tabs):
            chap = CLEAN_AIR_STORY_CHAPTERS[idx]
            with tab:
                mascot_img = get_mascot_base64(chap["mascot"])
                col_img, col_text = st.columns([1.1, 2.2])

                with col_img:
                    clean_script = chap['voice_script'].replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
                    safe_markdown(f"""
                    <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-radius: 16px; padding: 16px; text-align: center; margin-bottom: 12px;">
                        <img src="{mascot_img}" alt="{chap['title']}" style="width: 100%; max-height: 220px; object-fit: cover; border-radius: 12px; display: block; margin-bottom: 12px; box-shadow: 0 4px 14px rgba(31,52,76,0.06);" />
                        <span style="font-family: var(--font-mono); font-size: 0.68rem; font-weight: 800; color: {chap['badge_color']}; background: #FFFFFF; border: 1px solid #E2E8F0; padding: 3px 10px; border-radius: 9999px;">
                            {chap['hero_badge']}
                        </span>
                        <div style="font-family: var(--font-sans); font-size: 0.78rem; color: #64748B; margin-top: 8px; font-style: italic; line-height: 1.4;">
                            💡 Analogy: {chap['analogy']}
                        </div>
                        <div style="display: flex; gap: 6px; margin-top: 12px;">
                            <button onclick="narrateStoryChapter('{chap['number']}', '{chap['title']}', '{clean_script}');" type="button" style="flex: 1; display: inline-flex; align-items: center; justify-content: center; gap: 6px; background: #FFFFFF; border: 1.5px solid {chap['badge_color']}; color: {chap['badge_color']}; font-family: var(--font-heading); font-size: 0.80rem; font-weight: 800; padding: 8px 12px; border-radius: 10px; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                                🔊 Listen Aloud
                            </button>
                            <button onclick="stopStoryNarration();" type="button" title="Stop Audio" style="background: #F1F5F9; border: 1px solid #CBD5E1; color: #64748B; font-family: var(--font-mono); font-size: 0.75rem; font-weight: 700; padding: 8px 12px; border-radius: 10px; cursor: pointer;">
                                ⏹️ Stop
                            </button>
                        </div>
                    </div>
                    """)

                with col_text:
                    safe_markdown(f"""
                    <div>
                        <div style="font-family: var(--font-mono); font-size: 0.70rem; font-weight: 800; color: {chap['badge_color']}; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px;">
                            {chap['number']} &bull; ILLUSTRATED LESSON
                        </div>
                        <h3 style="font-family: var(--font-heading); font-size: 1.25rem; font-weight: 800; color: #1F344C; margin: 0 0 6px 0; line-height: 1.3;">
                            {chap['title']}
                        </h3>
                        <p style="font-family: var(--font-sans); font-size: 0.85rem; color: #FF6845; font-weight: 600; margin: 0 0 12px 0;">
                            {chap['subtitle']}
                        </p>
                        <div style="font-family: var(--font-sans); font-size: 0.86rem; color: #475569; line-height: 1.65; margin-bottom: 16px; background: #FFFFFF; border: 1px solid #EBE6DF; border-radius: 12px; padding: 14px 18px;">
                            {chap['story'].strip().replace(chr(10) + chr(10), '<br/><br/>')}
                        </div>
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px 16px;">
                            <div style="font-family: var(--font-heading); font-size: 0.78rem; font-weight: 800; color: #1F344C; text-transform: uppercase; margin-bottom: 6px;">
                                🌟 Key Family Takeaways from this Chapter:
                            </div>
                            {"".join(f'<div style="font-family: var(--font-sans); font-size: 0.80rem; color: #334155; margin-bottom: 4px; line-height: 1.45;">• {tk}</div>' for tk in chap['takeaways'])}
                        </div>
                    </div>
                    """)


def render_simple_terminology_decoder() -> None:
    """
    Renders the interactive 'Everyday Air Decoder' catalog in Simple Mode.
    Decodes complex scientific, medical, and meteorological terms into
    crystal-clear everyday language, real-world analogies, and practical family action rules.
    """
    safe_markdown("""
    <div style="margin: 24px 0 14px 0;">
        <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 9999px; padding: 4px 14px; margin-bottom: 6px;">
            <span style="font-size: 0.9rem;">💡</span>
            <span style="font-family: var(--font-heading); font-size: 0.72rem; font-weight: 800; color: #0284C7; text-transform: uppercase; letter-spacing: 0.08em;">
                EVERYDAY AIR DECODER • PLAIN-ENGLISH TRANSLATOR
            </span>
        </div>
        <h2 style="font-family: var(--font-heading); font-size: 1.4rem; font-weight: 800; color: #1F344C; margin: 0 0 6px 0; letter-spacing: -0.02em;">
            Confused by Science Words? Here is What They Really Mean!
        </h2>
        <p style="font-family: var(--font-sans); font-size: 0.88rem; color: #5A6E85; margin: 0; line-height: 1.55;">
            We translated all 14 technical terms used across this website into clear real-world analogies and practical action rules so every family member can understand with confidence.
        </p>
    </div>
    """)

    # Interactive Filter by Category
    filter_col1, filter_col2 = st.columns([1.5, 1.5])
    with filter_col1:
        cat_choice = st.selectbox(
            "🏷️ Filter Terms by Category:",
            options=[
                "🌟 Show All Terms (14 Total)",
                "🧪 The Pollutants (PM2.5, PM10, NO2, O3, SO2, CO)",
                "🌤️ Weather & Atmospheric Physics (Inversion, PBL, Ventilation)",
                "📊 Indices & Benchmarks (AQI, Safe Windows)",
                "🛡️ Masks & Safety Equipment (N95, HEPA Filters)",
                "🏛️ Regulations & Directives (GRAP, CAAQMS)"
            ],
            index=0,
            key="decoder_category_filter"
        )

    with filter_col2:
        search_kw = st.text_input(
            "🔍 Quick Search Term or Keyword:",
            placeholder="e.g. Inversion, PM2.5, Mask, Ozone, AQI...",
            key="decoder_search_input"
        ).strip().lower()

    # Filter items
    filtered_terms = EVERYDAY_TERMS_CATALOG
    if "The Pollutants" in cat_choice:
        filtered_terms = [t for t in filtered_terms if t["category"] == "pollutants"]
    elif "Weather & Atmospheric Physics" in cat_choice:
        filtered_terms = [t for t in filtered_terms if t["category"] == "weather"]
    elif "Indices & Benchmarks" in cat_choice:
        filtered_terms = [t for t in filtered_terms if t["category"] == "standards"]
    elif "Masks & Safety Equipment" in cat_choice:
        filtered_terms = [t for t in filtered_terms if t["category"] == "gear"]
    elif "Regulations & Directives" in cat_choice:
        filtered_terms = [t for t in filtered_terms if t["category"] == "rules"]

    if search_kw:
        filtered_terms = [
            t for t in filtered_terms
            if (search_kw in t["term"].lower() or
                search_kw in t["plain_name"].lower() or
                search_kw in t["what_it_is"].lower() or
                search_kw in t["analogy"].lower())
        ]

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if not filtered_terms:
        st.info("No terms found matching your search. Try typing 'PM2.5', 'AQI', 'Inversion', or 'Mask'!")
        return

    # Two-Column Card Grid
    grid_cols = st.columns(2)
    for idx, item in enumerate(filtered_terms):
        with grid_cols[idx % 2]:
            with st.container(border=True):
                card_html = f"""
                <div>
                    <!-- Header with Badge and Category -->
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                        <div>
                            <span style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #1F344C; display: inline-flex; align-items: center; gap: 6px;">
                                <span>{item['icon']}</span>
                                <span>{item['term']}</span>
                            </span>
                            <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #64748B;">
                                Scientific Name: {item['technical_name']}
                            </div>
                        </div>
                        <span style="font-family: var(--font-mono); font-size: 0.65rem; font-weight: 700; color: {item['badge_color']}; background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); padding: 2px 8px; border-radius: 9999px;">
                            {item['category_label'].split(' ')[-1]}
                        </span>
                    </div>

                    <!-- Plain English Translation Title -->
                    <div style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 800; color: {item['badge_color']}; margin-bottom: 8px;">
                        👉 What It Really Means: {item['plain_name']}
                    </div>

                    <!-- Concrete Everyday Analogy Box -->
                    <div style="background: #FAF6F1; border: 1px solid #EBE6DF; border-left: 4px solid {item['badge_color']}; border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; font-family: var(--font-sans); font-size: 0.82rem; color: #1F344C; line-height: 1.45;">
                        <strong style="color: {item['badge_color']};">💡 Real-Life Analogy:</strong> {item['analogy']}
                    </div>

                    <!-- Plain Explanation -->
                    <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #475569; line-height: 1.5; margin-bottom: 8px;">
                        <strong style="color: #1F344C;">What It Is:</strong> {item['what_it_is']}
                    </div>
                    <div style="font-family: var(--font-sans); font-size: 0.82rem; color: #475569; line-height: 1.5; margin-bottom: 10px;">
                        <strong style="color: #DC2626;">Health Effect:</strong> {item['why_it_matters']}
                    </div>

                    <!-- What You Should Do Action Rule -->
                    <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 8px 12px; font-family: var(--font-sans); font-size: 0.80rem; color: #166534; line-height: 1.45;">
                        <strong>✅ What You Should Do:</strong> {item['action_rule']}
                    </div>
                </div>
                """
                safe_markdown(card_html)
