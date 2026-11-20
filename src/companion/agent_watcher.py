"""Agent Watcher module for Jellyfish World.

Monitors real-time activity and events from connected AI agents:
- Claude Code
- OpenCode / Codex
- Hermes / OpenClaw
- DeepSeek harnesses
- Cursor / Windsurf

Tracks what agents are doing and reflects their progress in the jellyfish's mood.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

from rich.table import Table

from src.ui.palette import Palette

# Module-level variable for test override
_activity_log_path_override: Path | None = None


def set_activity_log_path_override(path: Path | None) -> None:
    """Override the activity log path for testing purposes."""
    global _activity_log_path_override
    _activity_log_path_override = path


def get_activity_log_path() -> Path:
    """Return path to local agent activity buffer."""
    if _activity_log_path_override is not None:
        return _activity_log_path_override
    repo_root = Path(__file__).resolve().parent.parent.parent
    data_dir = repo_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "agent_activity.json"


def record_agent_event(agent_name: str, event_text: str, mood: str = "calm") -> None:
    """Record a new event from an external AI agent."""
    log_path = get_activity_log_path()
    events: list[dict[str, Any]] = []

    if log_path.exists():
        try:
            with open(log_path, encoding="utf-8") as f:
                events = json.load(f)
        except Exception:
            events = []

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    new_entry = {
        "time": timestamp,
        "agent": agent_name,
        "event": event_text,
        "mood": mood,
    }
    events.insert(0, new_entry)
    # Keep last 30 events
    events = events[:30]

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)


def get_recent_agent_events() -> list[dict[str, Any]]:
    """Return list of recent agent activities."""
    log_path = get_activity_log_path()
    if not log_path.exists():
        # Return empty list - no fake seed events
        return []
    try:
        with open(log_path, encoding="utf-8") as f:
            data = json.load(f)
            return data if data else []
    except Exception:
        return []


def render_agent_watcher_table() -> Table:
    """Render a Rich Table summarizing external agent activity."""
    table = Table(
        title="🔭 Agent Watcher — Live Observer Feed",
        border_style=Palette.CYAN,
        header_style="bold " + Palette.CYAN,
    )
    table.add_column("Time", style="dim", width=10)
    table.add_column("Agent", style="bold " + Palette.GOLD, width=15)
    table.add_column("Current Work / Task", style=Palette.WHITE)
    table.add_column("Glow Reaction", justify="center", width=15)

    events = get_recent_agent_events()
    if not events:
        table.add_row(
            "—",
            "[dim]No agents connected[/dim]",
            "[dim]Run 'jelly connect all' to link agents via MCP[/dim]",
            "[dim]—[/dim]",
        )
    else:
        for e in events[:10]:
            mood_str = e.get("mood", "calm")
            if mood_str == "sparkle":
                glow_badge = f"[bold {Palette.PINK}]★ sparkle[/]"
            elif mood_str == "curious":
                glow_badge = f"[{Palette.ROSE}]? curious[/]"
            elif mood_str == "playful":
                glow_badge = f"[bold {Palette.GOLD}]~ playful[/]"
            else:
                glow_badge = f"[{Palette.CYAN}]· calm[/]"

            table.add_row(
                e.get("time", ""),
                e.get("agent", "Agent"),
                e.get("event", ""),
                glow_badge,
            )
    return table
