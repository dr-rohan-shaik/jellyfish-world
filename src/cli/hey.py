#!/usr/bin/env python3
"""Tiny `hey` CLI command for Jellyfish World.

Requires the word `jellyfish`:
    hey jellyfish <message>
"""
import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
_repo_root = str(Path(__file__).resolve().parent.parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from rich.console import Console
from src.ui.palette import Palette, get_theme
from src.companion.chat import respond_to_owner
from src.bridge.mcp_server import STATE


def main():
    console = Console(theme=get_theme())
    args = sys.argv[1:]

    if not args:
        console.print(f"[dim]To call your jellyfish companion, type:[/dim] [bold {Palette.CYAN}]hey jellyfish <message>[/]")
        return

    full_text = " ".join(args).strip()

    # Rule: Must require the word "jellyfish"
    if "jellyfish" not in full_text.lower():
        console.print(f"[dim]The ocean remains quiet... The call requires the word 'jellyfish'.[/dim]")
        console.print(f"[dim]Try:[/dim] [bold {Palette.CYAN}]hey jellyfish {full_text}[/]")
        return

    # Strip out the invocation keyword "jellyfish"
    words = full_text.split()
    msg_words = [w for w in words if w.lower() != "jellyfish"]
    message = " ".join(msg_words).strip() or "hello"

    # Generate in-character reply
    reply = respond_to_owner(message, STATE["name"], STATE["mood"])
    founder_tag = f" [bold {Palette.GOLD}](#00001 ★ FOUNDER)[/]" if STATE["is_founder"] else f" [dim](#00001)[/]"

    console.print(f"\n[bold {Palette.ELECTRIC_CYAN}]{STATE['name']}[/]{founder_tag}: [italic {Palette.WHITE}]{reply.replace(STATE['name'] + ': ', '')}[/]\n")


if __name__ == "__main__":
    main()
