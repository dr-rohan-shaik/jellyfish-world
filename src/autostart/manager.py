"""Autostart manager orchestrating PowerShell and CMD configurations.

Implements:
- jelly autostart status
- jelly autostart on [--yes]
- jelly autostart off [--yes]
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.autostart.powershell import (
    locate_active_profile,
    has_jellyfish_block,
    generate_powershell_block,
    apply_powershell_autostart,
    remove_powershell_autostart,
)
from src.autostart.cmd_autorun import (
    get_current_autorun,
    generate_cmd_hook,
    append_to_autorun,
    set_cmd_autorun,
    remove_cmd_autorun,
    HOOK_IDENTIFIER,
)
from src.ui.palette import get_theme, Palette


def get_default_paths() -> Tuple[str, str]:
    """Get paths to current venv python and jelly CLI entry point."""
    py_path = sys.executable
    repo_root = Path(__file__).resolve().parent.parent.parent
    cli_path = str(repo_root / "src" / "cli" / "jelly.py")
    return py_path, cli_path


def show_status(console: Console) -> None:
    """Display autostart status for PowerShell and CMD."""
    table = Table(title="Jellyfish World — Terminal Autostart Status", border_style=Palette.CYAN)
    table.add_column("Shell", style="bold")
    table.add_column("Target Location", style="dim")
    table.add_column("Status", justify="center")

    # PowerShell status
    ps_profile = locate_active_profile()
    ps_active = False
    if ps_profile.exists():
        content = ps_profile.read_text(encoding="utf-8")
        ps_active = has_jellyfish_block(content)

    ps_status = "[bold green]ENABLED[/bold green]" if ps_active else "[dim red]DISABLED[/dim red]"
    table.add_row("PowerShell", str(ps_profile), ps_status)

    # CMD status
    cmd_val = get_current_autorun()
    cmd_active = bool(cmd_val and HOOK_IDENTIFIER in cmd_val)
    cmd_status = "[bold green]ENABLED[/bold green]" if cmd_active else "[dim red]DISABLED[/dim red]"
    table.add_row("Command Prompt", "HKCU\\Software\\Microsoft\\Command Processor\\AutoRun", cmd_status)

    console.print(table)
    if cmd_val and not cmd_active:
        console.print(f"[dim]Existing CMD AutoRun: {cmd_val}[/dim]")


def enable_autostart(console: Console, assume_yes: bool = False) -> bool:
    """Enable terminal autostart for PowerShell and CMD after confirmation."""
    py_path, cli_path = get_default_paths()
    ps_profile = locate_active_profile()
    ps_block = generate_powershell_block(py_path, cli_path)

    cmd_prev = get_current_autorun()
    cmd_hook = generate_cmd_hook(py_path, cli_path)
    cmd_new = append_to_autorun(cmd_prev, cmd_hook)

    # Print planned changes
    console.print(Panel(
        f"[bold cyan]Planned Changes for Terminal Autostart:[/bold cyan]\n\n"
        f"[bold]1. PowerShell Profile:[/bold] {ps_profile}\n"
        f"[dim]Will create a timestamped backup copy before modifying.[/dim]\n"
        f"Block to insert:\n[green]{ps_block.strip()}[/green]\n\n"
        f"[bold]2. Command Prompt (HKCU only):[/bold]\n"
        f"Registry Value: HKCU\\Software\\Microsoft\\Command Processor\\AutoRun\n"
        f"Previous Value: {cmd_prev or '(none)'}\n"
        f"New Value:      [green]{cmd_new}[/green]",
        title="Autostart Confirmation Preview",
        border_style=Palette.GOLD,
    ))

    if not assume_yes:
        confirm = input("\nDo you want to apply these changes? (type 'yes' to confirm): ").strip().lower()
        if confirm != "yes":
            console.print("[yellow]Operation cancelled by user. No files or registry keys were modified.[/yellow]")
            return False

    # Apply PowerShell
    success_ps, _, bak_ps = apply_powershell_autostart(ps_profile, py_path, cli_path)
    if success_ps:
        console.print(f"[green]✓[/green] PowerShell profile updated. Backup saved to: [dim]{bak_ps}[/dim]")
    else:
        console.print(f"[red]✗[/red] Failed to update PowerShell profile.")

    # Apply CMD
    success_cmd, _, _ = set_cmd_autorun(py_path, cli_path)
    if success_cmd:
        console.print(f"[green]✓[/green] Command Prompt AutoRun registry updated in HKCU.")
    else:
        console.print(f"[red]✗[/red] Failed to update CMD registry.")

    console.print("\n[bold cyan]Terminal autostart enabled successfully![/bold cyan]")
    return True


def disable_autostart(console: Console, assume_yes: bool = False) -> bool:
    """Disable terminal autostart for PowerShell and CMD after confirmation."""
    ps_profile = locate_active_profile()
    cmd_prev = get_current_autorun()

    console.print(Panel(
        f"[bold cyan]Planned Removal of Terminal Autostart:[/bold cyan]\n\n"
        f"[bold]1. PowerShell Profile:[/bold] {ps_profile}\n"
        f"Will remove block between '# >>> jellyfish' and '# <<< jellyfish'.\n"
        f"A timestamped backup copy will be created.\n\n"
        f"[bold]2. Command Prompt Registry:[/bold]\n"
        f"Will strip jellyfish hook from HKCU\\Software\\Microsoft\\Command Processor\\AutoRun.",
        title="Autostart Removal Preview",
        border_style=Palette.GOLD,
    ))

    if not assume_yes:
        confirm = input("\nDo you want to proceed with removal? (type 'yes' to confirm): ").strip().lower()
        if confirm != "yes":
            console.print("[yellow]Operation cancelled by user. No changes made.[/yellow]")
            return False

    # Remove PowerShell
    if ps_profile.exists():
        success_ps, _, bak_ps = remove_powershell_autostart(ps_profile)
        if success_ps:
            console.print(f"[green]✓[/green] Removed jellyfish block from PowerShell profile. Backup: [dim]{bak_ps}[/dim]")
        else:
            console.print(f"[dim]PowerShell profile had no active jellyfish block.[/dim]")

    # Remove CMD
    success_cmd, new_cmd, _ = remove_cmd_autorun()
    if success_cmd:
        console.print(f"[green]✓[/green] Removed jellyfish hook from CMD AutoRun in HKCU.")
    else:
        console.print(f"[dim]Command Prompt AutoRun had no active jellyfish hook.[/dim]")

    console.print("\n[bold cyan]Terminal autostart disabled.[/bold cyan]")
    return True
