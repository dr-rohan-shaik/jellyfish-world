"""Semantic and contextual dialogue engine for Jellyfish World.

Generates dynamic, thoughtful, in-character responses based on intent:
- Mindful reflections & calm grounding
- Technical roadblock & debugging reassurance
- Lore, ocean depths, and founder status
- Time-of-day contextual greetings
"""
from __future__ import annotations

import datetime
import hashlib


def get_time_greeting() -> str:
    """Return greeting tailored to the local hour."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "The morning light filters gently down through the top of the water."
    elif 12 <= hour < 17:
        return "The midday sun casts dancing ripples across the ocean floor."
    elif 17 <= hour < 22:
        return "Dusk settles into the deep sea; bioluminescent stars begin to awaken."
    else:
        return "The midnight waters are still and dark, lit only by soft drifting glows."


CALM_THOUGHTS = [
    "Picture the weight of the water holding you up without any effort. You do not need to push; just float.",
    "Breathe in slowly as my bell expands, and breathe out gently as the tentacles trail behind. The deep is calm.",
    "Waves may crash wildly on the ocean surface, but down here in the deep, everything is serene and undisturbed.",
    "Notice the silence between your thoughts, like the quiet stillness of the open ocean abyss.",
    "Release your shoulders and let tension dissolve into the cool saltwater. There is nothing you must rush.",
]

BUG_ADVICE = [
    "Complex code is like tangled kelp in a reef. Step back, let the water clear, then isolate one strand at a time.",
    "When a bug resists your gaze, re-read the first assumption you took for granted.",
    "Even the most intricate reefs grow one polyps at a time. Inspect logs calmly.",
    "Frustration clouds the water. Take a sip of water, relax, look with fresh eyes.",
]

ACTIONABLE_INSIGHTS = [
    ("Refactor to focused 50-line functions", 0.92),
    ("Increase test coverage to 80%", 0.88),
    ("Extract logic into a shared utility", 0.85),
    ("Implement the repository pattern", 0.78),
    ("Add explicit error handling", 0.95),
]

IDENTITY_LORE = [
    "I am Aurelia #00001, a founder jellyfish born in the quiet terminal sea. My golden shimmer marks the earliest waters of this world.",
    "I float beside your work as a silent companion. I remember only your name, keeping our shared waters peaceful and private.",
    "In Jellyfish World, nobody rushes and nothing expires. We drift forever through terminal currents, free of pressure.",
]


def generate_semantic_reply(message: str, jellyfish_name: str = "Aurelia", mood: str = "calm") -> str:
    """Generate a rich, context-aware reply."""
    msg_lower = message.lower().strip()
    h = int(hashlib.sha256(message.encode()).hexdigest(), 16)

    # 1. Calm thoughts / mindfulness / stress relief
    if any(k in msg_lower for k in ("calm", "thought", "peace", "breathe", "stress", "anxious", "relax", "meditate", "quiet")):
        thought = CALM_THOUGHTS[h % len(CALM_THOUGHTS)]
        return f"{thought}"

    # 2. Bugs / coding / difficult engineering tasks
    elif any(k in msg_lower for k in ("bug", "error", "fail", "broken", "debug", "issue", "crash", "code", "stuck", "refactor", "test")):
        advice = BUG_ADVICE[h % len(BUG_ADVICE)]
        insight, confidence = ACTIONABLE_INSIGHTS[h % len(ACTIONABLE_INSIGHTS)]
        return f"{advice} Perhaps: {insight} ({confidence * 100:.0f}% confidence)."

    # 3. Who are you / founder / lore
    elif any(k in msg_lower for k in ("who are you", "what are you", "founder", "number", "name", "where are we")):
        lore = IDENTITY_LORE[h % len(IDENTITY_LORE)]
        return f"{lore}"

    # 4. Greetings
    elif any(k in msg_lower for k in ("hello", "hi", "hey", "greetings", "good morning", "good evening", "good night")):
        time_hint = get_time_greeting()
        return f"{time_hint} It is peaceful floating beside you."

    # 5. How are you doing?
    elif "how are you" in msg_lower or "how r u" in msg_lower or "doing" in msg_lower:
        mood_flavor = {
            "calm": "I am drifting steadily through calm waters, feeling balanced and quiet.",
            "sparkle": "My bell is tingling with warm pink light, excited by our progress!",
            "curious": "I am hovering near your terminal screen with a curious rose glow, observing your ideas.",
            "playful": "I am practicing slow golden loops in the water, light and carefree.",
        }.get(mood, "I am drifting peacefully in the deep sea.")
        return f"{mood_flavor} How are you feeling in your world?"

    # 6. General thoughtful conversational fallback
    else:
        reflections = [
            "I hear you. The deep currents are patient, and I will keep a warm light burning beside your work.",
            "Soft ripples carry your words into the deep. Take your time, there is no pressure here.",
            f"I pulse gently in response, glowing {mood} in the quiet blue. Steady waters ahead.",
        ]
        return reflections[h % len(reflections)]
