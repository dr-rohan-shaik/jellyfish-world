"""Command Prompt (cmd.exe) AutoRun registry management for Jellyfish World.

Modifies strictly HKCU\\Software\\Microsoft\\Command Processor\\AutoRun.
NEVER touches HKLM or system-wide settings.
Preserves existing AutoRun commands and appends/removes surgically.
"""
from __future__ import annotations

import sys
from typing import Optional, Tuple

REG_SUBKEY = r"Software\Microsoft\Command Processor"
REG_VALUE_NAME = "AutoRun"
HOOK_IDENTIFIER = "jelly.py"


def generate_cmd_hook(python_path: str, cli_path: str) -> str:
    """Format the safe one-line cmd autostart hook."""
    py = f'"{python_path}"'
    cli = f'"{cli_path}"'
    return f'if not defined JELLY_SEEN if not "%TERM_PROGRAM%"=="vscode" {py} {cli} greet --autostart'


def is_jelly_hook(part: str) -> bool:
    """Detect whether a sub-command is the jellyfish greeting hook."""
    clean = part.strip()
    return ("jelly.py" in clean or "jelly" in clean) and "greet" in clean and "JELLY_SEEN" in clean


def append_to_autorun(existing: Optional[str], hook: str) -> str:
    """Append hook to existing AutoRun command without overwriting it."""
    if not existing or not existing.strip():
        return hook

    clean_existing = existing.strip()
    if is_jelly_hook(clean_existing):
        # Already present; replace hook portion
        cleaned = remove_from_autorun(clean_existing)
        if cleaned:
            return f"{cleaned} & {hook}"
        return hook

    return f"{clean_existing} & {hook}"


def remove_from_autorun(current: Optional[str]) -> Optional[str]:
    """Surgically remove the jellyfish hook from the AutoRun string."""
    if not current:
        return None

    # Split command chained with &
    parts = [p.strip() for p in current.split("&") if p.strip()]
    remaining = [p for p in parts if not is_jelly_hook(p)]

    if not remaining:
        return None
    return " & ".join(remaining)


def get_current_autorun() -> Optional[str]:
    """Read the current AutoRun registry value from HKCU."""
    if sys.platform != "win32":
        return None

    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, REG_VALUE_NAME)
            return str(val)
    except FileNotFoundError:
        return None
    except Exception:
        return None


def set_cmd_autorun(
    python_path: str,
    cli_path: str,
) -> Tuple[bool, str, Optional[str]]:
    """Set/append the jellyfish hook in HKCU Command Processor AutoRun.

    Returns:
        (success: bool, new_value: str, previous_value: Optional[str])
    """
    if sys.platform != "win32":
        return False, "Not running on Windows", None

    import winreg
    prev = get_current_autorun()
    hook = generate_cmd_hook(python_path, cli_path)
    new_val = append_to_autorun(prev, hook)

    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY) as key:
            winreg.SetValueEx(key, REG_VALUE_NAME, 0, winreg.REG_SZ, new_val)
        return True, new_val, prev
    except Exception as e:
        return False, f"Registry error: {e}", prev


def remove_cmd_autorun() -> Tuple[bool, Optional[str], Optional[str]]:
    """Remove the jellyfish hook from HKCU Command Processor AutoRun.

    Returns:
        (success: bool, new_value: Optional[str], previous_value: Optional[str])
    """
    if sys.platform != "win32":
        return False, None, None

    import winreg
    prev = get_current_autorun()
    if not prev or not is_jelly_hook(prev):
        return False, prev, prev

    new_val = remove_from_autorun(prev)

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY, 0, winreg.KEY_SET_VALUE) as key:
            if new_val:
                winreg.SetValueEx(key, REG_VALUE_NAME, 0, winreg.REG_SZ, new_val)
            else:
                winreg.DeleteValue(key, REG_VALUE_NAME)
        return True, new_val, prev
    except Exception:
        return False, prev, prev
