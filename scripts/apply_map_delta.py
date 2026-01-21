#!/usr/bin/env python3
"""
Apply Map Delta - Automatically update combat_positions_<location>.json based on MAP-DELTA block.

Parses MAP-DELTA block from DM response and applies the changes to the battlemap JSON file,
creating a backup before modification.

Usage:
    echo "response text" | python scripts/apply_map_delta.py --location t18
    python scripts/apply_map_delta.py --text "response text" --location t18
    python scripts/apply_map_delta.py --dry-run --location t18  # Preview changes without applying
"""

import argparse
import json
import re
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT_DIR / "scripts"
DEFAULT_STATE_FILE = ROOT_DIR / "C:/DnD/Campaigns/Phandelver/saves/CURRENT_STATE.json"

DELTA_BLOCK_PAT = re.compile(
    r"MAP-DELTA\s+(?P<location>[a-zA-Z0-9_\-]+)\s*(?P<body>.*?)\s*END MAP-DELTA",
    re.IGNORECASE | re.DOTALL,
)

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


def get_map_file_path(location_code: str) -> Path:
    """Get battlemap file path for location code"""
    return SCRIPT_DIR / f"combat_positions_{location_code}.json"


def load_map(path: Path) -> Dict[str, Any]:
    """Load battlemap JSON file"""
    if not path.exists():
        print(f"ERROR: map file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: invalid map JSON: {e}", file=sys.stderr)
        sys.exit(1)


def save_map(path: Path, data: Dict[str, Any]) -> None:
    """Save battlemap JSON file"""
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except Exception as e:
        print(f"ERROR: failed to save map file: {e}", file=sys.stderr)
        sys.exit(1)


def create_backup(path: Path) -> Path:
    """Create a backup copy of the map file in a deterministic folder.
    
    Folder: scripts/backups/battlemap/
    Name:   combat_positions_<location>.<timestamp>.json
    """
    backup_dir = path.parent / "backups" / "battlemap"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    location_code = path.stem.replace("combat_positions_", "")
    backup_path = backup_dir / f"combat_positions_{location_code}.{ts}.json"
    shutil.copy2(path, backup_path)
    return backup_path


def parse_delta(text: str) -> Optional[Dict[str, Any]]:
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
        "defeat": []
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
    
    return deltas


def apply_deltas(map_data: Dict[str, Any], deltas: Dict[str, Any]) -> Dict[str, Any]:
    """Apply MAP-DELTA changes to map data"""
    combatants = map_data.get("combatants", {})
    defeated = map_data.get("defeated", [])
    
    # Apply moves
    for combatant_id, x, y in deltas.get("move", []):
        if combatant_id in combatants:
            combatants[combatant_id]["x"] = x
            combatants[combatant_id]["y"] = y
    
    # Apply adds
    for combatant_id, x, y, label, color in deltas.get("add", []):
        combatants[combatant_id] = {
            "x": x,
            "y": y,
            "color": color,
            "label": label
        }
        # Remove from defeated if it was there
        if combatant_id in defeated:
            defeated.remove(combatant_id)
    
    # Apply defeats
    for combatant_id, in deltas.get("defeat", []):
        # Remove from combatants
        if combatant_id in combatants:
            del combatants[combatant_id]
        # Add to defeated if not already there
        if combatant_id not in defeated:
            defeated.append(combatant_id)
    
    map_data["combatants"] = combatants
    map_data["defeated"] = defeated
    
    return map_data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default=None, help="Response text (if omitted, read stdin)")
    ap.add_argument("--location", default=None, help="Location code (e.g., t18). If not provided, inferred from STATE-DELTA block")
    ap.add_argument("--state", default=str(DEFAULT_STATE_FILE), help="Path to CURRENT_STATE.json")
    ap.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    
    text = args.text if args.text is not None else sys.stdin.read()
    if not text.strip():
        if args.dry_run:
            print("DRY-RUN: No MAP-DELTA block found, nothing to apply")
        sys.exit(0)
    
    # Parse delta block
    deltas = parse_delta(text)
    if not deltas:
        if args.dry_run:
            print("DRY-RUN: No MAP-DELTA block found, nothing to apply")
        sys.exit(0)
    
    # Determine location code
    location_code = args.location or deltas["location"]
    if not location_code:
        print("ERROR: Location code not provided and cannot be inferred", file=sys.stderr)
        sys.exit(1)
    
    # Validate location matches state if state file exists
    if not args.location:
        state_file = Path(args.state)
        expected_location = get_location_code_from_state(state_file)
        if expected_location and location_code != expected_location:
            print(f"ERROR: MAP-DELTA location '{location_code}' does not match state location '{expected_location}'", file=sys.stderr)
            sys.exit(1)
    
    # Get map file path
    map_file = get_map_file_path(location_code)
    
    # Load map
    map_data = load_map(map_file)
    
    # Apply deltas
    updated_map = apply_deltas(map_data, deltas)
    
    if args.dry_run:
        print(f"DRY-RUN: Would apply {len(deltas.get('move', []))} moves, {len(deltas.get('add', []))} adds, {len(deltas.get('defeat', []))} defeats")
        sys.exit(0)
    
    # Create backup
    create_backup(map_file)
    
    # Save updated map
    save_map(map_file, updated_map)
    
    # Silent unless verbose
    if args.verbose:
        print(f"Applied map delta to {map_file.name}")
        print(f"  Moves: {len(deltas.get('move', []))}")
        print(f"  Adds: {len(deltas.get('add', []))}")
        print(f"  Defeats: {len(deltas.get('defeat', []))}")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
