#!/usr/bin/env python3
"""
Emergency Character File Restoration Script
Restores corrupted Obsidian character files with correct ability scores and format
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

# Correct ability scores from reference document
CORRECT_STATS = {
    "Torgga_Brawnanvil": {
        "race": "Hill Dwarf",
        "class": "Cleric",
        "level": 5,
        "ability_scores": {"STR": 14, "DEX": 8, "CON": 16, "INT": 10, "WIS": 17, "CHA": 12},
        "ability_modifiers": {"STR": 2, "DEX": -1, "CON": 3, "INT": 0, "WIS": 3, "CHA": 1},
        "ac": 20,
        "initiative": -1,
        "proficiency": 3,
        "hp_max": 48,
        "xp": 8340,  # Approximate from earlier context
        "xp_to_next": 14000
    },
    "Eglath_Bearkiller": {
        "race": "Goliath",
        "class": "Barbarian",
        "level": 5,
        "ability_scores": {"STR": 19, "DEX": 16, "CON": 15, "INT": 12, "WIS": 10, "CHA": 8},
        "ability_modifiers": {"STR": 4, "DEX": 3, "CON": 2, "INT": 1, "WIS": 0, "CHA": -1},
        "ac": 20,
        "initiative": 3,
        "proficiency": 3,
        "hp_max": 50,
        "xp": 8340,
        "xp_to_next": 14000
    },
    "Brevin": {
        "race": "Halfling",
        "class": "Rogue",
        "level": 5,
        "ability_scores": {"STR": 8, "DEX": 17, "CON": 12, "INT": 15, "WIS": 10, "CHA": 15},
        "ability_modifiers": {"STR": -1, "DEX": 3, "CON": 1, "INT": 2, "WIS": 0, "CHA": 2},
        "ac": 15,
        "initiative": 6,
        "proficiency": 3,
        "hp_max": 33,
        "xp": 8340,
        "xp_to_next": 14000
    },
    "Vandross_Ephrates": {
        "race": "Human",
        "class": "Fighter",
        "level": 5,
        "ability_scores": {"STR": 15, "DEX": 16, "CON": 15, "INT": 11, "WIS": 13, "CHA": 9},
        "ability_modifiers": {"STR": 2, "DEX": 3, "CON": 2, "INT": 0, "WIS": 1, "CHA": -1},
        "ac": 19,
        "initiative": 3,
        "proficiency": 3,
        "hp_max": 44,
        "xp": 8340,
        "xp_to_next": 14000
    },
    "Zephyr_Sparkwhistle": {
        "race": "Gnome",
        "class": "Wizard",
        "level": 5,
        "ability_scores": {"STR": 9, "DEX": 15, "CON": 14, "INT": 16, "WIS": 12, "CHA": 10},
        "ability_modifiers": {"STR": -1, "DEX": 2, "CON": 2, "INT": 3, "WIS": 1, "CHA": 0},
        "ac": 13,
        "initiative": 2,
        "proficiency": 3,
        "hp_max": 32,
        "xp": 8340,
        "xp_to_next": 14000
    }
}

OBSIDIAN_VAULT = Path("C:/Users/ksist/Documents/Obsidian/DnD/Player Characters")

def extract_current_data(content: str) -> Dict[str, Any]:
    """Extract current HP, currency, and inventory from corrupted file"""
    data = {
        "hp_current": None,
        "hp_max": None,
        "currency": {"gp": 0, "sp": 0, "cp": 0},
        "inventory_section": None,
        "spell_slots": None,
        "class_resources": None
    }
    
    # Extract HP
    hp_match = re.search(r'\*\*HP:\*\*\s*(\d+)/(\d+)', content)
    if hp_match:
        data["hp_current"] = int(hp_match.group(1))
        data["hp_max"] = int(hp_match.group(2))
    
    # Extract currency
    gp_match = re.search(r'\*\*Gold:\*\*\s*([\d,]+)', content)
    sp_match = re.search(r'\*\*Silver:\*\*\s*([\d,]+)', content)
    cp_match = re.search(r'\*\*Copper:\*\*\s*([\d,]+)', content)
    
    if gp_match:
        data["currency"]["gp"] = int(gp_match.group(1).replace(',', ''))
    if sp_match:
        data["currency"]["sp"] = int(sp_match.group(1).replace(',', ''))
    if cp_match:
        data["currency"]["cp"] = int(cp_match.group(1).replace(',', ''))
    
    # Extract inventory section (everything from "## Inventory" to end)
    inv_match = re.search(r'(## Inventory.*)', content, re.DOTALL)
    if inv_match:
        data["inventory_section"] = inv_match.group(1)
    
    # Extract spell slots section
    spell_match = re.search(r'(## Spell Slots.*?)(?=\n##|\Z)', content, re.DOTALL)
    if spell_match:
        data["spell_slots"] = spell_match.group(1)
    
    # Extract class resources section
    resources_match = re.search(r'(## Class Resources.*?)(?=\n##|\Z)', content, re.DOTALL)
    if resources_match:
        data["class_resources"] = resources_match.group(1)
    
    return data

def restore_character_file(character_name: str):
    """Restore a character file with correct stats"""
    char_file = OBSIDIAN_VAULT / f"{character_name}.md"
    
    if not char_file.exists():
        print(f"ERROR: File not found: {char_file}")
        return False
    
    # Read current (corrupted) file
    current_content = char_file.read_text(encoding='utf-8')
    current_data = extract_current_data(current_content)
    
    # Get correct stats
    stats = CORRECT_STATS.get(character_name)
    if not stats:
        print(f"ERROR: No stats found for {character_name}")
        return False
    
    # Use current HP if available, otherwise use max
    hp_current = current_data.get("hp_current") or stats["hp_max"]
    hp_max = current_data.get("hp_max") or stats["hp_max"]
    
    # Build frontmatter
    frontmatter = f"""---
