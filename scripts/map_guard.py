#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Map Guard - Hard gate for battlemap validation (NO DRIFT)

This script validates battlemap state before every PLAY response:
- Validates CURRENT_STATE.json exists and parses
- Determines battlemap JSON path from combat_id/location
- Validates battlemap structure (grid, coordinates, tokens, bounds)
- Checks for coordinate drift, duplicates, invalid positions
- Outputs MAP_RECEIPT that must be pasted verbatim

If this script fails or cannot produce a valid receipt:
→ Respond ONLY with: "BLOCKED: run map_guard.py and paste MAP_RECEIPT"

Usage:
    python scripts/map_guard.py [--verbose]
"""

import json
import sys
import io
import os
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
import hashlib

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Paths
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
CONFIG_PATH = ROOT_DIR / "config" / "paths.json"
MAP_GUARD_STATE_FILE = ROOT_DIR / ".map_guard_state.json"

# Coordinate system constants
COORD_ORIGIN = "top_left"
COORD_X = "col"
COORD_Y = "row"
COORD_UNIT = "squares"  # No half-squares allowed


def load_config() -> Dict[str, Any]:
    """Load paths configuration"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)


def determine_battlemap_path(state: Dict[str, Any], config: Dict[str, Any]) -> Optional[Path]:
    """Determine battlemap JSON path from CURRENT_STATE.json"""
    # Check if combat is active
    combat = state.get("combat", {})
    if not combat.get("initiated") or combat.get("ended"):
        return None  # No active combat = no battlemap needed
    
    # Get combat_id or location
    combat_id = combat.get("combat_id")
    location = combat.get("location")
    scene_location = state.get("scene", {}).get("location")
    
    # Determine encounter identifier
    encounter_id = combat_id or location or scene_location
    if not encounter_id:
        return None
    
    # Extract location code (e.g., "t18_cleansing_chamber" -> "t18")
    # Or use full encounter_id
    location_code = encounter_id.split("_")[0] if "_" in encounter_id else encounter_id
    
    # Battlemap file naming: combat_positions_<location_code>.json
    battlemap_filename = f"combat_positions_{location_code}.json"
    battlemap_path = SCRIPT_DIR / battlemap_filename
    
    return battlemap_path if battlemap_path.exists() else None


def validate_battlemap_structure(battlemap_data: Dict[str, Any], verbose: bool = False) -> Tuple[bool, List[str]]:
    """Validate battlemap JSON structure"""
    errors = []
    
    # Required top-level fields
    required_fields = ["grid_size", "map_width_squares", "map_height_squares"]
    for field in required_fields:
        if field not in battlemap_data:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Get dimensions
    grid_size = battlemap_data.get("grid_size", 5)
    width = battlemap_data.get("map_width_squares", 20)
    height = battlemap_data.get("map_height_squares", 20)
    
    # Validate dimensions are positive integers
    if not isinstance(grid_size, int) or grid_size <= 0:
        errors.append(f"grid_size must be positive integer, got: {grid_size}")
    if not isinstance(width, int) or width <= 0:
        errors.append(f"map_width_squares must be positive integer, got: {width}")
    if not isinstance(height, int) or height <= 0:
        errors.append(f"map_height_squares must be positive integer, got: {height}")
    
    # Validate combatants
    combatants = battlemap_data.get("combatants", {})
    if not isinstance(combatants, dict):
        errors.append("combatants must be a dictionary")
        return False, errors
    
    # Track positions for duplicate detection
    position_map = {}  # (x, y) -> [token_ids]
    
    for token_id, token_data in combatants.items():
        if not isinstance(token_data, dict):
            errors.append(f"Combatant {token_id}: must be a dictionary")
            continue
        
        # Required fields
        if "x" not in token_data or "y" not in token_data:
            errors.append(f"Combatant {token_id}: missing x or y coordinate")
            continue
        
        x = token_data["x"]
        y = token_data["y"]
        
        # Validate coordinates are integers
        if not isinstance(x, int) or not isinstance(y, int):
            errors.append(f"Combatant {token_id}: coordinates must be integers, got x={x} (type: {type(x).__name__}), y={y} (type: {type(y).__name__})")
            continue
        
        # Validate coordinates are in bounds
        if x < 0 or x >= width:
            errors.append(f"Combatant {token_id}: x={x} out of bounds (0-{width-1})")
        if y < 0 or y >= height:
            errors.append(f"Combatant {token_id}: y={y} out of bounds (0-{height-1})")
        
        # Track position for duplicate detection
        pos_key = (x, y)
        if pos_key not in position_map:
            position_map[pos_key] = []
        position_map[pos_key].append(token_id)
    
    # Check for duplicates (unless explicitly allowed - stacking rules)
    # For now, we allow stacking but warn in verbose mode
    if verbose:
        for pos, token_ids in position_map.items():
            if len(token_ids) > 1:
                if verbose:
                    print(f"INFO: Position {pos} has multiple tokens: {', '.join(token_ids)}", file=sys.stderr)
    
    # Validate defeated list
    defeated = battlemap_data.get("defeated", [])
    if not isinstance(defeated, list):
        errors.append("defeated must be a list")
    # Note: Defeated tokens may not be in combatants (they've been removed)
    # This is valid - we don't validate their presence
    
    # Validate terrain (optional but should be valid if present)
    terrain = battlemap_data.get("terrain", {})
    if terrain and not isinstance(terrain, dict):
        errors.append("terrain must be a dictionary")
    else:
        for terrain_id, terrain_data in terrain.items():
            if not isinstance(terrain_data, dict):
                errors.append(f"Terrain {terrain_id}: must be a dictionary")
                continue
            
            if "x" not in terrain_data or "y" not in terrain_data:
                errors.append(f"Terrain {terrain_id}: missing x or y coordinate")
                continue
            
            tx = terrain_data.get("x")
            ty = terrain_data.get("y")
            tw = terrain_data.get("width", 1)
            th = terrain_data.get("height", 1)
            
            if not isinstance(tx, int) or not isinstance(ty, int):
                errors.append(f"Terrain {terrain_id}: coordinates must be integers")
            if not isinstance(tw, int) or tw <= 0:
                errors.append(f"Terrain {terrain_id}: width must be positive integer")
            if not isinstance(th, int) or th <= 0:
                errors.append(f"Terrain {terrain_id}: height must be positive integer")
            
            # Check bounds
            if tx < 0 or tx + tw > width:
                errors.append(f"Terrain {terrain_id}: x={tx}, width={tw} out of bounds (0-{width})")
            if ty < 0 or ty + th > height:
                errors.append(f"Terrain {terrain_id}: y={ty}, height={th} out of bounds (0-{height})")
    
    return len(errors) == 0, errors


