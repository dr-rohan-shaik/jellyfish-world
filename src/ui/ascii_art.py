"""ASCII Animation and Art Engine for Jellyfish World.

Implements:
- 4-frame breathing & swaying animation loop with vertical drift.
- Layered cosmetic compositing (hats, round glasses, glow ring).
- Bioluminescent mood glow coloring.
- Founders gold glow.
- Responsive scaling for 40x20 Termux up to 80x24 desktop terminals.
"""
from __future__ import annotations

from rich.align import Align
from rich.box import DOUBLE, ROUNDED
from rich.panel import Panel
from rich.text import Text

from src.core.cosmetics import CosmeticItem, apply_cosmetics_to_frame
from src.ui.palette import Palette, get_mood_color, is_no_color, is_reduced_motion

# Animation constants
FRAME_WIDTH = 21
FRAME_HEIGHT = 7
MAX_DRIFT = 2
TOTAL_FRAMES = 4

# 4 distinct animation frames (Width: 21 chars centered)
RAW_FRAMES: list[tuple[int, list[str]]] = [
    # Frame 0: Bell contracted, float at highest point (drift offset = 0)
    (
        0,
        [
            "     .-~~~-.     ",
            "    /  o o  \\    ",
            "   (   ‿‿    )   ",
            "    '-.___.-'    ",
            "     ) | | (     ",
            "     ( | | )     ",
            "      ) | (      ",
        ],
    ),
    # Frame 1: Bell expanding, drifting down (drift offset = 1)
    (
        1,
        [
            "   .---~~~---.   ",
            "  /   o   o   \\  ",
            " (     ‿‿      ) ",
            "  '--._____.-'   ",
            "    (  | |  )    ",
            "     ) | | (     ",
            "     ( | | )     ",
        ],
    ),
    # Frame 2: Bell fully expanded, lowest float point (drift offset = 2)
    (
        2,
        [
            "  .----~~~----.  ",
            " /    o   o    \\ ",
            "(      ‿‿      ) ",
            " '---._____.-'   ",
            "     | | | |     ",
            "    (  | |  )    ",
            "     ) | | (     ",
        ],
    ),
    # Frame 3: Bell relaxing, rising back up (drift offset = 1)
    (
        1,
        [
            "   .---~~~---.   ",
            "  /   o   o   \\  ",
            " (     ‿‿      ) ",
            "  '--._____.-'   ",
            "    )  | |  (    ",
            "   (   | |   )   ",
            "     |  |  |     ",
        ],
    ),
]


def get_animated_frame(
    frame_idx: int,
    equipped: list[CosmeticItem] | None = None,
    mood: str = "calm",
    is_founder: bool = False,
    include_drift: bool = True,
) -> Text:
    """Produce a styled Rich Text object for a given animation frame.

    Args:
        frame_idx: 0 to 3
        equipped: active cosmetics list
        mood: temporary mood ('calm', 'sparkle', 'curious', etc.)
        is_founder: whether to display golden founders glow
        include_drift: whether to apply vertical padding drift

    Returns:
        Rich Text instance ready for console rendering.
    """
    if is_reduced_motion():
        frame_idx = 0
        include_drift = False

    actual_idx = frame_idx % len(RAW_FRAMES)
    drift_offset, base_lines = RAW_FRAMES[actual_idx]

    # Composite cosmetics
    composited_lines = apply_cosmetics_to_frame(
        frame_lines=base_lines,
        equipped_items=equipped or [],
        target_width=FRAME_WIDTH,
    )

    # Vertical drift padding (0, 1, or 2 blank lines at top, remaining at bottom)
    top_pad = drift_offset if include_drift else 1
    bottom_pad = (MAX_DRIFT - top_pad) if include_drift else 1

    all_lines = ([" " * FRAME_WIDTH] * top_pad) + composited_lines + ([" " * FRAME_WIDTH] * bottom_pad)

    # Build styled text
    mood_color = get_mood_color(mood)
    accent_color = Palette.GOLD if is_founder else mood_color
    body_color = Palette.ELECTRIC_CYAN

    result = Text()
    for line in all_lines:
        line_text = Text(line)
        if not is_no_color():
            # Apply styling to special parts
            if is_founder and ("\\_v_v_/" in line or "GOLD" in line):
                line_text.stylize(f"bold {Palette.GOLD}")
            elif "\\_v_v_/" in line:
                line_text.stylize(f"bold {Palette.GOLD}")
            elif "(o)" in line:
                line_text.stylize(f"bold {Palette.WHITE}")
            elif ":·*" in line or "*·:" in line:
                line_text.stylize(f"bold {accent_color}")
            elif "‿‿" in line:
                line_text.stylize(f"bold {Palette.PINK}")
            else:
                line_text.stylize(f"{body_color}")
        result.append_text(line_text)
        result.append("\n")

    return result


def render_jellyfish_card(
    frame_idx: int,
    name: str = "Aurelia",
    number: int = 1,
    mood: str = "calm",
    is_founder: bool = False,
    equipped: list[CosmeticItem] | None = None,
    speech: str | None = None,
    hint: str = "jellyfish <message>",
    terminal_width: int = 80,
    terminal_height: int = 24,
) -> Panel:
    """Render the full home view card containing the jellyfish, headers, speech, and hint."""
    num_str = f"#{number:05d}"
    founder_badge = " ★ FOUNDER" if is_founder else ""
    title_str = f"[bold {Palette.GOLD}]{name} {num_str}{founder_badge}[/]" if is_founder else f"[bold {Palette.ELECTRIC_CYAN}]{name}[/] [dim]{num_str}[/]"

    jelly_text = get_animated_frame(
        frame_idx=frame_idx,
        equipped=equipped,
        mood=mood,
        is_founder=is_founder,
    )

    content = Text()
    content.append_text(jelly_text)

    # Speech line if present
    if speech:
        content.append("\n")
        speech_text = Text(f'"{speech}"', style=f"italic {Palette.WHITE}")
        content.append_text(speech_text)
        content.append("\n")

    # Hint line
    if hint:
        content.append("\n")
        hint_text = Text(hint, style=f"dim {Palette.MID_BLUE}")
        content.append_text(hint_text)

    # Border style follows founder or mood
    border_style = Palette.GOLD if is_founder else get_mood_color(mood)

    # Adapt panel width for compact screens (40x20 minimum)
    panel_width = min(terminal_width - 2, 46) if terminal_width < 60 else 52

    return Panel(
        Align.center(content),
        title=title_str,
        subtitle=f"[dim]mood: {mood}[/dim]",
        border_style=border_style,
        box=DOUBLE if is_founder else ROUNDED,
        width=panel_width,
    )
