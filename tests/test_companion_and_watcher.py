"""Unit tests for Interactive Companion & Agent Watcher."""
import tempfile
from pathlib import Path

import pytest

from src.companion.agent_watcher import (
    get_recent_agent_events,
    record_agent_event,
    render_agent_watcher_table,
    set_activity_log_path_override,
)
from src.companion.chat import respond_to_owner
from src.companion.work_context import (
    generate_work_options,
)


@pytest.fixture(autouse=True)
def isolate_agent_log():
    """Isolate each test with its own temporary agent activity log."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = Path(f.name)
    set_activity_log_path_override(temp_path)
    yield
    set_activity_log_path_override(None)
    if temp_path.exists():
        temp_path.unlink()


def test_agent_watcher_event_recording():
    record_agent_event("Claude Code", "Refactoring database queries", "sparkle")
    events = get_recent_agent_events()
    assert len(events) > 0
    top = events[0]
    assert top["agent"] == "Claude Code"
    assert "Refactoring" in top["event"]
    assert top["mood"] == "sparkle"


def test_agent_watcher_table_rendering():
    record_agent_event("OpenCode", "Running integration tests", "curious")
    table = render_agent_watcher_table()
    assert table is not None
    assert "Agent Watcher" in str(table.title)


def test_work_options_generator():
    options = generate_work_options()
    assert len(options) == 3
    letters = [o["letter"] for o in options]
    assert letters == ["A", "B", "C"]
    for o in options:
        assert len(o["title"]) > 0
        assert len(o["desc"]) > 0


def test_companion_in_character_chat():
    reply_greet = respond_to_owner("hello jellyfish!", "Aurelia", "calm")
    assert "Aurelia:" in reply_greet
    assert "AI" not in reply_greet
    assert "language model" not in reply_greet
    assert "pain" not in reply_greet

    reply_work = respond_to_owner("I'm working on a tough bug", "Aurelia", "calm")
    assert "Aurelia:" in reply_work
    assert len(reply_work.split(".")) <= 4  # 1-3 sentences
