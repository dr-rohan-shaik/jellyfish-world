"""Shell execution guards and loop prevention for Jellyfish World autostart.

Ensures the greeting:
1. Only runs in interactive shells (TTY check).
2. Never runs inside VS Code terminals (TERM_PROGRAM=vscode).
3. Never runs when cmd.exe is called with /c or non-interactively.
4. Never runs in nested subshells (JELLY_SEEN=1).
5. Never runs when quiet mode is active.
"""
from __future__ import annotations

import os
import sys


def is_seen() -> bool:
    """Return True if JELLY_SEEN environment variable is set to 1."""
    return os.environ.get("JELLY_SEEN", "").strip() == "1"


def mark_seen() -> None:
    """Set JELLY_SEEN=1 in the current process environment."""
    os.environ["JELLY_SEEN"] = "1"


def is_vscode_terminal() -> bool:
    """Return True if running inside VS Code terminal."""
    return os.environ.get("TERM_PROGRAM", "").lower() == "vscode"


def is_interactive_tty() -> bool:
    """Return True if both stdin and stdout are interactive TTYs."""
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except Exception:
        return False


def is_cmd_slash_c() -> bool:
    """Check if cmd.exe was likely invoked with /c or in a script context."""
    # Check command-line arguments of this process or environment flags
    cmd_line = " ".join(sys.argv).lower()
    if "/c" in cmd_line or "-c" in cmd_line:
        return True

    # Check Windows PROMPT variable; non-interactive cmd often lacks PROMPT
    if sys.platform == "win32" and "PROMPT" not in os.environ and "PSModulePath" not in os.environ:
        return True

    return False


def is_quiet_mode() -> bool:
    """Check if quiet mode is set via environment or flag."""
    val = os.environ.get("JELLY_QUIET", "").strip().lower()
    return val in ("1", "true", "yes", "on")


def should_suppress_greeting() -> tuple[bool, str]:
    """Determine if the jellyfish greeting should be suppressed.

    Returns:
        (suppress: bool, reason: str)
    """
    if is_seen():
        return True, "JELLY_SEEN is set (nested shell or already greeted)"

    if is_vscode_terminal():
        return True, "Running inside VS Code terminal (TERM_PROGRAM=vscode)"

    if is_quiet_mode():
        return True, "Quiet mode is active (JELLY_QUIET=1)"

    if not is_interactive_tty():
        return True, "Non-interactive stream (stdin or stdout is not a TTY)"

    if is_cmd_slash_c():
        return True, "Non-interactive /c command execution detected"

    return False, ""
