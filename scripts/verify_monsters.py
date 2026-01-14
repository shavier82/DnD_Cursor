#!/usr/bin/env python3
"""
Verify Monster Database Coverage
Checks which monsters from the user's list are in the database.
"""

import json
from pathlib import Path

# Load database
db_path = Path(r"C:\DnD\DnD_Cursor\rules_database\monsters.json")
with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

parsed_names = [m['name'] for m in data.values()]

# User's expected monster list (sample - key monsters)
expected_monsters = [
    "Aarakocra Aeromancer",
    "Aarakocra Skirmisher",
    "Aboleth",
    "Goblin Warrior",
    "Goblin Boss",
    "Goblin Hexer",
    "Goblin Minion",
    "Ancient Red Dragon",
    "Young Black Dragon",
    "Dragon Turtle",
    "Tarrasque",
    "Beholder",
    "Mind Flayer",
    "Lich",
    "Vampire",
    "Commoner",
    "Guard",
    "Mage",
    "Priest",
    "Bandit",
    "Berserker",
    "Assassin",
    "Gladiator",
    "Knight",
]

print(f"Total monsters in database: {len(parsed_names)}")
print(f"\nChecking {len(expected_monsters)} key monsters:\n")

found = []
missing = []

for monster in expected_monsters:
    if monster in parsed_names:
        found.append(monster)
        print(f"  [+] {monster}")
    else:
        missing.append(monster)
        print(f"  [-] {monster} (MISSING)")

print(f"\n{'='*50}")
print(f"Found: {len(found)}/{len(expected_monsters)}")
print(f"Missing: {len(missing)}/{len(expected_monsters)}")

if missing:
    print(f"\nMissing monsters:")
    for m in missing:
        print(f"  - {m}")

# Show monster types breakdown
print(f"\n{'='*50}")
print("Monster types in database:")
types = {}
for m in data.values():
    t = m['type']
    types[t] = types.get(t, 0) + 1

for t, count in sorted(types.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {t}: {count}")













