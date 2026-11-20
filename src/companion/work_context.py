"""Work Context and Calm Decision Engine for Jellyfish World.

Inspects current working directory tasks (git changes, modified files)
and formulates 3 gentle, pressure-free options for the owner.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def get_git_status_summary(cwd: Path | None = None) -> dict[str, Any]:
    """Inspect git repository status in the current working directory."""
    if cwd is None:
        cwd = Path.cwd()

    summary = {
        "is_git": False,
        "branch": "",
        "modified_count": 0,
        "recent_files": [],
    }

    try:
        # Check branch
        res_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if res_branch.returncode == 0:
            summary["is_git"] = True
            summary["branch"] = res_branch.stdout.strip()

        # Check modified files
        res_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if res_status.returncode == 0:
            lines = [line.strip() for line in res_status.stdout.splitlines() if line.strip()]
            summary["modified_count"] = len(lines)
            summary["recent_files"] = [line.split()[-1] for line in lines[:5]]
    except Exception:
        pass

    return summary


def generate_work_options(cwd: Path | None = None) -> list[dict[str, str]]:
    """Produce 3 calm options for the owner based on current work."""
    git_info = get_git_status_summary(cwd)
    branch = git_info["branch"] or "main"
    mod_count = git_info["modified_count"]

    if mod_count > 0:
        opt_work = f"Review or run tests on {mod_count} modified files (branch: '{branch}')"
    else:
        opt_work = f"Workspace is calm & clean on '{branch}' — ready for new tasks"

    return [
        {
            "letter": "A",
            "title": "Continue Code Flow",
            "desc": opt_work,
            "action": "work",
        },
        {
            "letter": "B",
            "title": "Aesthetic Shift",
            "desc": "Switch your jellyfish's bioluminescent glow (Cyan / Pink / Gold)",
            "action": "glow",
        },
        {
            "letter": "C",
            "title": "Gentle Breather",
            "desc": "Pause for a 30-second silent drift to rest your eyes",
            "action": "breathe",
        },
    ]
