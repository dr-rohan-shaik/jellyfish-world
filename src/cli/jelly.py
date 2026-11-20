#!/usr/bin/env python3
"""Main CLI for Jellyfish World (`jelly`).

Fast path:
- `jelly greet`: executes with minimal overhead (<50ms).
- `jelly mcp`: launches stdio JSON-RPC MCP server for Claude, Codex, OpenCode, Hermes, OpenClaw.
"""
from __future__ import annotations

import argparse
import os
import sys

from rich.console import Console

# Fast-path modules (lightweight, imported early for speed)
from src.autostart.greet import play_greeting

# Bootstrap must be imported first to ensure project root is on sys.path
from src.bridge.mcp_server import run_mcp_server
from src.ui.palette import get_theme


def main():
    # Fast path 1: `jelly greet`
    if len(sys.argv) > 1 and sys.argv[1] == "greet":
        force_flag = "--force" in sys.argv or "-f" in sys.argv
        autostart_flag = "--autostart" in sys.argv
        play_greeting(force=force_flag, is_autostart=autostart_flag)
        sys.exit(0)

    # Fast path 2: `jelly mcp` (stdio server for connected agents)
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        run_mcp_server()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        prog="jelly",
        description="Jellyfish World — Terminal Companion & Agent Bridge",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # greet command
    greet_p = subparsers.add_parser("greet", help="Play short greeting animation")
    greet_p.add_argument("--force", "-f", action="store_true", help="Bypass all startup guards")
    greet_p.add_argument("--autostart", action="store_true", help="Running via shell startup hook")

    # mcp command
    subparsers.add_parser("mcp", help="Run Model Context Protocol (MCP) stdio server")

    # connect command
    connect_p = subparsers.add_parser("connect", help="Connect jellyfish to external AI coding agents")
    connect_p.add_argument("target", nargs="?", default="all", choices=["all", "status", "claude", "cursor", "opencode"], help="Agent to connect")

    # disconnect command
    disconnect_p = subparsers.add_parser("disconnect", help="Disconnect jellyfish from external AI coding agents")
    disconnect_p.add_argument("target", nargs="?", default="all", choices=["all", "claude", "cursor", "opencode"], help="Agent to disconnect")

    # autostart command
    autostart_p = subparsers.add_parser("autostart", help="Manage terminal startup integration")
    autostart_p.add_argument("action", choices=["on", "off", "status"], help="Action to perform")
    autostart_p.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompts")

    # sidepane command
    sidepane_p = subparsers.add_parser("sidepane", help="Windows Terminal sidepane control")
    sidepane_p.add_argument("action", choices=["on", "off"], help="Open or close sidepane")

    # home preview
    home_p = subparsers.add_parser("home", help="Open live floating jellyfish view")
    home_p.add_argument("--cycles", type=int, default=0, help="Cycles to run (0 = infinite)")
    home_p.add_argument("--silent", "-s", action="store_true", help="Run silently without interactive prompts")

    # gitpush command
    gitpush_p = subparsers.add_parser("gitpush", help="Commit and push changes with a calm message")
    gitpush_p.add_argument("-m", "--message", type=str, help="Commit message (optional, will generate one if not provided)")
    gitpush_p.add_argument("-b", "--branch", type=str, help="Branch to push to (default: auto-detect)")
    gitpush_p.add_argument("--remote", type=str, default="origin", help="Git remote name (default: origin)")
    gitpush_p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompts")

    args = parser.parse_args()
    console = Console(theme=get_theme())

    if args.command == "greet":
        play_greeting(force=args.force, is_autostart=args.autostart)

    elif args.command == "mcp":
        run_mcp_server()

    elif args.command == "connect":
        from src.bridge.manager import run_connect, show_bridge_status
        if args.target == "status":
            show_bridge_status(console)
        else:
            run_connect(console, target=args.target)

    elif args.command == "disconnect":
        from src.bridge.manager import run_disconnect
        run_disconnect(console, target=args.target)

    elif args.command == "autostart":
        from src.autostart.manager import disable_autostart, enable_autostart, show_status
        if args.action == "status":
            show_status(console)
        elif args.action == "on":
            enable_autostart(console, assume_yes=args.yes)
        elif args.action == "off":
            disable_autostart(console, assume_yes=args.yes)

    elif args.command == "sidepane":
        from src.autostart.sidepane import close_sidepane_instruction, open_sidepane
        if args.action == "on":
            py_path = sys.executable
            cli_path = os.path.abspath(__file__)
            ok, msg = open_sidepane(py_path, cli_path)
            if ok:
                console.print(f"[bold green]✓[/bold green] {msg}")
            else:
                console.print(f"[bold red]✗[/bold red] {msg}")
        elif args.action == "off":
            console.print(f"[dim]{close_sidepane_instruction()}[/dim]")

    elif args.command == "home":
        from src.ui.preview import run_preview
        run_preview(cycles=args.cycles, interactive=not(args.silent))

    elif args.command == "gitpush":
        from src.cli.gitpush import run_gitpush
        run_gitpush(
            message=args.message,
            branch=args.branch,
            remote=args.remote,
            skip_confirmation=args.yes,
            console=console,
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
