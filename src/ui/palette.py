"""Palette and styling definitions for Jellyfish World.

Supports:
- Deep-sea navy, bioluminescent pink, bioluminescent cyan, founder gold.
- Dynamic mood glow colors.
- Automatic NO_COLOR and REDUCED_MOTION environment detection.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from rich.style import Style
from rich.theme import Theme


def is_no_color() -> bool:
    """Return True if NO_COLOR environment variable is active."""
    val = os.environ.get("NO_COLOR", "")
    return bool(val and val.lower() not in ("0", "false", "no"))


def is_reduced_motion() -> bool:
    """Return True if REDUCED_MOTION is requested."""
    val = os.environ.get("REDUCED_MOTION", "")
    return val.lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Palette:
    """Core color palette constants."""
    # Deep ocean colors
    NAVY: str = "#0b132b"
    DEEP_BLUE: str = "#1c2541"
    MID_BLUE: str = "#3a506b"

    # Bioluminescent highlights
    CYAN: str = "#5bc0be"
    ELECTRIC_CYAN: str = "#6fffe9"
    PINK: str = "#ff70a6"
    ROSE: str = "#ff97b7"
    PURPLE: str = "#c77dff"

    # Founders & Special
    GOLD: str = "#ffd166"
    WHITE: str = "#f0f8ff"
    DIM: str = "#6c757d"


# Mood to glow color mapping
MOOD_COLORS = {
    "calm": Palette.CYAN,
    "curious": Palette.ROSE,
    "sparkle": Palette.PINK,
    "playful": Palette.GOLD,
    "dreaming": Palette.PURPLE,
    "soft": Palette.ELECTRIC_CYAN,
}


def get_mood_color(mood: str) -> str:
    """Return hex color for a given mood."""
    if is_no_color():
        return ""
    return MOOD_COLORS.get(mood.lower(), Palette.CYAN)


def get_theme() -> Theme:
    """Construct Rich Theme matching Jellyfish World palette."""
    if is_no_color():
        return Theme({
            "jelly.glow": Style(),
            "jelly.body": Style(),
            "jelly.founder": Style(bold=True),
            "jelly.accessory": Style(),
            "jelly.speech": Style(),
            "jelly.hint": Style(dim=True),
            "jelly.water": Style(dim=True),
        })

    return Theme({
        "jelly.glow": Style(color=Palette.CYAN),
        "jelly.body": Style(color=Palette.ELECTRIC_CYAN, bold=True),
        "jelly.founder": Style(color=Palette.GOLD, bold=True),
        "jelly.accessory": Style(color=Palette.GOLD),
        "jelly.speech": Style(color=Palette.WHITE, italic=True),
        "jelly.hint": Style(color=Palette.DIM),
        "jelly.water": Style(color=Palette.MID_BLUE),
        "jelly.pink": Style(color=Palette.PINK),
        "jelly.gold": Style(color=Palette.GOLD, bold=True),
    })
