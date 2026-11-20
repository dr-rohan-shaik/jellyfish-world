"""Unit tests for Command Prompt AutoRun string manipulation."""
from src.autostart.cmd_autorun import (
    generate_cmd_hook,
    append_to_autorun,
    remove_from_autorun,
    is_jelly_hook,
)


def test_generate_cmd_hook():
    hook = generate_cmd_hook("C:/py/python.exe", "C:/app/jelly.py")
    assert is_jelly_hook(hook)
    assert "JELLY_SEEN" in hook
    assert "vscode" in hook


def test_append_to_empty():
    hook = generate_cmd_hook("C:/py/python.exe", "C:/app/jelly.py")
    result = append_to_autorun(None, hook)
    assert result == hook

    result2 = append_to_autorun("", hook)
    assert result2 == hook


def test_append_preserves_existing():
    hook = generate_cmd_hook("C:/py/python.exe", "C:/app/jelly.py")
    existing = "chcp 65001"
    result = append_to_autorun(existing, hook)

    assert result.startswith("chcp 65001 & ")
    assert hook in result


def test_append_idempotent():
    hook = generate_cmd_hook("C:/py/python.exe", "C:/app/jelly.py")
    existing = "doskey ls=dir"
    once = append_to_autorun(existing, hook)
    twice = append_to_autorun(once, hook)

    assert is_jelly_hook(twice)
    # The hook should only appear once
    assert twice.count("jelly.py") == 1
    assert "doskey ls=dir" in twice


def test_remove_hook_restores_original():
    hook = generate_cmd_hook("C:/py/python.exe", "C:/app/jelly.py")
    existing = "chcp 65001"
    chained = append_to_autorun(existing, hook)

    cleaned = remove_from_autorun(chained)
    assert cleaned == "chcp 65001"


def test_remove_when_only_hook_returns_none():
    hook = generate_cmd_hook("C:/py/python.exe", "C:/app/jelly.py")
    cleaned = remove_from_autorun(hook)
    assert cleaned is None
