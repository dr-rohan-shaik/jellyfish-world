"""Git push helper for Jellyfish World."""
from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel


def run_gitpush(
    message: str | None,
    branch: str | None,
    remote: str,
    skip_confirmation: bool,
    console: Console,
) -> None:
    """Commit staged/approved changes and push to remote."""
    repo_root = Path.cwd()

    # Check git status
    try:
        res_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        console.print("[red]Error: Not in a git repository[/red]")
        return

    if res_status.returncode != 0 or not res_status.stdout.strip():
        console.print("[dim]No changes to commit. The waters are calm.[/dim]")
        return

    # Get current branch
    try:
        res_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        current_branch = res_branch.stdout.strip() if res_branch.returncode == 0 else "unknown"
    except Exception:
        current_branch = "unknown"

    # Check if there's a remote for this branch
    if not branch:
        branch = current_branch

    # Generate calm commit message if not provided
    if not message:
        now = datetime.now()
        mood = _get_current_mood()
        message = f"{mood} - Update from {now.strftime('%Y-%m-%d %H:%M')}"

    # Confirm before pushing
    if not skip_confirmation:
        changed_files = [
            line[3:].strip()
            for line in res_status.stdout.strip().split("\n")
            if line.strip()
        ]

        console.print(
            Panel(
                f"[bold]Ready to commit & push:[/bold]\n\n"
                f"[cyan]Branch:[/cyan] {branch}\n"
                f"[cyan]Message:[/cyan] {message}\n"
                f"[cyan]Files changed:[/cyan] {len(changed_files)}\n"
                f"[cyan]Remote:[/cyan] {remote}\n\n"
                f"[dim]The deep currents are ready. Proceed? (y/N)[/dim]",
                border_style="cyan",
            )
        )

        try:
            response = input("\n[bold cyan]> [/bold cyan]").strip().lower()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]The tide shifts. Cancelled.[/dim]")
            return

        if response not in ("y", "yes"):
            console.print("[dim]The waters hold steady. Cancelled.[/dim]")
            return

    # Stage all changes
    try:
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_root,
            check=True,
            timeout=10,
        )
    except Exception as e:
        console.print(f"[red]Error staging changes: {e}[/red]")
        return

    # Commit
    try:
        res_commit = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if res_commit.returncode != 0:
            if "nothing to commit" in res_commit.stdout.lower():
                console.print("[dim]Nothing to commit. The waters are still.[/dim]")
                return
            console.print(f"[yellow]Commit note: {res_commit.stdout.strip()}[/yellow]")

        console.print(f"[bold green]✓[/bold green] Committed: {message}")
    except Exception as e:
        console.print(f"[red]Error committing: {e}[/red]")
        return

    # Push
    try:
        res_push = subprocess.run(
            ["git", "push", "-u", remote, branch],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if res_push.returncode != 0:
            console.print(f"[red]✗ Push failed: {res_push.stderr}[/red]")
            return

        # Extract commit hash from push output
        commit_line = None
        for line in res_push.stdout.split("\n"):
            if "->" in line:
                commit_line = line.strip()
                break

        if commit_line:
            console.print(f"[bold green]✓[/bold green] {commit_line}")
        else:
            console.print(f"[bold green]✓[/bold green] Pushed to {remote}/{branch}")

    except Exception as e:
        console.print(f"[red]Error pushing: {e}[/red]")
        return


def _get_current_mood() -> str:
    import time

    hour = time.localtime().tm_hour
    if 5 <= hour < 12:
        return "Morning tide shift"
    elif 12 <= hour < 17:
        return "Midday update"
    elif 17 <= hour < 22:
        return "Dusk drift"
    else:
        return "Midnight current"


if __name__ == "__main__":
    # Simple CLI for testing
    import argparse

    parser = argparse.ArgumentParser(description="Git push helper")
    parser.add_argument("-m", "--message", help="Commit message")
    parser.add_argument("-b", "--branch", help="Branch to push")
    parser.add_argument("-r", "--remote", default="origin", help="Git remote")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    args = parser.parse_args()

    console = Console()
    run_gitpush(args.message, args.branch, args.remote, args.yes, console)
