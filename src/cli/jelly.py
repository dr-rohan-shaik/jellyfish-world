#!/usr/bin/env python3
"""Main CLI for Jellyfish World (`jelly`).

Fast path:
- `jelly greet`: executes with minimal overhead (<50ms).
- `jelly mcp`: launches stdio JSON-RPC MCP server for Claude, Codex, OpenCode, Hermes, OpenClaw.
"""
import sys
import os

# Ensure src is on sys.path
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

# Fast path 1: `jelly greet`
if len(sys.argv) > 1 and sys.argv[1] == "greet":
    from src.autostart.greet import play_greeting
    force_flag = "--force" in sys.argv or "-f" in sys.argv
    autostart_flag = "--autostart" in sys.argv
    play_greeting(force=force_flag, is_autostart=autostart_flag)
    sys.exit(0)

# Fast path 2: `jelly mcp` (stdio server for connected agents)
if len(sys.argv) > 1 and sys.argv[1] == "mcp":
    from src.bridge.mcp_server import run_mcp_server
    run_mcp_server()
    sys.exit(0)

# Full CLI imports for management commands
import argparse
from rich.console import Console
from src.ui.palette import get_theme


def main():
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

    args = parser.parse_args()
    console = Console(theme=get_theme())

    if args.command == "greet":
        from src.autostart.greet import play_greeting
        play_greeting(force=args.force, is_autostart=args.autostart)

    elif args.command == "mcp":
        from src.bridge.mcp_server import run_mcp_server
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
        from src.autostart.manager import show_status, enable_autostart, disable_autostart
        if args.action == "status":
            show_status(console)
        elif args.action == "on":
            enable_autostart(console, assume_yes=args.yes)
        elif args.action == "off":
            disable_autostart(console, assume_yes=args.yes)

    elif args.command == "sidepane":
        from src.autostart.sidepane import open_sidepane, close_sidepane_instruction
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
        run_preview(cycles=args.cycles)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
