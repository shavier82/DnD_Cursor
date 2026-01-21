#!/usr/bin/env python3
"""
Quick utility to update a single combatant's position in the positions JSON file.
Then re-annotate the map.

Usage:
    python update_combat_position.py <combatant_id> <new_x> <new_y> <positions_file> <map_image> <output_image>

Example:
    python update_combat_position.py brevin 5 15 positions.json map.png map_annotated.png
"""

import sys
from pathlib import Path

# Import from annotate_combat_map
sys.path.insert(0, str(Path(__file__).parent))
from annotate_combat_map import update_combatant_position, annotate_map, load_positions

def main():
    if len(sys.argv) < 7:
        print("Usage: python update_combat_position.py <combatant_id> <new_x> <new_y> <positions_file> <map_image> <output_image>")
        print("\nExample:")
        print("  python update_combat_position.py brevin 5 15 positions.json map.png map_annotated.png")
        sys.exit(1)
    
    combatant_id = sys.argv[1]
    try:
        new_x = int(sys.argv[2])
        new_y = int(sys.argv[3])
    except ValueError:
        print("ERROR: new_x and new_y must be integers", file=sys.stderr)
        sys.exit(1)
    
    positions_file = sys.argv[4]
    map_image = sys.argv[5]
    output_image = sys.argv[6]
    
    # Update position
    if not update_combatant_position(positions_file, combatant_id, new_x, new_y):
        sys.exit(1)
    
    # Re-annotate map
    with open(positions_file, 'r') as f:
        positions_data = json.load(f)
    
    success = annotate_map(map_image, output_image, positions_data, show_trails=True, positions_file=positions_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    import json
    main()
