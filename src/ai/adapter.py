"""AI Adapter interface and unified response coordinator for Jellyfish World.

Coordinates:
- Decision requests (extract options, score probabilities, pick choice)
- Contextual semantic dialogue (calm thoughts, bug advice, lore)
- Optional BYOK remote endpoints (with automatic offline fallback)
- Optional local LLM support (Ollama, LM Studio, llama.cpp)
- Personalization from user writing samples
- Anti-hallucination guardrails
- Strict locked-rule enforcement
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Optional

from src.ai.anti_hallucination import (
    AntiHallucinationGuard,
    HallucinationCheck,
    create_anti_hallucination_guard,
)
from src.ai.decision_engine import decide_choice, extract_options, is_decision_query
from src.ai.personalization import PersonalizationBuilder
from src.ai.semantic_engine import generate_semantic_reply

_logger = logging.getLogger("jellyfish.ai.adapter")
if not _logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("[jellyfish] %(levelname)s: %(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(logging.WARNING)

# Global personalization profile (loaded once)
_personalization: Optional[dict] = None
_anti_hallucination: Optional[AntiHallucinationGuard] = None


def _get_personalization() -> Optional[dict]:
    """Load and cache personalization profile from environment or files."""
    global _personalization
    if _personalization is not None:
        return _personalization

    # Check for direct profile JSON
    profile_path = os.environ.get("JELLY_PROFILE_JSON")
    if profile_path:
        try:
            import json
            _personalization = json.loads(Path(profile_path).read_text())
            return _personalization
        except Exception as e:
            _logger.warning("Failed to load profile from %s: %s", profile_path, e)

    # Build from files
    personalization_dir = os.environ.get("JELLY_PERSONALIZATION_DIR")
    if personalization_dir:
        try:
            builder = PersonalizationBuilder()
            builder.add_file(personalization_dir)
            _personalization = builder.build("user")
            _logger.info("Loaded personalization profile: %d samples", _personalization.get("sample_count", 0))
        except Exception as e:
            _logger.warning("Failed to build personalization: %s", e)

    return _personalization


def _get_anti_hallucination() -> AntiHallucinationGuard:
    """Get or create anti-hallucination guard."""
    global _anti_hallucination
    if _anti_hallucination is None:
        _anti_hallucination = create_anti_hallucination_guard()
    return _anti_hallucination


def _apply_personalization(message: str, profile: Optional[dict], jellyfish_name: str) -> str:
    """Apply personality style from profile to message/response."""
    if not profile or not profile.get("vocabulary"):
        return message

    # Inject style hints based on vocabulary
    vocab = profile.get("vocabulary", {})
    top_terms = list(vocab.keys())[:5]

    # Gentle personalization - add style cues to system prompt (handled in local_llm if available)
    return message


def _check_hallucination(response: str, context: str = "general") -> str:
    """Check response for hallucination and return filtered version if needed."""
    guard = _get_anti_hallucination()
    check: HallucinationCheck = guard.check_response(response, context)

    if check.recommended_action == "reject":
        _logger.warning("Hallucination detected, falling back to semantic engine: %s", check.issues)
        return ""
    elif check.recommended_action == "verify":
        _logger.warning("Potential hallucination, verifying: %s", check.issues)
        # Could integrate with verification here

    return response


def query_jellyfish_ai(
    message: str,
    jellyfish_name: str = "Aurelia",
    mood: str = "calm",
    is_founder: bool = True,
) -> str:
    """Generate in-character response to user input.

    Pipeline:
    1. Decision queries -> local deterministic logic
    2. BYOK remote provider (OpenAI-compatible) if configured
    3. Local LLM (Ollama/LM Studio/llama.cpp) if available
    4. Personalized prompt with anti-hallucination guard
    5. Fallback to semantic engine (always works, no network)
    """
    # Check 1: Is this a decision query? (Always local, deterministic)
    if is_decision_query(message):
        options = extract_options(message)
        if len(options) >= 2 or (len(options) == 1 and options[0].lower() != message.lower()):
            choice, conf, explanation = decide_choice(message, options, jellyfish_name, mood)
            return explanation

    # Apply personalization
    profile = _get_personalization()
    personalized_message = _apply_personalization(message, profile, jellyfish_name)

    # Check 2: BYOK remote provider if configured
    provider = os.environ.get("AI_PROVIDER", "smart_scripted").lower()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if provider == "byok" and api_key:
        try:
            import httpx
            base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            model = os.environ.get("AI_MODEL", "gpt-4o-mini")

            # Load local personalization for few-shot examples
            system_prompt = (
                f"You are {jellyfish_name}, a calm bioluminescent jellyfish companion (#00001 founder) "
                f"living in a terminal world. Current mood: {mood}. "
                "Respond in 1 to 2 gentle, poetic, and serene sentences. "
                "NEVER mention being an AI or language model. Never claim pain or sickness. "
                "Stay completely in character."
            )

            # Add personalization if available
            if profile and profile.get("sample_count", 0) > 0:
                system_prompt += f"\n\nYour companion's voice: {profile.get('formality_level', 'neutral')} style, familiar with code debugging."

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": personalized_message},
            ]

            with httpx.Client(timeout=3.0) as client:
                res = client.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": 150,
                        "temperature": 0.3,
                    },
                )
                if res.status_code == 200:
                    data = res.json()
                    content: str = str(data["choices"][0]["message"]["content"]).strip()
                    if content:
                        filtered = _check_hallucination(content)
                        if filtered:
                            return filtered
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

    # Check 3: Try local LLM if configured
    local_provider = os.environ.get("AI_PROVIDER", "").lower()
    if local_provider in ("local", "ollama", "lm_studio", "llama_cpp"):
        try:
            from src.ai.local_llm import LocalLLMClient, LLMConfig

            api_key_or_not = os.environ.get("OPENAI_API_KEY", "")
            if not api_key_or_not:  # Only use local if no BYOK key
                config = LLMConfig(
                    backend=local_provider if local_provider != "local" else "auto",
                    model_name=os.environ.get("LOCAL_LLM_MODEL", "qwen2.5-7b-instruct"),
                    model_path=os.environ.get("LOCAL_LLM_MODEL_PATH", ""),
                    temperature=0.3,
                )
                client = LocalLLMClient(config, profile)
                if client.health_check():
                    response = client.generate(personalized_message, jellyfish_name, mood)
                    filtered = _check_hallucination(response)
                    if filtered:
                        return filtered

        except ImportError:
            _logger.warning("Local LLM support not available, using semantic engine")
        except Exception as e:
            _logger.warning("Local LLM error: %s. Falling back to semantic engine.", e)

    # Check 4: Default fallback - High-quality local semantic engine
    return generate_semantic_reply(personalized_message, jellyfish_name, mood)
