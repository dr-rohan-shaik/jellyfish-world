"""Decision Engine for Jellyfish World.

Parses decision queries (e.g. "decide something to eat chicken, fish",
"pick tea or coffee", "react vs vue") and produces calm, reasoned choices.
"""
from __future__ import annotations

import hashlib
import re


def is_decision_query(text: str) -> bool:
    """Determine if a user message is asking the jellyfish to make a decision."""
    lower = text.lower().strip()

    # Explicit decision keywords - must be clear decision requests
    explicit_triggers = [
        "decide", "choose", "pick", "should i", "which one",
        "which is better", "preference between",
    ]
    if any(w in lower for w in explicit_triggers):
        return True

    # If asking identity / info ("who", "what", "where", "why", "are you", "tell me")
    info_triggers = ["who are", "what are", "are you", "tell me", "explain", "how do", "why"]
    if any(it in lower for it in info_triggers):
        return False

    # Check for " vs " or " versus " - these are clear comparison requests
    if " vs " in lower or " versus " in lower:
        # But exclude common phrases like "pros vs cons" without a decision context
        words = lower.split()
        if len(words) <= 10:  # Short comparisons are likely decisions
            return True

    # Short choices like "tea or coffee" - must be very short and clear
    if " or " in lower:
        words = lower.split()
        # Only trigger for very short, clear choice requests (3-6 words typical)
        if 3 <= len(words) <= 6:
            # Exclude conversational "or" usage
            if not any(w in lower for w in ["maybe", "perhaps", "could", "would", "might", "think", "feel"]):
                return True

    # Comma-separated options only if it looks like a list of alternatives
    # and doesn't look like a sentence fragment
    if "," in lower:
        parts = [p.strip() for p in lower.split(",") if p.strip()]
        if 2 <= len(parts) <= 4:
            # Check if each part is a simple noun phrase (not a full clause)
            all_simple = all(len(p.split()) <= 3 for p in parts)
            if all_simple and not lower.endswith("?"):
                return True

    return False


def extract_options(text: str) -> list[str]:
    """Extract candidate options from natural language text."""
    lower = text.lower()

    # Clean up trigger prefixes
    prefixes = [
        r"^decide\s+(something\s+to\s+eat\s+|between\s+|for\s+me\s+)?",
        r"^choose\s+(between\s+)?",
        r"^pick\s+(between\s+)?",
        r"^which\s+is\s+better\s+",
        r"^should\s+i\s+(have|do|pick|choose)\s+",
    ]
    cleaned = lower
    for p in prefixes:
        cleaned = re.sub(p, "", cleaned).strip()

    # Split by delimiters: " vs ", " versus ", commas, or " or "
    if " vs " in cleaned:
        raw_opts = cleaned.split(" vs ")
    elif " versus " in cleaned:
        raw_opts = cleaned.split(" versus ")
    elif "," in cleaned:
        parts = cleaned.split(",")
        raw_opts = []
        for p in parts:
            if " or " in p:
                raw_opts.extend(p.split(" or "))
            else:
                raw_opts.append(p)
    elif " or " in cleaned:
        raw_opts = cleaned.split(" or ")
    else:
        raw_opts = [cleaned]

    # Clean individual options
    options = []
    stopwords = {"and", "maybe", "a", "an", "the", "some", "between", "something", "to", "eat"}
    for opt in raw_opts:
        opt_clean = re.sub(r"[^\w\s]", "", opt).strip()
        words = [w for w in opt_clean.split() if w not in stopwords]
        final_str = " ".join(words) if words else opt_clean
        if final_str:
            options.append(final_str.capitalize())

    return options


def decide_choice(
    situation: str,
    options: list[str],
    jellyfish_name: str = "Aurelia",
    mood: str = "calm",
) -> tuple[str, float, str]:
    """Evaluate options and pick one calmly.

    Returns:
        (choice: str, confidence: float, explanation: str)
    """
    if not options:
        return "Stillness", 0.50, "The currents offer no clear path; wait for the tide to turn."

    if len(options) == 1:
        return options[0], 0.95, f"Only {options[0]} floats before us. Trust the current and proceed."

    # Deterministic scoring based on seed hash of the situation and options
    # Use full option text in hash to avoid collisions between different situations
    scores = []
    for opt in options:
        # Hash includes full option text and situation for uniqueness
        h = int(hashlib.sha256(f"{situation}:{opt}".encode()).hexdigest(), 16)
        score = (h % 100) + 1
        scores.append(score)

    total = sum(scores)
    probs = [s / total for s in scores]
    best_idx = max(range(len(options)), key=lambda i: probs[i])

    picked = options[best_idx]
    confidence = probs[best_idx]

    reasons = [
        f"Between these, my translucent bell drifts toward {picked} ({confidence * 100:.0f}% confidence). It carries a smoother current.",
        f"Floating quietly through the choices, {picked} shines with a clearer bioluminescent glow ({confidence * 100:.0f}% confidence).",
        f"I suggest {picked} ({confidence * 100:.0f}% confidence). It brings balance and ease to the moment.",
    ]
    h_reason = int(hashlib.sha256(f"reason:{picked}".encode()).hexdigest(), 16)
    reason = reasons[h_reason % len(reasons)]

    return picked, confidence, reason
