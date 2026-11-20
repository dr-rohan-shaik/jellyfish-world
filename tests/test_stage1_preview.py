"""Tests for Stage 1: Design Preview, Animation Frames, and Layered Accessories."""
import os
import pytest
from src.core.cosmetics import load_cosmetics_catalog, apply_cosmetics_to_frame
from src.ui.ascii_art import (
    RAW_FRAMES,
    get_animated_frame,
    render_jellyfish_card,
)
from src.ui.palette import is_no_color, is_reduced_motion


def test_cosmetics_catalog_loaded():
    catalog = load_cosmetics_catalog()
    assert "crown" in catalog
    assert "glasses" in catalog
    assert "glow_ring" in catalog

    crown = catalog["crown"]
    assert crown.slot == "hat"
    assert "\\_v_v_/" in crown.line

    glasses = catalog["glasses"]
    assert glasses.slot == "glasses"
    assert "o o" in glasses.replacements

    ring = catalog["glow_ring"]
    assert ring.slot == "glow_ring"
    assert len(ring.rim_brackets) == 2


def test_frame_definitions():
    assert len(RAW_FRAMES) == 4
    for drift, lines in RAW_FRAMES:
        assert isinstance(drift, int)
        assert len(lines) >= 6
        for line in lines:
            assert len(line) > 0


def test_glasses_replacement():
    catalog = load_cosmetics_catalog()
    glasses = catalog["glasses"]

    test_lines = [
        "    /  o o  \\    ",
        "   (   ‿‿    )   ",
        "    '-.___.-'    ",
    ]
    composited = apply_cosmetics_to_frame(test_lines, [glasses])
    assert any("(o)-(o)" in line for line in composited)


def test_crown_hat_layer():
    catalog = load_cosmetics_catalog()
    crown = catalog["crown"]

    test_lines = [
        "     .-~~~-.     ",
        "    /  o o  \\    ",
    ]
    composited = apply_cosmetics_to_frame(test_lines, [crown])
    assert "\\_v_v_/" in composited[0]


def test_glow_ring_brackets():
    catalog = load_cosmetics_catalog()
    ring = catalog["glow_ring"]

    test_lines = [
        "     .-~~~-.     ",
        "    '-.___.-'    ",
    ]
    composited = apply_cosmetics_to_frame(test_lines, [ring])
    assert any(":·*" in line and "*·:" in line for line in composited)


def test_animated_frame_generation():
    for i in range(4):
        rendered = get_animated_frame(frame_idx=i, mood="calm", is_founder=False)
        assert len(rendered.plain) > 0


def test_card_rendering_standard_and_compact():
    # 80x24 standard
    card_80 = render_jellyfish_card(frame_idx=0, terminal_width=80, terminal_height=24)
    assert card_80 is not None

    # 40x20 compact mobile
    card_40 = render_jellyfish_card(frame_idx=0, terminal_width=40, terminal_height=20)
    assert card_40 is not None
    assert card_40.width <= 40


def test_founder_rendering():
    card_founder = render_jellyfish_card(frame_idx=0, number=1, is_founder=True)
    assert "FOUNDER" in str(card_founder.title)


def test_reduced_motion_and_no_color(monkeypatch):
    monkeypatch.setenv("REDUCED_MOTION", "1")
    assert is_reduced_motion() is True

    frame = get_animated_frame(frame_idx=3)
    assert frame is not None

    monkeypatch.setenv("NO_COLOR", "1")
    assert is_no_color() is True
