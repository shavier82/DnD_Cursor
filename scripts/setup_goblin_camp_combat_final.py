#!/usr/bin/env python3
"""Setup combat state for goblin camp encounter with actual initiative"""

import json
import random
from datetime import datetime

state_file = r'C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json'

# Read state
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

# Player initiatives (from user)
player_initiatives = {
    "Brevin": 17,
    "Torgga Brawnanvil": 13,
    "Eglath Bearkiller": 11,
    "Zephyr Sparkwhistle": 4,
    "Vandross Ephrates": 17
}

# Roll enemy initiatives
goblin_initiatives = [random.randint(1, 20) for _ in range(6)]
hobgoblin_initiatives = [random.randint(1, 20) for _ in range(2)]

# Create initiative order
initiative_order = []

# Add players
for name, init in player_initiatives.items():
    initiative_order.append({"name": name, "initiative": init, "type": "player"})

# Add goblins
for i, init in enumerate(goblin_initiatives, 1):
    initiative_order.append({"name": f"Goblin{i}", "initiative": init, "type": "enemy"})

# Add hobgoblins
for i, init in enumerate(hobgoblin_initiatives, 1):
    initiative_order.append({"name": f"Hobgoblin{i}", "initiative": init, "type": "enemy"})

# Sort by initiative (highest first)
initiative_order.sort(key=lambda x: x["initiative"], reverse=True)

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

# Get first turn
first_turn = initiative_order[0]["name"] if initiative_order else None

# Update combat section
state["combat"] = {
    "initiated": True,
    "ended": False,
    "round": 1,
    "current_turn": first_turn,
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
print(f"  - First turn: {first_turn}")
print(f"  - Initiative order:")
for entry in initiative_order:
    print(f"    {entry['name']}: {entry['initiative']} ({entry['type']})")
print(f"  - Frightened enemies: 4 (Goblin1, Goblin4, Goblin5, Hobgoblin1)")

















