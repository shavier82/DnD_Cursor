#!/usr/bin/env python3
"""
Sync combat status from combat engine to positions JSON file for battlemap display.
This allows the battlemap to show HP tracker, initiative order, and current turn.

Usage:
    python sync_combat_status_to_map.py <combat_id> <positions_json_file>

Example:
    python sync_combat_status_to_map.py 6c23908e-9db4-46a5-9ec7-190d672c0c59 scripts/combat_positions_t17.json
"""

import sys
import json
from pathlib import Path

# Import MCP combat engine (if available)
try:
    import asyncio
    import json as json_lib
    from mcp_servers.combat_engine.combat_server import get_combat_state, CombatStateManager
except ImportError:
    print("WARNING: Could not import combat engine. Manual combat_status update required.", file=sys.stderr)
    CombatStateManager = None


def load_combat_status_from_mcp(combat_id):
    """Load combat status from MCP combat engine"""
    if CombatStateManager is None:
        return None
    
    try:
        manager = CombatStateManager()
        state = manager.get_combat(combat_id)
        if not state:
            return None
        
        # Build combat status structure
        combatants_data = {}
        for cid, combatant in state.combatants.items():
            combatants_data[cid] = {
                "name": combatant.creature.name,
                "hp": f"{combatant.creature.current_hp}/{combatant.creature.max_hp}",
                "hp_percent": combatant.creature.hp_percent,
                "ac": combatant.creature.ac,
                "initiative": combatant.initiative,
                "conditions": combatant.active_conditions,
                "is_alive": combatant.is_alive,
            }
        
        current_turn = state.get_current_combatant()
        
        return {
            "round": state.round_number,
            "current_turn": {
                "creature_id": current_turn.creature.creature_id if current_turn else None,
                "name": current_turn.creature.name if current_turn else None,
                "initiative": current_turn.initiative if current_turn else None,
            },
            "initiative_order": state.initiative_order,
            "combatants": combatants_data,
            "is_active": state.is_active,
        }
    except Exception as e:
        print(f"WARNING: Could not load combat status from MCP: {e}", file=sys.stderr)
        return None


def update_positions_with_combat_status(positions_file, combat_status):
    """Update positions JSON file with combat status data"""
    if not Path(positions_file).exists():
        print(f"ERROR: Positions file not found: {positions_file}", file=sys.stderr)
        return False
    
    with open(positions_file, 'r') as f:
        positions_data = json.load(f)
    
    # Add or update combat_status
    positions_data["combat_status"] = combat_status
    
    # Save updated positions
    with open(positions_file, 'w') as f:
        json.dump(positions_data, f, indent=2)
    
    print(f"SUCCESS: Updated {positions_file} with combat status")
    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: python sync_combat_status_to_map.py <combat_id> <positions_json_file>")
        print("\nExample:")
        print("  python sync_combat_status_to_map.py 6c23908e-9db4-46a5-9ec7-190d672c0c59 scripts/combat_positions_t17.json")
        sys.exit(1)
    
    combat_id = sys.argv[1]
    positions_file = sys.argv[2]
    
    # Try to load from MCP
    combat_status = load_combat_status_from_mcp(combat_id)
    
    if combat_status:
        update_positions_with_combat_status(positions_file, combat_status)
    else:
        print("ERROR: Could not load combat status. Manual update required.", file=sys.stderr)
        print("\nTo manually add combat status, add a 'combat_status' key to your positions JSON:")
        print("""
  "combat_status": {
    "round": 1,
    "current_turn": {
      "creature_id": "torgga_brawnanvil",
      "name": "Torgga Brawnanvil",
      "initiative": 5
    },
    "initiative_order": ["brevin", "torgga_brawnanvil", ...],
    "combatants": {
      "brevin": {
        "name": "Brevin",
        "hp": "32/45",
        "hp_percent": 0.71,
        "ac": 15,
        "initiative": 12,
        "conditions": [],
        "is_alive": true
      },
      ...
    },
    "is_active": true
  }
        """)
        sys.exit(1)


if __name__ == "__main__":
    main()
