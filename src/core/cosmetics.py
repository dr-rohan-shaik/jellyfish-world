"""Core cosmetics logic and data layer.

Loads cosmetic items from data files and applies them to ASCII frames.
Pure logic: zero UI imports.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CosmeticItem:
    """Represents an equipable accessory."""
    id: str
    name: str
    slot: str  # 'hat', 'glasses', 'glow_ring'
    description: str
    item_type: str  # 'hat_layer', 'eye_layer', 'ring_layer'
    line: Optional[str] = None
    replacements: Dict[str, str] = field(default_factory=dict)
    rim_brackets: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> CosmeticItem:
        return cls(
            id=data["id"],
            name=data["name"],
            slot=data["slot"],
            description=data.get("description", ""),
            item_type=data.get("type", "generic"),
            line=data.get("line"),
            replacements=data.get("replacements", {}),
            rim_brackets=data.get("rim_brackets", []),
        )


def load_cosmetics_catalog(cosmetics_dir: Optional[Path] = None) -> Dict[str, CosmeticItem]:
    """Load all cosmetic item definitions from the data directory."""
    if cosmetics_dir is None:
        # Default to repo root / data / cosmetics
        cosmetics_dir = Path(__file__).resolve().parent.parent.parent / "data" / "cosmetics"

    catalog: Dict[str, CosmeticItem] = {}
    if not cosmetics_dir.exists():
        return catalog

    for file_path in cosmetics_dir.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                item = CosmeticItem.from_dict(data)
                catalog[item.id] = item
        except Exception:
            continue
    return catalog


def apply_cosmetics_to_frame(
    frame_lines: List[str],
    equipped_items: List[CosmeticItem],
    target_width: int = 21,
) -> List[str]:
    """Composite equipped cosmetics onto a jellyfish ASCII frame.

    Args:
        frame_lines: Raw ASCII lines for a single frame.
        equipped_items: List of CosmeticItem instances to apply.
        target_width: Character width for centering.

    Returns:
        List of modified/composited ASCII lines.
    """
    lines = list(frame_lines)

    # Separate items by slot
    hat = next((item for item in equipped_items if item.slot == "hat"), None)
    glasses = next((item for item in equipped_items if item.slot == "glasses"), None)
    ring = next((item for item in equipped_items if item.slot == "glow_ring"), None)

    # 1. Apply glasses (modifies the eye row)
    if glasses and glasses.replacements:
        new_lines = []
        for line in lines:
            mod_line = line
            for old_eye, new_eye in glasses.replacements.items():
                if old_eye in mod_line:
                    mod_line = mod_line.replace(old_eye, new_eye)
            new_lines.append(mod_line)
        lines = new_lines

    # 2. Apply glow ring (modifies the rim row with brackets)
    if ring and ring.rim_brackets and len(ring.rim_brackets) >= 2:
        prefix, suffix = ring.rim_brackets[0], ring.rim_brackets[1]
        new_lines = []
        for line in lines:
            # Look for bell rim signature '-.___.-' or '--._____.-'
            if "'-." in line or "'--." in line:
                stripped = line.strip()
                # Center rim with brackets
                ringed = f"{prefix}{stripped}{suffix}"
                new_lines.append(ringed.center(target_width))
            else:
                new_lines.append(line)
        lines = new_lines

    # 3. Apply hat (prepends a hat line atop the bell)
    if hat and hat.line:
        lines = [hat.line.center(target_width)] + lines
    else:
        # Keep consistent vertical baseline with empty padding line
        lines = [" " * target_width] + lines

    return lines
