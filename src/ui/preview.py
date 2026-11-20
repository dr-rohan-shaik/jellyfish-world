"""Design Preview Runner for Jellyfish World.

Showcases:
1. 4-frame breathing & vertical drift animation.
2. Layered cosmetics (crown, glasses, glow ring, combinations).
3. Bioluminescent mood glow shifts.
4. Founder gold glow (#00001) vs standard glow (#00047).
5. 40x20 and 80x24 terminal responsive layouts.
"""
from __future__ import annotations

import argparse
import shutil
import time
from typing import Any

# ruff: noqa: I001
# Bootstrap must be imported first to ensure project root is on sys.path
import src.bootstrap  # noqa: F401

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

from src.core.cosmetics import load_cosmetics_catalog
from src.ui.ascii_art import render_jellyfish_card
from src.ui.palette import Palette, get_theme


DemoConfig = dict[str, Any]


def run_preview(
    cycles: int = 0,
    interval: float = 0.25,
    force_compact: bool = False,
    founder_demo: bool = True,
) -> None:
    """Run interactive design preview."""
    console = Console(theme=get_theme())
    catalog = load_cosmetics_catalog()

    crown = catalog.get("crown")
    glasses = catalog.get("glasses")
    ring = catalog.get("glow_ring")

    # Sequence of demo configurations to rotate through
    demos: list[DemoConfig] = [
        {"name": "Aurelia", "num": 1, "founder": True, "mood": "calm", "items": [], "desc": "Bare Founder (#00001, Gold Glow)"},
        {"name": "Aurelia", "num": 1, "founder": True, "mood": "sparkle", "items": [crown] if crown else [], "desc": "Founder with Golden Crown"},
        {"name": "Corallia", "num": 47, "founder": False, "mood": "curious", "items": [glasses] if glasses else [], "desc": "Curious (#00047) with Round Glasses"},
        {"name": "Lumina", "num": 128, "founder": False, "mood": "sparkle", "items": [ring] if ring else [], "desc": "Sparkle with Bioluminescent Glow Ring"},
        {"name": "Solaria", "num": 7, "founder": True, "mood": "playful", "items": [crown, glasses, ring], "desc": "Founder with All Cosmetics Equipped"},
    ]

    total_frames = 4
    cycle_count = 0
    demo_idx = 0

    try:
        with Live(console=console, refresh_per_second=8, screen=False) as live:
            while True:
                for frame_idx in range(total_frames):
                    cols, rows = (40, 20) if force_compact else shutil.get_terminal_size((80, 24))
                    curr = demos[demo_idx]

                    speech = f"Softly drifting in the deep... [{curr['desc']}]"
                    card = render_jellyfish_card(
                        frame_idx=frame_idx,
                        name=str(curr["name"]),
                        number=int(curr["num"]),
                        mood=str(curr["mood"]),
                        is_founder=bool(curr["founder"]),
                        equipped=[i for i in curr["items"] if i is not None],
                        speech=speech,
                        hint="hey jellyfish how are you?",
                        terminal_width=cols,
                        terminal_height=rows,
                    )

                    header = Text("~ JELLYFISH WORLD — DESIGN PREVIEW ~", style=f"bold {Palette.CYAN}")
                    footer = Text(
                        f"Terminal Size: {cols}x{rows} | Frame: {frame_idx}/3 | Ctrl+C to stop",
                        style="dim",
                    )

                    layout = Layout()
                    layout.split_column(
                        Layout(Align.center(header), size=1),
                        Layout(Align.center(card)),
                        Layout(Align.center(footer), size=1),
                    )

                    live.update(layout)
                    time.sleep(interval)

                cycle_count += 1
                demo_idx = (demo_idx + 1) % len(demos)

                if cycles > 0 and cycle_count >= cycles:
                    break
    except KeyboardInterrupt:
        pass

    console.print("\n[bold cyan]Preview concluded peacefully.[/bold cyan]\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Jellyfish World Design Preview")
    parser.add_argument("--cycles", type=int, default=0, help="Number of animation cycles to run before exiting (0 = infinite)")
    parser.add_argument("--interval", type=float, default=0.25, help="Seconds per frame (default: 0.25)")
    parser.add_argument("--compact", action="store_true", help="Force 40x20 compact mobile viewport")
    parser.add_argument("--no-founder", action="store_true", help="Disable founder demo")
    args = parser.parse_args()

    run_preview(
        cycles=args.cycles,
        interval=args.interval,
        force_compact=args.compact,
        founder_demo=not args.no_founder,
    )


if __name__ == "__main__":
    main()
