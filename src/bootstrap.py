"""Bootstrap module for Jellyfish World.

Ensures the project root is on sys.path for all entry points.
This module should be imported first by all CLI entry points.
"""
from __future__ import annotations

import sys
from pathlib import Path


def ensure_project_root_on_path() -> Path:
    """Add the project root to sys.path if not already present.

    Returns:
        The project root Path.
    """
    # This file is at src/bootstrap.py, so project root is parent.parent
    project_root = Path(__file__).resolve().parent.parent
    project_root_str = str(project_root)

    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)

    return project_root


# Auto-execute on import
ensure_project_root_on_path()
