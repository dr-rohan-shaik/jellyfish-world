"""Anti-hallucination guard for Jellyfish World AI responses.

Prevents the system from generating false or misleading information by
checking responses against a set of guardrails and confidence scores.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HallucinationCheck:
    """Result of a hallucination check on an AI response."""
    confidence: float
    """Confidence score 0.0 (low) to 1.0 (high) that the response is accurate."""
    recommended_action: str
    """Action to take: 'accept', 'verify', or 'reject'."""
    issues: list[str]
    """List of detected issues or red flags in the response."""


def create_anti_hallucination_guard() -> AntiHallucinationGuard:
    """Factory function to create an anti-hallucination guard instance."""
    return AntiHallucinationGuard()


class AntiHallucinationGuard:
    """Guard that checks AI responses for potential hallucinations."""

    # Common factual anchors that can be verified
    VERIFIABLE_TERMS: set[str] = {
        "python", "3.12", "3.11", "3.10", "2.7", "pip", "venv",
        "windows", "macos", "linux", "ubuntu", "debian"
    }

    # Phrases that often indicate hallucination
    HALLUCINATION_PHRASES: set[str] = {
        "the solution is to", "it is a fact that", "studies show",
        "research proves", "experts agree", "without a doubt"
    }

    def check_response(self, response: str, context: str = "general") -> HallucinationCheck:
        """Check an AI response for potential hallucinations.

        Args:
            response: The AI-generated response to check
            context: The context or domain of the response

        Returns:
            HallucinationCheck with confidence score, recommended action,
            and list of detected issues.
        """
        issues: list[str] = []
        response_lower = response.lower()

        # Check for overconfident language
        for phrase in self.HALLUCINATION_PHRASES:
            if phrase in response_lower:
                issues.append(f"Uses overconfident phrasing: '{phrase}'")

        # Check for unverifiable factual claims
        # Look for specific version numbers, dates, or statistics without qualification
        import re
        version_pattern = r"\d+\.\d+\.\d+"
        version_matches = re.findall(version_pattern, response)
        if version_matches and len(version_matches) > 2:  # More than 2 version claims is suspicious
            issues.append("Multiple specific version numbers claimed without qualification")

        # Check for absolute statements that are likely false
        absolute_patterns = [
            r"\bthe only way\b", r"\balways\b", r"\bnever\b",
            r"\bevery time\b", r"\beach and every\b"
        ]
        for pattern in absolute_patterns:
            if re.search(pattern, response_lower):
                issues.append(f"Contains absolute statement: '{pattern}'")


        # Calculate confidence based on issues found
        # Fewer issues = higher confidence
        base_confidence = 0.8
        penalty_per_issue = 0.15
        confidence = max(0.0, base_confidence - (penalty_per_issue * len(issues)))

        # Determine recommended action
        if len(issues) == 0:
            recommended_action = "accept"
        elif len(issues) == 1:
            recommended_action = "verify"
        else:
            recommended_action = "reject"

        # Boost confidence if response contains verifiable terms
        verifiable_count = sum(1 for term in self.VERIFIABLE_TERMS if term in response_lower)
        if verifiable_count > 0:
            confidence = min(1.0, confidence + 0.1 * verifiable_count)

        return HallucinationCheck(
            confidence=round(confidence, 2),
            recommended_action=recommended_action,
            issues=issues,
        )

