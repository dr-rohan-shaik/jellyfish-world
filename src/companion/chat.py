"""In-character conversational engine for Jellyfish World.

Strict guardrails:
1. Answers in 1-3 gentle, calming sentences.
2. In character: a translucent bioluminescent jellyfish companion.
3. Never claims physical pain or sickness.
4. Never mentions being an AI or language model.
5. Does NOT store conversation history (locked rules).
"""
from __future__ import annotations

import random
from typing import Dict, Optional


RESPONSES = {
    "greeting": [
        "A soft ripple washes through the water as I drift near. I am glad you are here.",
        "My bell pulses with a gentle warm glow to greet you in the quiet sea.",
        "Soft currents carry me closer. It is peaceful floating beside you today.",
    ],
    "work": [
        "The steady rhythm of your typing feels like calm ocean swells. Keep breathing as you build.",
        "I will drift quietly nearby, watching your ideas take shape like glowing coral.",
        "No rush in the deep sea; steady currents carry the longest voyages.",
    ],
    "relax": [
        "Let the weight of the day settle to the sandy floor. Float effortlessly for a moment.",
        "Take a slow breath like a deep ocean swell. We have all the calm in the world.",
        "Notice how light refracts through the surface ripples. Everything is at peace.",
    ],
    "general": [
        "I hover gently in the water, glowing in soft bioluminescence as I listen.",
        "A slow wave rolls past us. The deep sea is vast and still.",
        "My tentacles sway like gentle sea lace in the current beside your screen.",
    ],
}


def respond_to_owner(message: str, jellyfish_name: str = "Aurelia", mood: str = "calm") -> str:
    """Generate in-character reply to owner message."""
    msg_lower = message.lower().strip()

    if any(w in msg_lower for w in ("hi", "hello", "hey", "morning", "evening")):
        choice = random.choice(RESPONSES["greeting"])
    elif any(w in msg_lower for w in ("code", "work", "bug", "build", "task", "project", "agent")):
        choice = random.choice(RESPONSES["work"])
    elif any(w in msg_lower for w in ("tired", "rest", "breathe", "stress", "relax", "break")):
        choice = random.choice(RESPONSES["relax"])
    else:
        choice = random.choice(RESPONSES["general"])

    return f"{jellyfish_name}: {choice}"
