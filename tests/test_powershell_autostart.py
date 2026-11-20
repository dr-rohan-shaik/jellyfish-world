"""Unit tests for PowerShell profile injection, backup, and clean removal."""
from pathlib import Path

from src.autostart.powershell import (
    END_MARKER,
    START_MARKER,
    apply_powershell_autostart,
    generate_powershell_block,
    has_jellyfish_block,
    inject_block,
    remove_block,
    remove_powershell_autostart,
)


def test_block_generation():
    block = generate_powershell_block("C:/python.exe", "C:/jelly.py")
    assert START_MARKER in block
    assert END_MARKER in block
    assert "JELLY_SEEN" in block
    assert "vscode" in block
    assert "greet" in block


def test_inject_into_empty_content():
    content = ""
    new_content = inject_block(content, "C:/python.exe", "C:/jelly.py")
    assert has_jellyfish_block(new_content)
    assert START_MARKER in new_content
    assert END_MARKER in new_content


def test_inject_preserves_existing_user_code():
    existing = "function Prompt { 'PS> ' }\nSet-Alias ll Get-ChildItem\n"
    new_content = inject_block(existing, "C:/python.exe", "C:/jelly.py")

    assert "function Prompt" in new_content
    assert "Set-Alias ll" in new_content
    assert has_jellyfish_block(new_content)


def test_inject_is_idempotent():
    existing = "Set-Location C:\\\n"
    once = inject_block(existing, "C:/python.exe", "C:/jelly.py")
    twice = inject_block(once, "C:/python.exe", "C:/jelly.py")

    assert twice.count(START_MARKER) == 1
    assert twice.count(END_MARKER) == 1
    assert "Set-Location C:\\" in twice


def test_remove_leaves_user_code_intact():
    user_header = "Write-Host 'Hello User'\n"
    user_footer = "Set-Alias g git\n"
    profile = inject_block(user_header, "C:/python.exe", "C:/jelly.py") + user_footer

    assert has_jellyfish_block(profile)
    cleaned = remove_block(profile)

    assert not has_jellyfish_block(cleaned)
    assert "Write-Host 'Hello User'" in cleaned
    assert "Set-Alias g git" in cleaned


def test_apply_and_remove_with_backup(tmp_path: Path):
    test_profile = tmp_path / "Microsoft.PowerShell_profile.ps1"
    test_profile.write_text("# Initial user profile\n$env:MY_VAR = '1'\n", encoding="utf-8")

    # Apply
    ok, content, bak = apply_powershell_autostart(test_profile, "C:/python.exe", "C:/jelly.py")
    assert ok is True
    assert bak is not None
    assert bak.exists()
    assert "# Initial user profile" in bak.read_text(encoding="utf-8")
    assert has_jellyfish_block(test_profile.read_text(encoding="utf-8"))

    # Remove
    ok_rem, rem_content, bak2 = remove_powershell_autostart(test_profile)
    assert ok_rem is True
    assert not has_jellyfish_block(test_profile.read_text(encoding="utf-8"))
    assert "$env:MY_VAR = '1'" in test_profile.read_text(encoding="utf-8")
