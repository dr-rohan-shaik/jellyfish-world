"""Windows Terminal Sidepane launcher for Jellyfish World.

Spawns a vertical split pane in the active Windows Terminal window
running the live floating jellyfish view via `wt.exe`.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from typing import Tuple


def is_windows_terminal_available() -> bool:
    """Check if wt.exe is available on the system PATH."""
    return shutil.which("wt.exe") is not None or shutil.which("wt") is not None


def open_sidepane(python_path: str, cli_path: str, width_fraction: float = 0.35) -> Tuple[bool, str]:
    """Launch a vertical split pane in Windows Terminal running `jelly home`."""
    if sys.platform != "win32":
        return False, "Sidepane requires Windows Terminal on Windows."

    wt = shutil.which("wt.exe") or shutil.which("wt")
    if not wt:
        return False, "Windows Terminal ('wt.exe') is not found on your PATH."

    # Windows Terminal command:
    # -w 0: Target current window
    # sp: split pane
    # -V: vertical split
    # -s: size fraction (e.g. 0.35)
    size_str = f"{width_fraction:.2f}"
    cmd = [
        wt,
        "-w", "0",
        "sp",
        "-V",
        "-s", size_str,
        "powershell.exe",
        "-NoExit",
        "-Command",
        f'& "{python_path}" "{cli_path}" home',
    ]

    try:
        subprocess.Popen(cmd, shell=False)
        return True, "Opened jellyfish floating view in Windows Terminal sidepane."
    except Exception as e:
        return False, f"Failed to spawn Windows Terminal split pane: {e}"


def close_sidepane_instruction() -> str:
    """Return instructions to close the sidepane."""
    return "To close the sidepane, click inside it and press Ctrl+Shift+W, or type 'exit'."
