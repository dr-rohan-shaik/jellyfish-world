"""PowerShell $PROFILE management for Jellyfish World autostart.

Safely adds and removes a single marked block:
# >>> jellyfish
...
# <<< jellyfish

Always creates a timestamped backup before writing.
"""
from __future__ import annotations

import datetime
import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

START_MARKER = "# >>> jellyfish"
END_MARKER = "# <<< jellyfish"


def get_default_profile_paths() -> List[Path]:
    """Return common user PowerShell profile locations (User scope only)."""
    user_home = Path.home()
    documents = user_home / "Documents"
    return [
        documents / "PowerShell" / "Microsoft.PowerShell_profile.ps1",
        documents / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1",
    ]


def locate_active_profile() -> Path:
    """Find the existing profile, or return the standard PowerShell 7 / Windows PowerShell location."""
    paths = get_default_profile_paths()
    for p in paths:
        if p.exists():
            return p
    return paths[0]


def has_jellyfish_block(content: str) -> bool:
    """Check if the profile content already contains the jellyfish block."""
    return START_MARKER in content and END_MARKER in content


def generate_powershell_block(python_path: str, cli_path: str) -> str:
    """Generate the exact block to insert into $PROFILE."""
    py = str(python_path).replace("\\", "/")
    cli = str(cli_path).replace("\\", "/")
    companion = str(Path(cli_path).parent.parent / "companion" / "session.py").replace("\\", "/")
    return (
        f"{START_MARKER}\n"
        f"# Automatically added by Jellyfish World - do not edit directly\n"
        f"function global:jellyfish {{\n"
        f'    & "{py}" "{companion}" $args\n'
        f"}}\n"
        f"if (-not $env:JELLY_SEEN -and $env:TERM_PROGRAM -ne 'vscode') {{\n"
        f'    & "{py}" "{cli}" greet --autostart\n'
        f"}}\n"
        f"{END_MARKER}\n"
    )


def inject_block(content: str, python_path: str, cli_path: str) -> str:
    """Insert or update the marked block in profile text."""
    block = generate_powershell_block(python_path, cli_path)
    if has_jellyfish_block(content):
        # Replace existing block cleanly
        before = content.split(START_MARKER)[0].rstrip()
        after = content.split(END_MARKER)[1].lstrip()
        new_content = f"{before}\n\n{block}\n{after}".strip() + "\n"
        return new_content

    # Append block
    sep = "\n\n" if content.strip() else ""
    return content.rstrip() + sep + block


def remove_block(content: str) -> str:
    """Remove the marked jellyfish block cleanly from profile text."""
    if not has_jellyfish_block(content):
        return content

    before = content.split(START_MARKER)[0].rstrip()
    after = content.split(END_MARKER)[1].lstrip()

    if before and after:
        return f"{before}\n\n{after}".strip() + "\n"
    elif before:
        return before.strip() + "\n"
    elif after:
        return after.strip() + "\n"
    return ""


def backup_profile(profile_path: Path) -> Optional[Path]:
    """Create a timestamped backup of the profile."""
    if not profile_path.exists():
        return None

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = profile_path.parent / f"{profile_path.name}.bak.{timestamp}"
    shutil.copy2(profile_path, backup_path)
    return backup_path


def apply_powershell_autostart(
    profile_path: Path,
    python_path: str,
    cli_path: str,
) -> Tuple[bool, str, Optional[Path]]:
    """Inject autostart block into profile with automatic backup."""
    backup_path = None
    if profile_path.exists():
        backup_path = backup_profile(profile_path)
        content = profile_path.read_text(encoding="utf-8")
    else:
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        content = ""

    new_content = inject_block(content, python_path, cli_path)
    profile_path.write_text(new_content, encoding="utf-8")
    return True, new_content, backup_path


def remove_powershell_autostart(
    profile_path: Path,
) -> Tuple[bool, str, Optional[Path]]:
    """Remove autostart block from profile with automatic backup."""
    if not profile_path.exists():
        return False, "Profile does not exist", None

    content = profile_path.read_text(encoding="utf-8")
    if not has_jellyfish_block(content):
        return False, "No jellyfish block found in profile", None

    backup_path = backup_profile(profile_path)
    new_content = remove_block(content)
    profile_path.write_text(new_content, encoding="utf-8")
    return True, new_content, backup_path