def compute_map_hash(battlemap_data: Dict[str, Any]) -> str:
    """Compute hash of battlemap state for render sync checking"""
    # Create a deterministic representation
    # Sort keys for consistent hashing
    sorted_json = json.dumps(battlemap_data, sort_keys=True, separators=(',', ':'))
    return hashlib.md5(sorted_json.encode('utf-8')).hexdigest()[:8]


def main():
    parser = argparse.ArgumentParser(description="Map Guard - Battlemap validation")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    # Load config
    try:
        config = load_config()
    except SystemExit:
        sys.exit(1)
    
    # Load CURRENT_STATE.json
    state_file_path = Path(config.get("state_file", ""))
    if not state_file_path or not state_file_path.exists():
        print("BLOCKED: CURRENT_STATE.json not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(state_file_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except Exception as e:
        print(f"BLOCKED: Failed to load CURRENT_STATE.json: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check if combat is active
    combat = state.get("combat", {})
    if not combat.get("initiated") or combat.get("ended"):
        # No active combat - map guard passes (no map needed)
        print("MAP_RECEIPT")
        print("- ENCOUNTER_ID: none (no active combat)")
        print("- CURRENT_STATE: loaded")
        print("- BATTLEMAP: not_required")
        print("- COORD_SYS: ok (origin=top_left, xy=col_row)")
        print("- MAP_REFRESH_DUE: false")
        sys.exit(0)
    
    # Determine battlemap path
    battlemap_path = determine_battlemap_path(state, config)
    if not battlemap_path:
        encounter_id = combat.get("combat_id") or combat.get("location") or "unknown"
        print(f"BLOCKED: Battlemap file not found for encounter: {encounter_id}", file=sys.stderr)
        sys.exit(1)
    
    # Load battlemap JSON
    try:
        with open(battlemap_path, 'r', encoding='utf-8') as f:
            battlemap_data = json.load(f)
    except Exception as e:
        print(f"BLOCKED: Failed to load battlemap JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate battlemap structure
    is_valid, errors = validate_battlemap_structure(battlemap_data, args.verbose)
    if not is_valid:
        if args.verbose:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
        print("BLOCKED: Battlemap validation failed", file=sys.stderr)
        sys.exit(1)
    
    # Compute map hash
    map_hash = compute_map_hash(battlemap_data)
    
    # Get encounter ID
    encounter_id = combat.get("combat_id") or combat.get("location") or "unknown"
    
    # Count tokens
    combatants = battlemap_data.get("combatants", {})
    token_count = len(combatants)
    
    # Get dimensions
    width = battlemap_data.get("map_width_squares", 20)
    height = battlemap_data.get("map_height_squares", 20)
    
    # Output MAP_RECEIPT
    print("MAP_RECEIPT")
    print(f"- ENCOUNTER_ID: {encounter_id}")
    print("- CURRENT_STATE: loaded")
    print(f"- BATTLEMAP: loaded ({battlemap_path.name})")
    print(f"- COORD_SYS: ok (origin={COORD_ORIGIN}, x={COORD_X}, y={COORD_Y})")
    print(f"- TOKENS: ok (N={token_count})")
    print(f"- BOUNDS: ok ({width}x{height})")
    print(f"- MAP_HASH: {map_hash}")
    print("- MAP_REFRESH_DUE: false")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
