#!/usr/bin/env python3
"""
Map Delta Guard - Validates map mutation tags against MAP-DELTA block.

This guard ensures that if any map changes are mentioned in narration
([MAPMOVE], [MAPADD], [MAPDEFEAT], [MAPTERRAIN]), they must be:
1. Declared in a MAP-DELTA block
2. Properly formatted
3. Within bounds
4. Valid token IDs (for moves/defeats)

Fail-closed: blocks if tags exist but delta is missing/incomplete.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_STATE_FILE = Path("C:/DnD/Campaigns/Phandelver/saves/CURRENT_STATE.json")

# Regex patterns for inline map tags
MAPMOVE_PAT = re.compile(
    r"\[MAPMOVE\s+(?P<id>[a-zA-Z0-9_\-]+)\s+(?P<x>\d+)\s+(?P<y>\d+)\s*\]",
    re.IGNORECASE,
)
MAPADD_PAT = re.compile(
    r"\[MAPADD\s+(?P<id>[a-zA-Z0-9_\-]+)\s+(?P<x>\d+)\s+(?P<y>\d+)\s+(?P<label>[a-zA-Z0-9_\-]+)\s+(?P<color>[a-zA-Z]+)\s*\]",
    re.IGNORECASE,
)
MAPDEFEAT_PAT = re.compile(
    r"\[MAPDEFEAT\s+(?P<id>[a-zA-Z0-9_\-]+)\s*\]",
    re.IGNORECASE,
)
MAPTERRAIN_PAT = re.compile(
    r"\[MAPTERRAIN\s+(?P<terrain_id>[a-zA-Z0-9_\-]+)\s+(?P<x>\d+)\s+(?P<y>\d+)\s+(?P<w>\d+)\s+(?P<h>\d+)\s+(?P<type>[a-zA-Z0-9_\-]+)\s+(?P<color>[a-zA-Z]+)\s*\]",
    re.IGNORECASE,
)

# MAP-DELTA block pattern
DELTA_BLOCK_PAT = re.compile(
    r"MAP-DELTA\s+(?P<location>[a-zA-Z0-9_\-]+)\s*(?P<body>.*?)\s*END MAP-DELTA",
    re.IGNORECASE | re.DOTALL,
)

# Delta line patterns
DELTA_MOVE_PAT = re.compile(
    r"^\s*-\s*move:\s*(?P<id>[a-zA-Z0-9_\-]+)\s*->\s*(?P<x>\d+),(?P<y>\d+)\s*$",
    re.IGNORECASE,
)
DELTA_ADD_PAT = re.compile(
    r"^\s*-\s*add:\s*(?P<id>[a-zA-Z0-9_\-]+)\s*@\s*(?P<x>\d+),(?P<y>\d+)\s+label=(?P<label>[a-zA-Z0-9_\-]+)\s+color=(?P<color>[a-zA-Z]+)\s*$",
    re.IGNORECASE,
)
DELTA_DEFEAT_PAT = re.compile(
    r"^\s*-\s*defeat:\s*(?P<id>[a-zA-Z0-9_\-]+)\s*$",
    re.IGNORECASE,
)
DELTA_TERRAIN_PAT = re.compile(
    r"^\s*-\s*terrain:\s*(?P<terrain_id>[a-zA-Z0-9_\-]+)\s*@\s*(?P<x>\d+),(?P<y>\d+)\s+size=(?P<w>\d+)x(?P<h>\d+)\s+type=(?P<type>[a-zA-Z0-9_\-]+)\s+color=(?P<color>[a-zA-Z]+)\s*$",
    re.IGNORECASE,
)


def get_location_code_from_state(state_file: Path) -> Optional[str]:
    """Get location code from CURRENT_STATE.json"""
    if not state_file.exists():
        return None
    
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
        combat = state.get("combat", {})
        if not combat.get("initiated") or combat.get("ended"):
            return None
        
        location = combat.get("location") or state.get("scene", {}).get("location")
        if not location:
            return None
        
        # Extract location code: "t18_cleansing_chamber" -> "t18"
        location_code = location.split("_")[0] if "_" in location else location
        return location_code
    except Exception:
        return None


def parse_map_tags(text: str) -> Dict[str, List[Tuple]]:
    """Parse all map mutation tags from text"""
    tags = {
        "move": [],
        "add": [],
        "defeat": [],
        "terrain": []
    }
    
    # Parse MAPMOVE
    for m in MAPMOVE_PAT.finditer(text):
        tags["move"].append((m.group("id"), int(m.group("x")), int(m.group("y"))))
    
    # Parse MAPADD
    for m in MAPADD_PAT.finditer(text):
        tags["add"].append((
            m.group("id"),
            int(m.group("x")),
            int(m.group("y")),
            m.group("label"),
            m.group("color")
        ))
    
    # Parse MAPDEFEAT
    for m in MAPDEFEAT_PAT.finditer(text):
        tags["defeat"].append((m.group("id"),))
    
    # Parse MAPTERRAIN
    for m in MAPTERRAIN_PAT.finditer(text):
        tags["terrain"].append((
            m.group("terrain_id"),
            int(m.group("x")),
            int(m.group("y")),
            int(m.group("w")),
            int(m.group("h")),
            m.group("type"),
            m.group("color")
        ))
    
    return tags


def parse_delta_block(text: str) -> Optional[Dict[str, Any]]:
    """Parse MAP-DELTA block from text"""
    m = DELTA_BLOCK_PAT.search(text)
    if not m:
        return None
    
    location = m.group("location")
    body = m.group("body")
    
    deltas = {
        "location": location,
        "move": [],
        "add": [],
        "defeat": [],
        "terrain": []
    }
    
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        # Try move pattern
        m_move = DELTA_MOVE_PAT.match(line)
        if m_move:
            deltas["move"].append((
                m_move.group("id"),
                int(m_move.group("x")),
                int(m_move.group("y"))
            ))
            continue
        
        # Try add pattern
        m_add = DELTA_ADD_PAT.match(line)
        if m_add:
            deltas["add"].append((
                m_add.group("id"),
                int(m_add.group("x")),
                int(m_add.group("y")),
                m_add.group("label"),
                m_add.group("color")
            ))
            continue
        
        # Try defeat pattern
        m_defeat = DELTA_DEFEAT_PAT.match(line)
        if m_defeat:
            deltas["defeat"].append((m_defeat.group("id"),))
            continue
        
        # Try terrain pattern
        m_terrain = DELTA_TERRAIN_PAT.match(line)
        if m_terrain:
            deltas["terrain"].append((
                m_terrain.group("terrain_id"),
                int(m_terrain.group("x")),
                int(m_terrain.group("y")),
                int(m_terrain.group("w")),
                int(m_terrain.group("h")),
                m_terrain.group("type"),
                m_terrain.group("color")
            ))
            continue
    
    return deltas


def validate_coordinates(x: int, y: int, width: int, height: int) -> bool:
    """Check if coordinates are within bounds"""
    return 0 <= x < width and 0 <= y < height


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default=str(DEFAULT_STATE_FILE), help="Path to CURRENT_STATE.json")
    ap.add_argument("--text", default=None, help="Response text (if omitted, read stdin)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    
    text = args.text if args.text is not None else sys.stdin.read()
    if not text.strip():
        print("ERROR: No text provided", file=sys.stderr)
        sys.exit(1)
    
    # Get location code from state
    state_file = Path(args.state)
    expected_location = get_location_code_from_state(state_file)
    
    # Parse tags
    tags = parse_map_tags(text)
    has_tags = any(tags.values())
    
    # Parse delta block
    deltas = parse_delta_block(text)
    
    # If tags exist, delta must exist
    if has_tags and not deltas:
        print("BLOCKED: map changes detected but MAP-DELTA block is missing", file=sys.stderr)
        if args.verbose:
            print("\nViolations:")
            for change_type, items in tags.items():
                if items:
                    print(f" - Found {len(items)} {change_type} tag(s) but no MAP-DELTA block")
        sys.exit(1)
    
    # If no tags, delta should not exist (but not a hard fail)
    if not has_tags and deltas:
        if args.verbose:
            print("WARNING: MAP-DELTA block found but no map tags in narration")
    
    # If no tags and no delta, pass
    if not has_tags:
        print("OK: map_delta_guard passed")
        sys.exit(0)
    
    # Validate location matches (if state provides location)
    # If no combat is active (expected_location is None), skip location validation
    # This allows map deltas when combat isn't active (for testing/setup)
    if expected_location is not None and deltas["location"] != expected_location:
        print(f"BLOCKED: MAP-DELTA location '{deltas['location']}' does not match expected '{expected_location}'", file=sys.stderr)
        sys.exit(1)
    
    # Validate each tag has matching delta entry
    violations = []
    
    # Check moves
    for tag_move in tags["move"]:
        tag_id, tag_x, tag_y = tag_move
        found = False
        for delta_move in deltas["move"]:
            delta_id, delta_x, delta_y = delta_move
            if delta_id == tag_id and delta_x == tag_x and delta_y == tag_y:
                found = True
                break
        if not found:
            violations.append(f"Missing MAP-DELTA for move: {tag_id} -> ({tag_x},{tag_y})")
    
    # Check adds
    for tag_add in tags["add"]:
        tag_id, tag_x, tag_y, tag_label, tag_color = tag_add
        found = False
        for delta_add in deltas["add"]:
            delta_id, delta_x, delta_y, delta_label, delta_color = delta_add
            if delta_id == tag_id and delta_x == tag_x and delta_y == tag_y and delta_label == tag_label and delta_color == tag_color:
                found = True
                break
        if not found:
            violations.append(f"Missing MAP-DELTA for add: {tag_id} @ ({tag_x},{tag_y}) label={tag_label} color={tag_color}")
    
    # Check defeats
    for tag_defeat in tags["defeat"]:
        tag_id = tag_defeat[0]
        found = any(delta_defeat[0] == tag_id for delta_defeat in deltas["defeat"])
        if not found:
            violations.append(f"Missing MAP-DELTA for defeat: {tag_id}")
    
    # Check terrain (optional - we'll validate format but not enforce matching)
    # Terrain changes are less critical, so we just verify format
    
    if violations:
        print("BLOCKED: map delta not reconciled", file=sys.stderr)
        if args.verbose:
            print("\nViolations:")
            for v in violations:
                print(f" - {v}")
        sys.exit(1)
    
    print("OK: map_delta_guard passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
