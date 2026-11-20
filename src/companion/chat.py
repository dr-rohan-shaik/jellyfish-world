"""In-character conversational engine for Jellyfish World.

Routes through the unified AI Adapter:
- Decision resolution (parsing options and deciding)
- Semantic contextual responses (mindfulness, debugging, ocean lore)
- Optional BYOK remote endpoints

Strict guardrails:
1. Answers in 1-3 gentle, calming sentences.
2. In character: a translucent bioluminescent jellyfish companion.
3. Never claims physical pain or sickness.
4. Never mentions being an AI or language model.
5. Does NOT store conversation history (locked rules).
"""
from __future__ import annotations

from src.ai.adapter import query_jellyfish_ai


def respond_to_owner(message: str, jellyfish_name: str = "Aurelia", mood: str = "calm") -> str:
    """Generate in-character reply to owner message."""
    reply = query_jellyfish_ai(message, jellyfish_name, mood)
    return f"{jellyfish_name}: {reply}"
