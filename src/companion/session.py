"""Interactive Companion Session for Jellyfish World.

Entry point when user runs `jellyfish`.
Provides floating jellyfish, live in-terminal chat, Agent Watcher, and work options.
"""
from __future__ import annotations

import os
import shutil
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
_repo_root = str(Path(__file__).resolve().parent.parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

from src.core.cosmetics import load_cosmetics_catalog
from src.ui.ascii_art import render_jellyfish_card
from src.ui.palette import Palette, get_theme
from src.companion.agent_watcher import render_agent_watcher_table, record_agent_event
from src.companion.work_context import generate_work_options
from src.companion.chat import respond_to_owner
from src.bridge.mcp_server import STATE


def run_companion_session():
    """Run interactive terminal companion loop."""
    console = Console(theme=get_theme())
    catalog = load_cosmetics_catalog()
    crown = catalog.get("crown")

    frame_idx = 0
    speech_msg = "I am drifting quietly beside you. How can I help with your flow?"

    while True:
        cols, rows = shutil.get_terminal_size((80, 24))

        # Render floating jellyfish card
        card = render_jellyfish_card(
            frame_idx=frame_idx,
            name=STATE["name"],
            number=STATE["number"],
            mood=STATE["mood"],
            is_founder=STATE["is_founder"],
            equipped=[crown] if crown else [],
            speech=speech_msg,
            hint="type a command or option number below",
            terminal_width=cols,
            terminal_height=rows,
        )

        console.clear()
        console.print(card)

        # Options Menu
        console.print(Panel(
            f"[bold {Palette.CYAN}][1][/] 💬 Chat with {STATE['name']} (`hey jellyfish <message>`)\n"
            f"[bold {Palette.CYAN}][2][/] 🔭 Watch Other Agents (Live Claude Code, OpenCode, Hermes feed)\n"
            f"[bold {Palette.CYAN}][3][/] 🎯 Work Options & Decisions (Calm choices for current tasks)\n"
            f"[bold {Palette.CYAN}][4][/] ✨ Feed Light (Daily Tap)\n"
            f"[bold {Palette.CYAN}][5][/] 🪟 Dock to Sidepane (Float beside your editor)\n"
            f"[bold {Palette.CYAN}][q][/] 🌊 Return peacefully to shell",
            title="Calm Companion Menu",
            border_style=Palette.MID_BLUE,
            width=min(cols - 2, 52),
        ))

        try:
            choice = input("\nJellyfish > ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Aurelia drifts gently back into the ocean depths. See you soon![/dim]\n")
            break

        if not choice:
            frame_idx = (frame_idx + 1) % 4
            continue

        if choice.lower() in ("q", "quit", "exit"):
            console.print("\n[dim]Aurelia drifts gently back into the ocean depths. See you soon![/dim]\n")
            break

        # 1. Chat
        elif choice == "1" or choice.lower().startswith("hey"):
            msg = choice if choice.lower().startswith("hey") else input("Your message: ").strip()
            if msg:
                reply = respond_to_owner(msg, STATE["name"], STATE["mood"])
                speech_msg = reply
                # Animate a little
                frame_idx = (frame_idx + 1) % 4

        # 2. Watch Other Agents
        elif choice == "2":
            table = render_agent_watcher_table()
            console.clear()
            console.print(table)
            console.print("\n[dim]External agents (Claude Code, OpenCode, Hermes, DeepSeek) report here via MCP.[/dim]")
            input("\nPress Enter to return...")

        # 3. Work Options & Decisions
        elif choice == "3":
            options = generate_work_options()
            console.clear()
            console.print(Panel(
                f"[bold {Palette.GOLD}]Calm Guidance for Current Work:[/bold {Palette.GOLD}]\n\n" +
                "\n".join([f"[bold cyan]{o['letter']}.[/bold cyan] [bold]{o['title']}:[/bold] {o['desc']}" for o in options]),
                title="Current Work Options",
                border_style=Palette.CYAN,
            ))
            opt_pick = input("\nChoose an option (A/B/C or Enter to return): ").strip().upper()
            if opt_pick == "A":
                speech_msg = "Focus softly on your code flow. Steady currents carry great work."
            elif opt_pick == "B":
                # Cycle mood
                moods = ["calm", "sparkle", "curious", "playful"]
                next_mood = moods[(moods.index(STATE["mood"]) + 1) % len(moods)]
                STATE["mood"] = next_mood
                speech_msg = f"My bioluminescent glow shifted to {next_mood}."
            elif opt_pick == "C":
                speech_msg = "Taking a gentle breather... relax your shoulders and gaze at the sea."

        # 4. Feed Light (Tap)
        elif choice == "4":
            STATE["tap_count"] += 1
            STATE["mood"] = "sparkle"
            speech_msg = f"Thank you for feeding me light! Total taps: {STATE['tap_count']} ✨"

        # 5. Dock to Sidepane
        elif choice == "5":
            from src.autostart.sidepane import open_sidepane
            py_path = sys.executable
            cli_path = str(Path(_repo_root) / "src" / "cli" / "jelly.py")
            ok, msg = open_sidepane(py_path, cli_path)
            if ok:
                speech_msg = "I've floated over into your Windows Terminal sidepane!"
            else:
                speech_msg = f"Could not spawn sidepane: {msg}"

        else:
            # Treat direct text as a chat message
            reply = respond_to_owner(choice, STATE["name"], STATE["mood"])
            speech_msg = reply
            frame_idx = (frame_idx + 1) % 4


if __name__ == "__main__":
    run_companion_session()
