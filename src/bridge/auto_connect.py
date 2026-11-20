"""Auto-discovery and configuration injector for AI coding agents.

Supports:
- Claude Code / Claude Desktop
- Cursor / VS Code
- OpenCode / Codex
- Hermes / OpenClaw / DeepSeek (via universal runner scripts)
"""
from __future__ import annotations

import datetime
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


def get_default_paths() -> tuple[str, str]:
    """Get paths to current virtualenv python and main cli entrypoint."""
    py_path = sys.executable
    repo_root = Path(__file__).resolve().parent.parent.parent
    cli_path = str(repo_root / "src" / "cli" / "jelly.py")
    return py_path, cli_path


def get_agent_config_targets() -> dict[str, list[Path]]:
    """Return map of agent names to their potential MCP configuration paths."""
    home = Path.home()
    appdata = Path(os.environ.get("APPDATA", str(home / "AppData" / "Roaming")))

    return {
        "claude": [
            home / ".claude.json",
            appdata / "Claude" / "claude_desktop_config.json",
            home / ".config" / "claude" / "claude_desktop_config.json",
        ],
        "cursor": [
            home / ".cursor" / "mcp.json",
            appdata / "Cursor" / "User" / "globalStorage" / "mcp.json",
        ],
        "opencode": [
            home / ".config" / "opencode" / "mcp.json",
            home / ".opencode" / "mcp.json",
        ],
    }


def backup_file(path: Path) -> Path | None:
    """Create timestamped backup of a config file."""
    if not path.exists():
        return None
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak_path = path.parent / f"{path.name}.bak.{timestamp}"
    shutil.copy2(path, bak_path)
    return bak_path


def generate_mcp_entry(python_path: str, cli_path: str) -> dict[str, Any]:
    """Format the MCP stdio server entry for JSON configs."""
    return {
        "command": python_path,
        "args": [cli_path, "mcp"],
        "env": {
            "JELLY_SEEN": "1",
        },
    }


def inject_mcp_into_json(file_path: Path, python_path: str, cli_path: str) -> tuple[bool, str, Path | None]:
    """Add jellyfish entry to an MCP JSON configuration file."""
    bak = backup_file(file_path) if file_path.exists() else None
    data: dict[str, Any] = {}

    if file_path.exists():
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except Exception:
            data = {}

    # Target key depends on format: 'mcpServers' or 'servers'
    container_key = "mcpServers" if "mcpServers" in data or "servers" not in data else "servers"
    if container_key not in data or not isinstance(data[container_key], dict):
        data[container_key] = {}

    data[container_key]["jellyfish"] = generate_mcp_entry(python_path, cli_path)

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return True, f"Injected into {file_path}", bak


def remove_mcp_from_json(file_path: Path) -> tuple[bool, str, Path | None]:
    """Remove jellyfish entry from an MCP JSON configuration file."""
    if not file_path.exists():
        return False, "Config file does not exist", None

    bak = backup_file(file_path)
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return False, "Failed to parse JSON file", None

    removed = False
    for key in ("mcpServers", "servers"):
        if key in data and isinstance(data[key], dict) and "jellyfish" in data[key]:
            del data[key]["jellyfish"]
            removed = True

    if not removed:
        return False, "No jellyfish entry found in config", None

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return True, f"Removed jellyfish entry from {file_path}", bak


def generate_generic_runners(repo_root: Path, python_path: str, cli_path: str) -> tuple[Path, Path]:
    """Generate universal runner scripts for OpenClaw, Hermes, DeepSeek, and CLI agents."""
    bat_path = repo_root / "mcp_runner.bat"
    sh_path = repo_root / "mcp_runner.sh"

    bat_content = f'@echo off\n"{python_path}" "{cli_path}" mcp\n'
    sh_content = f'#!/usr/bin/env bash\nexec "{python_path}" "{cli_path}" mcp\n'

    bat_path.write_text(bat_content, encoding="utf-8")
    sh_path.write_text(sh_content, encoding="utf-8")
    try:
        sh_path.chmod(0o755)
    except Exception:
        pass

    return bat_path, sh_path


def scan_agent_status() -> list[dict[str, Any]]:
    """Inspect all supported agent configurations and return their status."""
    targets = get_agent_config_targets()
    results = []

    for agent, paths in targets.items():
        found_path = None
        has_jelly = False

        for p in paths:
            if p.exists():
                found_path = p
                try:
                    with open(p, encoding="utf-8") as f:
                        data = json.load(f)
                        servers = data.get("mcpServers") or data.get("servers") or {}
                        if "jellyfish" in servers:
                            has_jelly = True
                except Exception:
                    pass
                break

        results.append({
            "agent": agent,
            "installed": found_path is not None,
            "path": found_path,
            "connected": has_jelly,
        })
    return results


def connect_all_agents(repo_root: Path | None = None) -> list[dict[str, Any]]:
    """Automatically connect Jellyfish MCP bridge to all detected agents."""
    py_path, cli_path = get_default_paths()
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent

    # 1. Create universal scripts for Hermes / OpenClaw / DeepSeek
    generate_generic_runners(repo_root, py_path, cli_path)

    # 2. Inject into detected JSON configs
    targets = get_agent_config_targets()
    reports = []

    for agent, paths in targets.items():
        # Prefer existing file, else use primary default path
        target_path = next((p for p in paths if p.exists()), paths[0])
        ok, msg, bak = inject_mcp_into_json(target_path, py_path, cli_path)
        reports.append({
            "agent": agent,
            "success": ok,
            "path": target_path,
            "backup": bak,
            "message": msg,
        })

    return reports


def disconnect_all_agents() -> list[dict[str, Any]]:
    """Remove Jellyfish MCP bridge from all configured agents."""
    targets = get_agent_config_targets()
    reports = []

    for agent, paths in targets.items():
        for p in paths:
            if p.exists():
                ok, msg, bak = remove_mcp_from_json(p)
                reports.append({
                    "agent": agent,
                    "success": ok,
                    "path": p,
                    "backup": bak,
                    "message": msg,
                })
    return reports
