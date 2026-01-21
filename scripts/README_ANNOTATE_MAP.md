# Map Annotation Script - Usage Guide

## Quick Start

1. **Have your map image ready** (PNG or JPG format)
   - Example: `C:\DnD\Campaigns\Phandelver\maps\talhundereth.png`

2. **Run the annotation script:**
```bash
python scripts/annotate_combat_map.py "<map_image_path>" "<output_path>" --positions scripts/combat_positions_t17.json
```

**Example:**
```bash
python scripts/annotate_combat_map.py "C:\DnD\Campaigns\Phandelver\maps\talhundereth.png" "C:\DnD\Campaigns\Phandelver\maps\talhundereth_annotated.png" --positions scripts/combat_positions_t17.json
```

## Updating Positions During Combat

### Method 1: Quick Update Script
```bash
python scripts/update_combat_position.py <combatant_id> <new_x> <new_y> <positions_file> <map_image> <output_image>
```

**Example (move Brevin):**
```bash
python scripts/update_combat_position.py brevin 5 18 scripts/combat_positions_t17.json "C:\DnD\Campaigns\Phandelver\maps\talhundereth.png" "C:\DnD\Campaigns\Phandelver\maps\talhundereth_annotated.png"
```

### Method 2: Edit JSON, Then Re-Annotate
1. Edit `scripts/combat_positions_t17.json`
2. Change `x` and `y` values for combatants
3. Run annotation again:
```bash
python scripts/annotate_combat_map.py "<map_image>" "<output_image>" --positions scripts/combat_positions_t17.json --update
```

## Show Movement Trails

To see where combatants have moved:
```bash
python scripts/annotate_combat_map.py "<map_image>" "<output_image>" --positions scripts/combat_positions_t17.json --show-trails
```

## Position File Format

Edit `scripts/combat_positions_t17.json`:
```json
{
  "combatants": {
    "brevin": {
      "x": 3,    ← Grid X coordinate (0-19 for 20-wide map)
      "y": 22,   ← Grid Y coordinate (0-24 for 25-tall map)
      "color": "blue",
      "label": "B"
    },
    ...
  }
}
```

**Coordinates:**
- X: 0 = left edge, 19 = right edge (for 20-square wide map)
- Y: 0 = top edge, 24 = bottom edge (for 25-square tall map)
- Each square = 5 feet

## Tips

- **Party members** = Blue circles
- **Enemies** = Red (Malinia), Orange (Gemmules)
- **Terrain** = Gray (statue), Dark gray (rubble)
- **Elevated** = Malinia shows "↑20ft" indicator
- Movement history is automatically saved to `*_history.json`
