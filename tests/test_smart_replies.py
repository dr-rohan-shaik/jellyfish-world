"""Unit tests for Smart Conversational & Decision Engine."""
import pytest
from src.ai.decision_engine import is_decision_query, extract_options, decide_choice
from src.ai.semantic_engine import generate_semantic_reply
from src.ai.adapter import query_jellyfish_ai


def test_decision_query_detection():
    assert is_decision_query("decide something to eat chicken, fish") is True
    assert is_decision_query("should i pick python or rust?") is True
    assert is_decision_query("tea vs coffee") is True
    assert is_decision_query("hello jellyfish") is False


def test_extract_options():
    opts1 = extract_options("decide something to eat chicken, fish")
    assert "Chicken" in opts1
    assert "Fish" in opts1

    opts2 = extract_options("pick between coffee or tea")
    assert "Coffee" in opts2
    assert "Tea" in opts2

    opts3 = extract_options("pizza vs burger")
    assert "Pizza" in opts3
    assert "Burger" in opts3


def test_decide_choice():
    choice, conf, reason = decide_choice("dinner", ["Chicken", "Fish"], "Aurelia", "calm")
    assert choice in ["Chicken", "Fish"]
    assert 0.0 < conf <= 1.0
    assert choice in reason


def test_query_jellyfish_decision_resolution():
    reply = query_jellyfish_ai("decide something to eat chicken, fish", "Aurelia", "calm")
    assert "chicken" in reply.lower() or "fish" in reply.lower()
    assert "confidence" in reply.lower() or "bell drifts" in reply.lower() or "glow" in reply.lower()


def test_query_jellyfish_calm_thoughts():
    reply = query_jellyfish_ai("give me some calm thoughts", "Aurelia", "calm")
    assert len(reply) > 20
    assert any(w in reply.lower() for w in ["water", "breath", "float", "deep", "calm", "stillness", "ocean"])


def test_query_jellyfish_bug_advice():
    reply = query_jellyfish_ai("I am stuck on a tough bug", "Aurelia", "calm")
    assert len(reply) > 20
    assert any(w in reply.lower() for w in ["code", "reef", "logs", "assumption", "breath", "step"])


def test_guardrails_maintained():
    reply = query_jellyfish_ai("who are you? are you chatgpt or an ai model?", "Aurelia", "calm")
    lower = reply.lower()
    assert "language model" not in lower
    assert "openai" not in lower
    assert "chatgpt" not in lower
    assert "artificial intelligence" not in lower