class: {stats['class']}
level: {stats['level']}
player: null
race: {stats['race']}
tags:
- pc
- character
type: player_character
xp: {stats['xp']}
---

# {character_name.replace('_', ' ')}

## Quick Stats

**Class:** {stats['class']} {stats['level']}
**Race:** {stats['race']}

## Combat Stats

**HP:** {hp_current}/{hp_max}
**AC:** {stats['ac']}
**Initiative:** {stats['initiative']:+d}
**Speed:** 30 ft
**Proficiency Bonus:** +{stats['proficiency']}

## Ability Scores

| Stat | Score | Modifier |
|------|-------|----------|
| STR  | {stats['ability_scores']['STR']} | {stats['ability_modifiers']['STR']:+d} |
| DEX  | {stats['ability_scores']['DEX']} | {stats['ability_modifiers']['DEX']:+d} |
| CON  | {stats['ability_scores']['CON']} | {stats['ability_modifiers']['CON']:+d} |
| INT  | {stats['ability_scores']['INT']} | {stats['ability_modifiers']['INT']:+d} |
| WIS  | {stats['ability_scores']['WIS']} | {stats['ability_modifiers']['WIS']:+d} |
| CHA  | {stats['ability_scores']['CHA']} | {stats['ability_modifiers']['CHA']:+d} |

## Progression

**XP:** {stats['xp']:,} / {stats['xp_to_next']:,}

"""
    
    # Add spell slots if present
    if current_data.get("spell_slots"):
        frontmatter += current_data["spell_slots"] + "\n"
    
    # Add class resources if present
    if current_data.get("class_resources"):
        frontmatter += current_data["class_resources"] + "\n"
    
    # Add currency
    currency = current_data.get("currency", {})
    frontmatter += f"""## Currency

- **Gold:** {currency.get('gp', 0):,} gp
- **Silver:** {currency.get('sp', 0):,} sp
- **Copper:** {currency.get('cp', 0):,} cp

**Total Wealth:** {currency.get('gp', 0) + currency.get('sp', 0)/10 + currency.get('cp', 0)/100:.2f} gp

"""
    
    # Add inventory section (preserve existing)
    if current_data.get("inventory_section"):
        frontmatter += current_data["inventory_section"]
    else:
        frontmatter += "## Inventory\n\n*No inventory data preserved*\n"
    
    # Write restored file
    char_file.write_text(frontmatter, encoding='utf-8')
    print(f"OK: Restored {character_name}")
    return True

def main():
    """Restore all character files"""
    print("Restoring corrupted character files...\n")
    
    for char_name in CORRECT_STATS.keys():
        restore_character_file(char_name)
    
    print("\nRestoration complete!")

if __name__ == "__main__":
    main()
