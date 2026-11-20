"""Unit tests for Stage 8: Universal Agent Bridge (MCP & Auto-Connect)."""
import json
import pytest
from pathlib import Path

from src.bridge.mcp_server import (
    process_mcp_message,
    execute_tool,
    STATE,
)
from src.bridge.auto_connect import (
    inject_mcp_into_json,
    remove_mcp_from_json,
    generate_mcp_entry,
    generate_generic_runners,
    scan_agent_status,
)


def test_mcp_initialize():
    msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "claude-code", "version": "1.0"},
        },
    }
    resp = process_mcp_message(msg)
    assert resp is not None
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "jellyfish-world"
    assert "tools" in resp["result"]["capabilities"]


def test_mcp_tools_list():
    msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    resp = process_mcp_message(msg)
    assert resp is not None
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "hey_jellyfish" in tool_names
    assert "jellyfish_status" in tool_names
    assert "jellyfish_react" in tool_names
    assert "jellyfish_tap" in tool_names
    assert "jellyfish_decide" in tool_names


def test_mcp_tool_hey_jellyfish():
    call_msg = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "hey_jellyfish",
            "arguments": {"message": "hello jellyfish!"},
        },
    }
    resp = process_mcp_message(call_msg)
    assert resp is not None
    assert "result" in resp
    content = resp["result"]["content"][0]["text"]
    assert "Aurelia" in content
    assert "pulses softly" in content or "greeting" in content


def test_mcp_tool_jellyfish_status():
    call_msg = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {"name": "jellyfish_status", "arguments": {}},
    }
    resp = process_mcp_message(call_msg)
    assert resp is not None
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["name"] == "Aurelia"
    assert data["number"] == "#00001"
    assert data["is_founder"] is True
    assert "current_mood" in data


def test_mcp_tool_jellyfish_react():
    call_msg = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "jellyfish_react",
            "arguments": {"event": "All tests passed successfully!"},
        },
    }
    resp = process_mcp_message(call_msg)
    assert resp is not None
    assert STATE["mood"] == "sparkle"


def test_mcp_tool_jellyfish_tap():
    initial_taps = STATE["tap_count"]
    call_msg = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {"name": "jellyfish_tap", "arguments": {}},
    }
    resp = process_mcp_message(call_msg)
    assert resp is not None
    assert STATE["tap_count"] == initial_taps + 1


def test_mcp_tool_jellyfish_decide():
    call_msg = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "jellyfish_decide",
            "arguments": {
                "situation": "Choosing accent light",
                "options": ["Pink", "Cyan", "Gold"],
            },
        },
    }
    resp = process_mcp_message(call_msg)
    assert resp is not None
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["chosen_option"] in ["Pink", "Cyan", "Gold"]


def test_inject_and_remove_mcp_json(tmp_path: Path):
    test_cfg = tmp_path / "claude_desktop_config.json"
    test_cfg.write_text('{"mcpServers": {"other": {"command": "echo"}}}', encoding="utf-8")

    # Inject
    ok, msg, bak = inject_mcp_into_json(test_cfg, "python", "jelly.py")
    assert ok is True
    assert bak is not None
    assert bak.exists()

    with open(test_cfg, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "jellyfish" in data["mcpServers"]
    assert "other" in data["mcpServers"]

    # Remove
    ok_rem, msg_rem, bak2 = remove_mcp_from_json(test_cfg)
    assert ok_rem is True
    with open(test_cfg, "r", encoding="utf-8") as f:
        data_after = json.load(f)
    assert "jellyfish" not in data_after["mcpServers"]
    assert "other" in data_after["mcpServers"]


def test_generic_runners_generated(tmp_path: Path):
    bat, sh = generate_generic_runners(tmp_path, "python.exe", "jelly.py")
    assert bat.exists()
    assert sh.exists()
    assert "mcp" in bat.read_text(encoding="utf-8")
    assert "mcp" in sh.read_text(encoding="utf-8")
