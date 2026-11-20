"""CLI Manager for Universal Agent Bridge (`jelly connect` and `jelly disconnect`)."""
from __future__ import annotations

from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.bridge.auto_connect import (
    scan_agent_status,
    connect_all_agents,
    disconnect_all_agents,
    get_agent_config_targets,
    inject_mcp_into_json,
    remove_mcp_from_json,
    get_default_paths,
    generate_generic_runners,
)
from src.ui.palette import Palette


def show_bridge_status(console: Console) -> None:
    """Display connection status for all supported agents."""
    table = Table(title="Jellyfish World — Agent Bridge (MCP) Status", border_style=Palette.CYAN)
    table.add_column("Agent / Tool", style="bold")
    table.add_column("Config Target", style="dim")
    table.add_column("Status", justify="center")

    statuses = scan_agent_status()
    for s in statuses:
        agent_name = s["agent"].capitalize()
        path_str = str(s["path"]) if s["path"] else "(Not configured yet)"
        if s["connected"]:
            status_badge = "[bold green]CONNECTED[/bold green]"
        elif s["installed"]:
            status_badge = "[yellow]DETECTED (Ready to connect)[/yellow]"
        else:
            status_badge = "[dim]NOT FOUND[/dim]"

        table.add_row(agent_name, path_str, status_badge)

    # Universal runners for Hermes, OpenClaw, DeepSeek
    repo_root = Path(__file__).resolve().parent.parent.parent
    table.add_row(
        "OpenClaw / Hermes / DeepSeek",
        f"{repo_root / 'mcp_runner.bat'} (Universal Stdio)",
        "[bold cyan]AVAILABLE[/bold cyan]",
    )

    console.print(table)


def run_connect(console: Console, target: str = "all") -> None:
    """Connect jellyfish to target agent or all agents."""
    console.print(f"[bold cyan]Connecting Jellyfish World to '{target}' agents via MCP...[/bold cyan]\n")
    repo_root = Path(__file__).resolve().parent.parent.parent
    py_path, cli_path = get_default_paths()

    # Universal runners
    bat, sh = generate_generic_runners(repo_root, py_path, cli_path)
    console.print(f"[green]✓[/green] Universal runner scripts created for OpenClaw/Hermes/DeepSeek:")
    console.print(f"    - [dim]{bat}[/dim]\n    - [dim]{sh}[/dim]")

    if target.lower() == "all":
        reports = connect_all_agents(repo_root)
        for r in reports:
            agent = r["agent"].capitalize()
            if r["success"]:
                bak_info = f" (Backup: {r['backup'].name})" if r["backup"] else ""
                console.print(f"[green]✓[/green] [bold]{agent}[/bold] connected at: [dim]{r['path']}[/dim]{bak_info}")
            else:
                console.print(f"[yellow]![/yellow] {agent}: {r['message']}")
    else:
        targets = get_agent_config_targets()
        matched = targets.get(target.lower())
        if not matched:
            console.print(f"[red]Unknown agent '{target}'. Available: all, claude, cursor, opencode[/red]")
            return
        target_path = next((p for p in matched if p.exists()), matched[0])
        ok, msg, bak = inject_mcp_into_json(target_path, py_path, cli_path)
        if ok:
            console.print(f"[green]✓[/green] [bold]{target.capitalize()}[/bold] connected at: [dim]{target_path}[/dim]")
        else:
            console.print(f"[red]✗ Failed to connect {target}: {msg}[/red]")

    console.print("\n[bold green]All agents can now call your jellyfish directly via MCP tools![/bold green]")
    console.print("[dim]Tools exposed: hey_jellyfish, jellyfish_status, jellyfish_react, jellyfish_tap, jellyfish_decide[/dim]")


def run_disconnect(console: Console, target: str = "all") -> None:
    """Remove jellyfish MCP connection from agents."""
    console.print(f"[yellow]Disconnecting Jellyfish World from '{target}' agents...[/yellow]\n")
    if target.lower() == "all":
        reports = disconnect_all_agents()
        for r in reports:
            agent = r["agent"].capitalize()
            if r["success"]:
                console.print(f"[green]✓[/green] Disconnected from [bold]{agent}[/bold] ([dim]{r['path']}[/dim])")
            else:
                console.print(f"[dim]{agent}: {r['message']}[/dim]")
    else:
        targets = get_agent_config_targets()
        matched = targets.get(target.lower())
        if not matched:
            console.print(f"[red]Unknown agent '{target}'.[/red]")
            return
        for p in matched:
            if p.exists():
                ok, msg, _ = remove_mcp_from_json(p)
                if ok:
                    console.print(f"[green]✓[/green] Disconnected from [bold]{target.capitalize()}[/bold]")
                    return
        console.print(f"[dim]No active configuration found for {target}.[/dim]")
