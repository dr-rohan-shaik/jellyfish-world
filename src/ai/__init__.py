"""AI module for Jellyfish World."""

from src.ai.adapter import query_jellyfish_ai
from src.ai.decision_engine import decide_choice, extract_options, is_decision_query
from src.ai.semantic_engine import generate_semantic_reply
from src.ai.personalization import PersonalizationBuilder
from src.ai.anti_hallucination import (
    AntiHallucinationGuard,
    HallucinationCheck,
    create_anti_hallucination_guard,
)

__all__ = [
    # Main API
    "query_jellyfish_ai",
    # Decision engine
    "decide_choice",
    "extract_options",
    "is_decision_query",
    # Semantic responses
    "generate_semantic_reply",
    # Personalization
    "PersonalizationBuilder",
    # Anti-hallucination
    "AntiHallucinationGuard",
    "HallucinationCheck",
    "create_anti_hallucination_guard",
]

# Optional: Local LLM support
try:
    from src.ai.local_llm import (
        LocalLLMClient,
        LLMConfig,
        LocalLLMBackend,
        PersonalizationProfile,
    )

    __all__.extend([
        "LocalLLMClient",
        "LLMConfig",
        "LocalLLMBackend",
        "PersonalizationProfile",
    ])
except ImportError:
    pass