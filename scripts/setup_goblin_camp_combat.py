#!/usr/bin/env python3
"""Setup combat state for goblin camp encounter"""

import json
import random
from datetime import datetime

state_file = r'C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json'

# Read state
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

# Initiative order (from previous rolls)
initiative_order = [
    {"name": "Goblin3", "initiative": 19, "type": "enemy"},
    {"name": "Goblin4", "initiative": 16, "type": "enemy"},
    {"name": "Eglath Bearkiller", "initiative": 14, "type": "player"},
    {"name": "Hobgoblin1", "initiative": 13, "type": "enemy"},
    {"name": "Goblin5", "initiative": 12, "type": "enemy"},
    {"name": "Zephyr Sparkwhistle", "initiative": 11, "type": "player"},
    {"name": "Goblin6", "initiative": 11, "type": "enemy"},
    {"name": "Hobgoblin2", "initiative": 10, "type": "enemy"},
    {"name": "Goblin1", "initiative": 9, "type": "enemy"},
    {"name": "Goblin2", "initiative": 9, "type": "enemy"},
    {"name": "Brevin", "initiative": 6, "type": "player"},
    {"name": "Vandross Ephrates", "initiative": 5, "type": "player"},
    {"name": "Torgga Brawnanvil", "initiative": 1, "type": "player"}
]

# Combatants
combatants = {
    "Brevin": {"hp": 27, "max_hp": 27, "ac": 15, "status": "alive", "conditions": []},
    "Eglath Bearkiller": {"hp": 33, "max_hp": 33, "ac": 18, "status": "alive", "conditions": []},
    "Torgga Brawnanvil": {"hp": 39, "max_hp": 39, "ac": 20, "status": "alive", "conditions": []},
    "Vandross Ephrates": {"hp": 31, "max_hp": 31, "ac": 19, "status": "alive", "conditions": []},
    "Zephyr Sparkwhistle": {"hp": 26, "max_hp": 26, "ac": 13, "status": "alive", "conditions": []},
    "Goblin1": {"hp": 7, "max_hp": 7, "ac": 15, "status": "alive", "conditions": ["Frightened"]},
    "Goblin2": {"hp": 7, "max_hp": 7, "ac": 15, "status": "alive", "conditions": []},
    "Goblin3": {"hp": 7, "max_hp": 7, "ac": 15, "status": "alive", "conditions": []},
    "Goblin4": {"hp": 7, "max_hp": 7, "ac": 15, "status": "alive", "conditions": ["Frightened"]},
    "Goblin5": {"hp": 7, "max_hp": 7, "ac": 15, "status": "alive", "conditions": ["Frightened"]},
    "Goblin6": {"hp": 7, "max_hp": 7, "ac": 15, "status": "alive", "conditions": []},
    "Hobgoblin1": {"hp": 11, "max_hp": 11, "ac": 18, "status": "alive", "conditions": ["Frightened"]},
    "Hobgoblin2": {"hp": 11, "max_hp": 11, "ac": 18, "status": "alive", "conditions": []}
}

# Generate dice pools
dice_pools = {}
for i in range(1, 7):
    goblin_name = f"Goblin{i}"
    dice_pools[goblin_name] = {
        "hit_pool": [random.randint(1, 20) + 4 for _ in range(25)],
        "damage_pool": [random.randint(1, 6) + 2 for _ in range(25)],
        "hit_index": 0,
        "damage_index": 0
    }

for i in range(1, 3):
    hobgoblin_name = f"Hobgoblin{i}"
    dice_pools[hobgoblin_name] = {
        "hit_pool": [random.randint(1, 20) + 3 for _ in range(25)],
        "damage_pool": [random.randint(1, 8) + 1 for _ in range(25)],
        "hit_index": 0,
        "damage_index": 0
    }

# Update combat section
state["combat"] = {
    "initiated": True,
    "ended": False,
    "round": 1,
    "current_turn": "Goblin3",
    "location": "goblin_camp_northeast_cragmaw",
    "surprise_round": False,
    "surprised": [],
    "not_surprised": [],
    "initiative_order": initiative_order,
    "combatants": combatants,
    "dice_pools": dice_pools,
    "turn_narratives": []
}

# Update state
state["last_saved"] = datetime.now().isoformat()

# Write state
with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("OK: Combat state setup complete")
print(f"  - Initiative order: {len(initiative_order)} combatants")
print(f"  - Combatants: {len(combatants)}")
print(f"  - Dice pools: {len(dice_pools)} enemies")
print(f"  - Frightened enemies: 4 (Goblin1, Goblin4, Goblin5, Hobgoblin1)")

















