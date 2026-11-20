"""Jellyfish World - Terminal-first companion app with MCP bridge for AI agents."""

from src.ai.adapter import query_jellyfish_ai
from src.ai.decision_engine import decide_choice, extract_options, is_decision_query
from src.ai.semantic_engine import generate_semantic_reply
from src.bridge.mcp_server import STATE, run_mcp_server
from src.companion.agent_watcher import (
    get_recent_agent_events,
    record_agent_event,
    render_agent_watcher_table,
)
from src.companion.chat import respond_to_owner
from src.companion.session import handle_direct_message, run_companion_session
from src.companion.work_context import generate_work_options, get_git_status_summary
from src.core.cosmetics import CosmeticItem, apply_cosmetics_to_frame, load_cosmetics_catalog
from src.ui.ascii_art import get_animated_frame, render_jellyfish_card
from src.ui.palette import Palette, get_mood_color, get_theme, is_no_color, is_reduced_motion

__version__ = "1.0.0"
__all__ = [
    "query_jellyfish_ai",
    "decide_choice",
    "extract_options",
    "is_decision_query",
    "generate_semantic_reply",
    "STATE",
    "run_mcp_server",
    "get_recent_agent_events",
    "record_agent_event",
    "render_agent_watcher_table",
    "respond_to_owner",
    "handle_direct_message",
    "run_companion_session",
    "generate_work_options",
    "get_git_status_summary",
    "CosmeticItem",
    "apply_cosmetics_to_frame",
    "load_cosmetics_catalog",
    "get_animated_frame",
    "render_jellyfish_card",
    "Palette",
    "get_mood_color",
    "get_theme",
    "is_no_color",
    "is_reduced_motion",
]
