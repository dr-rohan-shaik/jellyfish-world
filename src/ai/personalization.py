"""Personalization builder for Jellyfish World AI responses.

Builds a writer profile from samples and files, enabling style-consistent
in-character responses that match the user's voice.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


class PersonalizationBuilder:
    """Build a personal writing profile from samples and files."""

    def __init__(self) -> None:
        self._samples: list[str] = []
        self._vocabulary: Counter[str] = Counter()
        self._formality_markers: set[str] = set()
        self._informal_markers: set[str] = set()

    def add_sample(self, text: str) -> PersonalizationBuilder:
        """Add a text sample to the profile builder."""
        self._samples.append(text.lower())
        self._update_vocabulary(text.lower())
        self._update_formality(text.lower())
        return self

    def add_file(self, path: Path) -> PersonalizationBuilder:
        """Add an entire file's content to the profile builder."""
        try:
            content = path.read_text(encoding="utf-8")
            self.add_sample(content)
        except Exception:
            pass
        return self

    def _update_vocabulary(self, text: str) -> None:
        """Update vocabulary counts from text."""
        # Remove punctuation and count words
        for word in text.split():
            clean = word.strip(".,;:!?'\"").lower()
            if len(clean) > 2:
                self._vocabulary[clean] += 1

    def _update_formality(self, text: str) -> None:
        """Update formality markers from text."""
        informal_words = {"gonna", "wanna", "kinda", "sorta", "yeah", "hm"}
        formal_words = {"therefore", "hence", "consequently", "nevertheless"}

        for word in text.split():
            clean = word.strip(".,;:!?'\"").lower()
            if clean in informal_words:
                self._informal_markers.add(clean)
            elif clean in formal_words:
                self._formality_markers.add(clean)

    def build(self, name: str = "user") -> dict[str, Any]:
        """Build and return the personalization profile."""
        # Determine formality level based on marker ratios
        total_markers = len(self._formality_markers) + len(self._informal_markers)
        if total_markers == 0:
            formality_level = "neutral"
        elif len(self._formality_markers) > len(self._informal_markers):
            formality_level = "formal"
        elif len(self._informal_markers) > len(self._formality_markers):
            formality_level = "informal"
        else:
            formality_level = "neutral"

        # Return top vocabulary items
        top_vocab = dict(self._vocabulary.most_common(50))

        return {
            "name": name,
            "vocabulary": top_vocab,
            "formality_level": formality_level,
            "sample_count": len(self._samples),
            "informal_markers": self._informal_markers,
            "formality_markers": self._formality_markers,
        }
