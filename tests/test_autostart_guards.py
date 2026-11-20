"""Unit tests for autostart shell guards and loop prevention."""
import sys

from src.autostart.guards import (
    is_quiet_mode,
    is_seen,
    is_vscode_terminal,
    mark_seen,
    should_suppress_greeting,
)


def test_jelly_seen_guard(monkeypatch):
    monkeypatch.setenv("JELLY_SEEN", "1")
    assert is_seen() is True
    suppress, reason = should_suppress_greeting()
    assert suppress is True
    assert "JELLY_SEEN" in reason


def test_mark_seen(monkeypatch):
    monkeypatch.delenv("JELLY_SEEN", raising=False)
    assert is_seen() is False
    mark_seen()
    assert is_seen() is True


def test_vscode_terminal_guard(monkeypatch):
    monkeypatch.delenv("JELLY_SEEN", raising=False)
    monkeypatch.setenv("TERM_PROGRAM", "vscode")
    assert is_vscode_terminal() is True
    suppress, reason = should_suppress_greeting()
    assert suppress is True
    assert "vscode" in reason.lower()


def test_quiet_mode_guard(monkeypatch):
    monkeypatch.delenv("JELLY_SEEN", raising=False)
    monkeypatch.delenv("TERM_PROGRAM", raising=False)
    monkeypatch.setenv("JELLY_QUIET", "1")
    assert is_quiet_mode() is True
    suppress, reason = should_suppress_greeting()
    assert suppress is True
    assert "quiet" in reason.lower()


def test_non_tty_stream_suppression(monkeypatch):
    monkeypatch.delenv("JELLY_SEEN", raising=False)
    monkeypatch.delenv("TERM_PROGRAM", raising=False)
    monkeypatch.delenv("JELLY_QUIET", raising=False)

    # Mock stdin/stdout as non-tty
    class DummyStream:
        def isatty(self):
            return False

    monkeypatch.setattr(sys, "stdin", DummyStream())
    suppress, reason = should_suppress_greeting()
    assert suppress is True
    assert "non-interactive" in reason.lower() or "tty" in reason.lower()
