#!/usr/bin/env python3
"""Fix rooftop encounter combat stats with correct HP values"""

import json
from datetime import datetime

state_file = r'C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json'

# Read state
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

# Correct HP values and recalculate damage
# Torgga's Guiding Bolt: 14 damage to Commander
# Commander: 58 HP - 14 = 44 HP remaining (NOT dead!)

# Brevin's attack: 20 damage to Brawler 1
# Brawler 1: 31 HP - 20 = 11 HP remaining (NOT dead!)
# Wails from the Grave: 6 necrotic to Brawler 2
# Brawler 2: 31 HP - 6 = 25 HP remaining (NOT 1 HP!)

# Update combat section if it exists, or create new rooftop encounter section
if "rooftop_encounter" not in state:
    state["rooftop_encounter"] = {}

state["rooftop_encounter"]["combatants"] = {
    "Goblin Psi Commander": {
        "hp": 44,  # 58 - 14 = 44
        "max_hp": 58,
        "ac": 15,  # Need to verify actual AC
        "status": "alive",
        "conditions": [],
        "initiative": 11,
        "type": "goblin_psi_commander",
        "carries": None  # Dropped sack when hit
    },
    "Goblin Psi Brawler 1": {
        "hp": 11,  # 31 - 20 = 11
        "max_hp": 31,
        "ac": 15,  # Need to verify actual AC
        "status": "alive",
        "conditions": [],
        "initiative": 16,
        "type": "goblin_psi_brawler"
    },
    "Goblin Psi Brawler 2": {
        "hp": 25,  # 31 - 6 = 25
        "max_hp": 31,
        "ac": 15,  # Need to verify actual AC
        "status": "alive",
        "conditions": [],
        "initiative": 15,
        "type": "goblin_psi_brawler"
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

print("OK: Rooftop encounter stats corrected")
print("  - Goblin Psi Commander: 44/58 HP (alive, took 14 damage)")
print("  - Goblin Psi Brawler 1: 11/31 HP (alive, took 20 damage)")
print("  - Goblin Psi Brawler 2: 25/31 HP (alive, took 6 necrotic damage)")
print("  - Encounter is still active - goblins have NOT been defeated")

















