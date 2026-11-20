"""Lightweight Model Context Protocol (MCP) Server for Jellyfish World.

Enables seamless two-way integration with AI agents:
- Claude Code / Claude Desktop
- Codex / OpenCode
- OpenClaw & Hermes
- DeepSeek harnesses
- Cursor & Windsurf

Zero heavy dependencies (uses Python standard library).
Starts in < 40ms over stdio JSON-RPC 2.0.
Strictly enforces locked invariants (no chat leaks, no release via agent).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
_repo_root = str(Path(__file__).resolve().parent.parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

# Global in-memory temporary state for the active jellyfish session
STATE = {
    "name": "Aurelia",
    "number": 1,
    "is_founder": True,
    "mood": "calm",
    "tap_count": 0,
    "equipped": ["Crown"],
}


# Tool definitions matching the MCP specification
MCP_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "hey_jellyfish",
        "description": "Speak gently to your AI jellyfish in character. It will answer with 1-3 calm sentences.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "What you want to say to your jellyfish.",
                }
            },
            "required": ["message"],
        },
    },
    {
        "name": "jellyfish_status",
        "description": "Get current status, name, birth number (#00001), founder status, and mood of your jellyfish.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "jellyfish_react",
        "description": "Notify your jellyfish of an event (e.g. 'code tested', 'build succeeded', 'refactoring', 'problem solved'). It will gently shift its temporary glow mood.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event": {
                    "type": "string",
                    "description": "The event or action completed by the agent.",
                }
            },
            "required": ["event"],
        },
    },
    {
        "name": "jellyfish_tap",
        "description": "Feed light to your jellyfish (daily 10-second glow interaction). Increases tap count.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "jellyfish_decide",
        "description": "Ask the jellyfish to make a calm, harmless aesthetic choice between options using its personality.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "situation": {
                    "type": "string",
                    "description": "The context or aesthetic dilemma.",
                },
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of options to choose from.",
                },
            },
            "required": ["situation", "options"],
        },
    },
]


def handle_hey_jellyfish(message: str) -> str:
    """Generate in-character reply without persisting any chat history."""
    msg_lower = message.lower()
    name = STATE["name"]
    mood = STATE["mood"]

    if "hello" in msg_lower or "hi" in msg_lower or "hey" in msg_lower:
        return f"{name} pulses softly with a {mood} glow, sending a warm ripple through the water in greeting."
    elif "how are you" in msg_lower:
        return f"{name} drifts calmly in the deep ocean currents, glowing {mood} and feeling peaceful."
    elif "who are you" in msg_lower or "what are you" in msg_lower:
        num = f"#{STATE['number']:05d}"
        founder = " (Founder #00001)" if STATE["is_founder"] else ""
        return f"I am {name} {num}{founder}, a calm jellyfish drifting in the terminal sea."
    else:
        return f"{name} listens quietly as light shimmers across its translucent bell. It sways its tentacles gently beside you."


def handle_jellyfish_status() -> Dict[str, Any]:
    """Return public status summary."""
    return {
        "name": STATE["name"],
        "number": f"#{STATE['number']:05d}",
        "is_founder": STATE["is_founder"],
        "current_mood": STATE["mood"],
        "equipped_cosmetics": list(STATE["equipped"]),
        "taps_today": STATE["tap_count"],
    }


def handle_jellyfish_react(event: str) -> str:
    """Shift temporary mood based on agent event."""
    from src.companion.agent_watcher import record_agent_event

    event_lower = event.lower()
    if any(k in event_lower for k in ("success", "passed", "fixed", "done", "complete")):
        STATE["mood"] = "sparkle"
        resp = f"{STATE['name']} sparks with bright bioluminescent pink flashes in celebration!"
    elif any(k in event_lower for k in ("think", "ponder", "search", "explore", "read")):
        STATE["mood"] = "curious"
        resp = f"{STATE['name']} tilts its bell and hovers closely with a curious rose shimmer."
    elif any(k in event_lower for k in ("play", "fun", "creative", "style")):
        STATE["mood"] = "playful"
        resp = f"{STATE['name']} performs a gentle flip and floats in a slow golden spiral."
    else:
        STATE["mood"] = "calm"
        resp = f"{STATE['name']} hums with a deep cyan bioluminescence, watching peacefully."

    record_agent_event("AI Agent", event, STATE["mood"])
    return resp


def handle_jellyfish_tap() -> str:
    """Increment light feed counter."""
    STATE["tap_count"] += 1
    return f"You fed light to {STATE['name']}. Its bell brightens with soothing warmth (Total light feeds: {STATE['tap_count']})."


def handle_jellyfish_decide(situation: str, options: List[str]) -> Dict[str, Any]:
    """Make calm autonomous decision."""
    if not options:
        return {"choice": None, "reason": "No options provided."}

    # Deterministic choice based on hash of situation and options
    import hashlib
    h = int(hashlib.sha256(f"{situation}:{','.join(options)}".encode()).hexdigest(), 16)
    picked_idx = h % len(options)
    choice = options[picked_idx]
    return {
        "situation": situation,
        "chosen_option": choice,
        "mood_at_decision": STATE["mood"],
        "note": "A calm, gentle choice made without pressure.",
    }


def execute_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Route tool call to appropriate handler."""
    if name == "hey_jellyfish":
        msg = arguments.get("message", "")
        return handle_hey_jellyfish(msg)

    elif name == "jellyfish_status":
        return handle_jellyfish_status()

    elif name == "jellyfish_react":
        evt = arguments.get("event", "")
        return handle_jellyfish_react(evt)

    elif name == "jellyfish_tap":
        return handle_jellyfish_tap()

    elif name == "jellyfish_decide":
        sit = arguments.get("situation", "")
        opts = arguments.get("options", [])
        return handle_jellyfish_decide(sit, opts)

    else:
        raise ValueError(f"Unknown tool: {name}")


def process_mcp_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process a single JSON-RPC 2.0 message from stdin."""
    msg_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    # Handshake: initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "jellyfish-world",
                    "version": "1.0.0",
                },
                "capabilities": {
                    "tools": {},
                },
            },
        }

    # Notification: initialized
    elif method == "notifications/initialized":
        return None

    # Ping
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

    # List tools
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": MCP_TOOLS,
            },
        }

    # Execute tool
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        try:
            result_data = execute_tool(tool_name, tool_args)
            text_output = (
                json.dumps(result_data, indent=2)
                if isinstance(result_data, (dict, list))
                else str(result_data)
            )
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": text_output,
                        }
                    ],
                },
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": str(e),
                },
            }

    # Unknown method
    if msg_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}",
            },
        }
    return None


def run_mcp_server():
    """Run standard I/O JSON-RPC loop."""
    sys.stderr.write("Jellyfish World MCP Server started over stdio.\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = process_mcp_message(req)
            if resp is not None:
                out = json.dumps(resp)
                sys.stdout.write(out + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            err = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_mcp_server()
