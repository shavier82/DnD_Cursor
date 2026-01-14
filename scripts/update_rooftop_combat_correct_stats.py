#!/usr/bin/env python3
"""Update rooftop encounter with correct stat blocks from bestiary"""

import json
from datetime import datetime

state_file = r'C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json'

# Read state
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

# Correct stats from bestiary:
# Goblin Psi Commander: AC 16, HP 58 (13d6 + 13)
# Goblin Psi Brawler: AC 15, HP 31 (7d6 + 7)

# Current damage:
# Torgga's Guiding Bolt: 14 damage to Commander
# Commander: 58 - 14 = 44 HP remaining

# Brevin's attack: 20 damage to Brawler 1
# Brawler 1: 31 - 20 = 11 HP remaining
# Wails from the Grave: 6 necrotic to Brawler 2
# Brawler 2: 31 - 6 = 25 HP remaining

# Update rooftop encounter combatants with correct stats
if "rooftop_encounter" not in state:
    state["rooftop_encounter"] = {}

state["rooftop_encounter"]["combatants"] = {
    "Goblin Psi Commander": {
        "hp": 44,  # 58 - 14 = 44
        "max_hp": 58,
        "ac": 16,  # Corrected from 15
        "status": "alive",
        "conditions": [],
        "initiative": 11,
        "type": "goblin_psi_commander",
        "carries": None,  # Dropped sack when hit
        "stats": {
            "str": 12,
            "dex": 19,
            "con": 13,
            "int": 17,
            "wis": 15,
            "cha": 10
        },
        "saving_throws": {"int": 5, "wis": 4},
        "skills": {"stealth": 8},
        "damage_resistances": ["psychic"],
        "challenge": 4,
        "xp": 1100
    },
    "Goblin Psi Brawler 1": {
        "hp": 11,  # 31 - 20 = 11
        "max_hp": 31,
        "ac": 15,
        "status": "alive",
        "conditions": [],
        "initiative": 16,
        "type": "goblin_psi_brawler",
        "stats": {
            "str": 9,
            "dex": 17,
            "con": 12,
            "int": 16,
            "wis": 15,
            "cha": 10
        },
        "saving_throws": {"int": 5, "wis": 4},
        "skills": {"stealth": 7},
        "damage_resistances": ["psychic"],
        "challenge": 2,
        "xp": 450
    },
    "Goblin Psi Brawler 2": {
        "hp": 25,  # 31 - 6 = 25
        "max_hp": 31,
        "ac": 15,
        "status": "alive",
        "conditions": [],
        "initiative": 15,
        "type": "goblin_psi_brawler",
        "stats": {
            "str": 9,
            "dex": 17,
            "con": 12,
            "int": 16,
            "wis": 15,
            "cha": 10
        },
        "saving_throws": {"int": 5, "wis": 4},
        "skills": {"stealth": 7},
        "damage_resistances": ["psychic"],
        "challenge": 2,
        "xp": 450
    }
}

state["rooftop_encounter"]["encounter_ended"] = False
state["rooftop_encounter"]["location"] = "sleeping_giant_rooftop"
state["rooftop_encounter"]["last_updated"] = datetime.now().isoformat()

# Update state
state["last_saved"] = datetime.now().isoformat()

# Write state
with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("OK: Rooftop encounter stats updated with correct bestiary values")
print("  - Goblin Psi Commander: 44/58 HP, AC 16 (alive, took 14 damage)")
print("  - Goblin Psi Brawler 1: 11/31 HP, AC 15 (alive, took 20 damage)")
print("  - Goblin Psi Brawler 2: 25/31 HP, AC 15 (alive, took 6 necrotic damage)")
print("  - Encounter is still active - combat continues")

















