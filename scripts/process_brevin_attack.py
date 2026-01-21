#!/usr/bin/env python3
"""Process Brevin's critical hit attack on Goblin3"""

import json
from datetime import datetime

state_file = r'C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json'

# Read state
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

# Critical hit damage calculation
# Base damage rolled: 11 (shortbow) + 2 (arrow) + 3 (sneak) + 5 (wails) = 21
# Critical hit doubles weapon dice, so add: 10 (shortbow) + 4 (arrow) + 7 (sneak) = 21 extra
# Total: 42 damage to Goblin3
# Wails from the Grave: 5 necrotic to second target (Goblin2)

# Update combatants
if "combat" not in state:
    state["combat"] = {}

if "combatants" not in state["combat"]:
    state["combat"]["combatants"] = {}

# Initialize goblins if not present
if "Goblin3" not in state["combat"]["combatants"]:
    state["combat"]["combatants"]["Goblin3"] = {"hp": 7, "max_hp": 7, "ac": 15, "status": "alive", "conditions": []}

if "Goblin2" not in state["combat"]["combatants"]:
    state["combat"]["combatants"]["Goblin2"] = {"hp": 7, "max_hp": 7, "ac": 15, "status": "alive", "conditions": []}

# Apply damage
goblin3 = state["combat"]["combatants"]["Goblin3"]
goblin3["hp"] = 7 - 42  # -35 HP (dead, massive overkill)
goblin3["status"] = "dead"

goblin2 = state["combat"]["combatants"]["Goblin2"]
goblin2["hp"] = 7 - 5  # 2 HP remaining
if goblin2["hp"] <= 0:
    goblin2["status"] = "unconscious" if goblin2["hp"] >= -7 else "dead"
else:
    goblin2["status"] = "alive"

# Update state
state["last_saved"] = datetime.now().isoformat()

# Write state
with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("OK: Brevin's attack processed")
print(f"  - Goblin3: 42 damage (dead)")
print(f"  - Goblin2: 5 necrotic damage (2 HP remaining)")































