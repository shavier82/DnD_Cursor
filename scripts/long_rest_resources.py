#!/usr/bin/env python3
"""
Reset all character resources after long rest.

Updates:
1. resources_state.json - resets all resources to max
2. Obsidian character sheets - restores spell slots via MCP
3. Syncs to Obsidian with SHA verification

Usage:
    python scripts/long_rest_resources.py
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT_DIR / "scripts"
RESOURCES_FILE = SCRIPT_DIR / "resources_state.json"
MCP_SHIM = SCRIPT_DIR / "mcp_call_shim.py"

# Maximum resources at level 5 (update when characters level up)
MAX_RESOURCES = {
    "brevin": {
        "spell_slots": {},  # Rogue - no spell slots
        "rage": 0,
        "superiority_die": 0,
        "ki": 0,
        "channel_divinity": 0,
        "bardic_inspiration": 0,
        "sorcery_point": 0,
        "wild_shape": 0,
        "maneuver": 0
    },
    "eglath_bearkiller": {
        "spell_slots": {},  # Barbarian - no spell slots
        "rage": 3,  # Barbarian 5: 3 rages per long rest
        "superiority_die": 0,
        "ki": 0,
        "channel_divinity": 0,
        "bardic_inspiration": 0,
        "sorcery_point": 0,
        "wild_shape": 0,
        "maneuver": 0
    },
    "torgga_brawnanvil": {
        "spell_slots": {
            "1": 4,  # Cleric 5: 4/3/2 spell slots
            "2": 3,
            "3": 2
        },
        "rage": 0,
        "superiority_die": 0,
        "ki": 0,
        "channel_divinity": 1,  # Cleric 5: 1 Channel Divinity (restores on short rest)
        "bardic_inspiration": 0,
        "sorcery_point": 0,
        "wild_shape": 0,
        "maneuver": 0
    },
    "zephyr_sparkwhistle": {
        "spell_slots": {
            "1": 4,  # Wizard 5: 4/3/2 spell slots
            "2": 3,
            "3": 2
        },
        "rage": 0,
        "superiority_die": 0,
        "ki": 0,
        "channel_divinity": 0,
        "bardic_inspiration": 0,
        "sorcery_point": 0,
        "wild_shape": 0,
        "maneuver": 0
    },
    "vandross_ephrates": {
        "spell_slots": {},  # Fighter - no spell slots
        "rage": 0,
        "superiority_die": 4,  # Battle Master 5: 4 superiority dice
        "ki": 0,
        "channel_divinity": 0,
        "bardic_inspiration": 0,
        "sorcery_point": 0,
        "wild_shape": 0,
        "maneuver": 0
    }
}

def actor_to_character_name(actor_id: str) -> str:
    """Convert actor_id (e.g., 'zephyr_sparkwhistle') to character name (e.g., 'Zephyr_Sparkwhistle')."""
    parts = actor_id.split('_')
    return '_'.join(part.capitalize() for part in parts)

def reset_spell_slots_obsidian(character_name: str, spell_slots: Dict[str, int]) -> bool:
    """Reset spell slots in Obsidian character sheet via MCP.
    
    Uses the ObsidianSyncServer directly to read and update character files.
    For each spell level, restores all slots to max.
    """
    if not spell_slots:
        return True  # No spell slots to restore
    
    # Import ObsidianSyncServer directly (same as mcp_call_shim.py)
    sys.path.insert(0, str(ROOT_DIR))
    try:
        from mcp_servers.obsidian_sync.obsidian_sync_server import ObsidianSyncServer
    except ImportError:
        # If import fails, skip character sheet update
        return True
    
    try:
        server = ObsidianSyncServer()
        content = server.read_character_file(character_name)
        if not content:
            # Character file not found - skip
            return True
        
        # For each spell level, restore all slots
        import re
        for level_str, max_slots in spell_slots.items():
            level = int(level_str)
            # Pattern: **Level X:** ●●● (3/4)
            pattern = rf'\*\*Level {level}:\*\*\s*([●○]+)\s*\((\d+)/(\d+)\)'
            match = re.search(pattern, content)
            if match:
                # Update to all filled dots (restore all slots)
                new_dots = "●" * max_slots
                replacement = f'**Level {level}:** {new_dots} ({max_slots}/{max_slots})'
                content = re.sub(pattern, replacement, content)
        
        # Write updated content back
        server.write_character_file(character_name, content)
        return True
        
    except Exception:
        # If update fails, just log and continue
        return False

def main() -> int:
    """Reset all resources to max values."""
    if not RESOURCES_FILE.exists():
        print(f"ERROR: resources file not found: {RESOURCES_FILE}", file=sys.stderr)
        return 1
    
    # Load current resources
    try:
        current_resources = json.loads(RESOURCES_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: failed to load resources: {e}", file=sys.stderr)
        return 1
    
    # Reset all resources to max
    reset_resources = json.loads(json.dumps(MAX_RESOURCES))  # Deep copy
    
    # Save reset resources
    try:
        RESOURCES_FILE.write_text(
            json.dumps(reset_resources, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
    except Exception as e:
        print(f"ERROR: failed to save resources: {e}", file=sys.stderr)
        return 1
    
    # Update Obsidian character sheets for spell slots
    for actor_id, resources in reset_resources.items():
        if resources.get("spell_slots"):
            char_name = actor_to_character_name(actor_id)
            reset_spell_slots_obsidian(char_name, resources["spell_slots"])
    
    # Sync to Obsidian
    sync_script = SCRIPT_DIR / "sync_resources_obsidian.py"
    if sync_script.exists():
        proc = subprocess.run(
            [sys.executable, str(sync_script)],
            text=True,
            capture_output=True,
            encoding='utf-8'
        )
        if proc.returncode != 0:
            error = proc.stderr.strip() or proc.stdout.strip()
            print(f"WARNING: Obsidian sync failed: {error}", file=sys.stderr)
            # Don't fail - resources are reset locally
    
    # Silent success (output handled by dm_workflow if called from there)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
