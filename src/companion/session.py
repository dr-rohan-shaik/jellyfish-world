"""Interactive Companion Session and Direct Chat CLI for Jellyfish World.

Usage:
    jellyfish                     -> Launches interactive floating companion dashboard
    jellyfish <message>           -> Direct in-character answer right in the terminal
"""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from src.bootstrap import ensure_project_root_on_path
from src.bridge.mcp_server import STATE
from src.companion.agent_watcher import render_agent_watcher_table
from src.companion.chat import respond_to_owner
from src.companion.work_context import generate_work_options
from src.core.cosmetics import load_cosmetics_catalog
from src.ui.ascii_art import render_jellyfish_card
from src.ui.palette import Palette, get_theme

ensure_project_root_on_path()


def handle_direct_message(args: list[str]) -> None:
    """Handle one-shot `jellyfish <message>` call directly in the shell."""
    raw_msg = " ".join(args).strip()
    words = raw_msg.split()

    # Strip redundant leading 'hey' or 'jellyfish' if present
    if words and words[0].lower() == "hey":
        words = words[1:]
    if words and words[0].lower() == "jellyfish":
        words = words[1:]

    clean_msg = " ".join(words).strip() or "hello"

    console = Console(theme=get_theme())
    reply = respond_to_owner(clean_msg, STATE["name"], STATE["mood"])
    founder_tag = f" [bold {Palette.GOLD}](#00001 ★ FOUNDER)[/]" if STATE["is_founder"] else " [dim](#00001)[/]"

    console.print(f"\n[bold {Palette.ELECTRIC_CYAN}]{STATE['name']}[/]{founder_tag}: [italic {Palette.WHITE}]{reply.replace(STATE['name'] + ': ', '')}[/]\n")


def chat_loop(console: Console, jelly_name: str, mood: str) -> None:
    """Interactive continuous chat mode."""
    console.print(Panel(
        f"[bold {Palette.CYAN}]💬 Whispering to {jelly_name}...[/bold {Palette.CYAN}]\n"
        f"[dim]Type your message and press Enter. Type 'back' or press Enter on empty line to return to menu.[/dim]",
        border_style=Palette.CYAN,
    ))

    while True:
        try:
            msg = input("\nYou > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not msg or msg.lower() in ("back", "exit", "menu", "q"):
            break

        reply = respond_to_owner(msg, jelly_name, mood)
        founder_tag = f" [bold {Palette.GOLD}](#00001 ★ FOUNDER)[/]" if STATE["is_founder"] else ""
        console.print(f"[bold {Palette.ELECTRIC_CYAN}]{jelly_name}[/]{founder_tag}: [italic {Palette.WHITE}]{reply.replace(jelly_name + ': ', '')}[/]")


def run_companion_session() -> None:
    """Run interactive terminal companion loop."""
    # Force UTF-8 for emoji support on Windows
    console = Console(theme=get_theme(), encoding="utf-8")
    catalog = load_cosmetics_catalog()
    crown = catalog.get("crown")

    frame_idx = 0
    speech_msg = "I am drifting quietly beside you. How can I help with your flow?"

    # Get repo root for cli_path
    repo_root = Path(__file__).resolve().parent.parent.parent

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
            hint="jellyfish <message> | type 1 to chat, 2 to watch agents",
            terminal_width=cols,
            terminal_height=rows,
        )

        console.print(card)

        # Display Agent Watcher Table above the menu
        console.print(render_agent_watcher_table())

        # Clear the option for watching agents in the menu
        menu_options = (
            f"[bold {Palette.CYAN}][1][/] 💬 Chat with {STATE['name']} (Interactive chat mode)\n"
            f"[bold {Palette.CYAN}][2][/] [dim]🔭 Watch Other Agents (Live Claude Code, OpenCode, Hermes feed)[/dim] (Displayed above)\n"
            f"[bold {Palette.CYAN}][3][/] 🎯 Work Options & Decisions (Calm choices for current tasks)\n"
            f"[bold {Palette.CYAN}][4][/] ✨ Feed Light (Daily Tap)\n"
            f"[bold {Palette.CYAN}][5][/] 🪟 Dock to Sidepane (Float beside your editor)\n"
            f"[bold {Palette.CYAN}][q][/] 🌊 Return peacefully to shell"
        )
        console.print(Panel(
            menu_options,
            title="Calm Companion Menu",
            border_style=Palette.MID_BLUE,
            width=min(cols - 2, 56),
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

        # 1. Chat Mode
        elif choice == "1":
            chat_loop(console, STATE["name"], STATE["mood"])


        # 3. Work Options & Decisions
        elif choice == "3":
            options = generate_work_options()
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
            console.print(f"\n[bold {Palette.PINK}]✨ You fed light to {STATE['name']}. Its bell glows warm pink! (Total taps: {STATE['tap_count']})[/]\n")
            speech_msg = f"Thank you for feeding me light! Total taps: {STATE['tap_count']} ✨"
            time.sleep(1.2)

        # 5. Dock to Sidepane
        elif choice == "5":
            from src.autostart.sidepane import open_sidepane
            py_path = sys.executable
            cli_path = str(repo_root / "src" / "cli" / "jelly.py")
            ok, msg = open_sidepane(py_path, cli_path)
            if ok:
                speech_msg = "I've floated over into your Windows Terminal sidepane!"
                console.print("[green]✓ Opened sidepane.[/green]")
            else:
                speech_msg = f"Could not spawn sidepane: {msg}"
                console.print(f"[red]✗ {msg}[/red]")
            time.sleep(1.0)

        else:
            # Direct chat input right from menu
            reply = respond_to_owner(choice, STATE["name"], STATE["mood"])
            founder_tag = f" [bold {Palette.GOLD}](#00001 ★ FOUNDER)[/]" if STATE["is_founder"] else ""
            console.print(f"\n[bold {Palette.ELECTRIC_CYAN}]{STATE['name']}[/]{founder_tag}: [italic {Palette.WHITE}]{reply.replace(STATE['name'] + ': ', '')}[/]\n")
            speech_msg = reply
            frame_idx = (frame_idx + 1) % 4
            input("Press Enter to continue...")


def main() -> None:
    """Main entry point for the jellyfish command."""
    if len(sys.argv) > 1:
        handle_direct_message(sys.argv[1:])
    else:
        run_companion_session()


if __name__ == "__main__":
    main()
