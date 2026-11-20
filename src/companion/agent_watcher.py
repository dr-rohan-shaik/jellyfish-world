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
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from src.ui.palette import Palette


def get_activity_log_path() -> Path:
    """Return path to local agent activity buffer."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    data_dir = repo_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "agent_activity.json"


def record_agent_event(agent_name: str, event_text: str, mood: str = "calm") -> None:
    """Record a new event from an external AI agent."""
    log_path = get_activity_log_path()
    events: List[Dict[str, Any]] = []

    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
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


def get_recent_agent_events() -> List[Dict[str, Any]]:
    """Return list of recent agent activities."""
    log_path = get_activity_log_path()
    if not log_path.exists():
        # Provide welcoming seed events if file is new
        return [
            {"time": "Now", "agent": "Claude Code", "event": "Connected via MCP stdio bridge", "mood": "calm"},
            {"time": "Now", "agent": "OpenCode", "event": "Ready to report coding tasks", "mood": "curious"},
        ]
    try:
        with open(log_path, "r", encoding="utf-8") as f:
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
