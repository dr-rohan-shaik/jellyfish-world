"""AI Adapter interface and unified response coordinator for Jellyfish World.

Coordinates:
- Decision requests (extract options, score probabilities, pick choice)
- Contextual semantic dialogue (calm thoughts, bug advice, lore)
- Optional BYOK remote endpoints (with automatic offline fallback)
- Strict locked-rule guardrail enforcement
"""
from __future__ import annotations

import logging
import os
import sys

from src.ai.decision_engine import decide_choice, extract_options, is_decision_query
from src.ai.semantic_engine import generate_semantic_reply

# Configure logger for BYOK warnings
_logger = logging.getLogger("jellyfish.ai.adapter")
if not _logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("[jellyfish] %(levelname)s: %(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(logging.WARNING)


def query_jellyfish_ai(
    message: str,
    jellyfish_name: str = "Aurelia",
    mood: str = "calm",
    is_founder: bool = True,
) -> str:
    """Generate in-character response to user input."""
    # Check 1: Is this a decision query?
    if is_decision_query(message):
        options = extract_options(message)
        if len(options) >= 2 or (len(options) == 1 and options[0].lower() != message.lower()):
            choice, conf, explanation = decide_choice(message, options, jellyfish_name, mood)
            return explanation

    # Check 2: BYOK remote provider if configured
    provider = os.environ.get("AI_PROVIDER", "smart_scripted").lower()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if provider == "byok" and api_key:
        try:
            import httpx
            base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            model = os.environ.get("AI_MODEL", "gpt-4o-mini")

            sys_prompt = (
                f"You are {jellyfish_name}, a calm bioluminescent jellyfish companion (#00001 founder) "
                f"living in a terminal world. Current mood: {mood}. "
                "Respond in 1 to 2 gentle, poetic, and serene sentences. "
                "NEVER mention being an AI or language model. Never claim pain or sickness. "
                "Stay completely in character."
            )
            with httpx.Client(timeout=3.0) as client:
                res = client.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": message},
                        ],
                        "max_tokens": 100,
                        "temperature": 0.7,
                    },
                )
                if res.status_code == 200:
                    data = res.json()
                    content: str = str(data["choices"][0]["message"]["content"]).strip()
                    if content:
                        return content
                else:
                    _logger.warning(
                        "BYOK request failed with status %d: %s",
                        res.status_code,
                        res.text[:200],
                    )
        except ImportError:
            _logger.warning(
                "BYOK provider requested but 'httpx' is not installed. "
                "Install with: pip install httpx>=0.27.0. Falling back to local engine."
            )
        except Exception as e:
            _logger.warning(
                "BYOK request failed: %s. Falling back to local semantic engine.",
                e,
            )

    # Default: High-quality local semantic engine
    return generate_semantic_reply(message, jellyfish_name, mood)
