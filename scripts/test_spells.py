#!/usr/bin/env python3
"""Test spell database."""

import json
import sys
from pathlib import Path

# Configure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

spells_file = Path(r"C:\DnD\DnD_Cursor\rules_database\spells.json")
spells = json.load(open(spells_file, 'r', encoding='utf-8'))

print("[*] Testing Spell Database\n")

# Test 1: Lookup Fireball
print("Test 1: Lookup Fireball")
fireball = spells.get('fireball')
if fireball:
    print(f"  [+] Name: {fireball['name']}")
    print(f"  [+] Level: {fireball['level']}")
    print(f"  [+] School: {fireball['school']}")
    print(f"  [+] Classes: {', '.join(fireball['classes'])}")
else:
    print("  [!] Fireball not found")
print()

# Test 2: Search for healing spells
print("Test 2: Search for healing spells (cure)")
cure_spells = [s for s in spells.values() if 'cure' in s['name'].lower()]
print(f"  [+] Found {len(cure_spells)} spells:")
for s in cure_spells[:5]:
    level_str = "Cantrip" if s['level'] == 0 else f"L{s['level']}"
    print(f"    - {s['name']} ({level_str} {s['school']})")
print()

# Test 3: Count Wizard cantrips
print("Test 3: Count Wizard cantrips")
wizard_cantrips = [s for s in spells.values() if 'Wizard' in s['classes'] and s['level'] == 0]
print(f"  [+] Wizard has {len(wizard_cantrips)} cantrips")
print()

# Test 4: Count concentration spells
print("Test 4: Count concentration spells")
concentration = [s for s in spells.values() if s.get('concentration')]
print(f"  [+] {len(concentration)} spells require concentration")
print()

# Test 5: Spells by school
print("Test 5: Spells by school")
by_school = {}
for spell in spells.values():
    school = spell['school']
    by_school[school] = by_school.get(school, 0) + 1

for school, count in sorted(by_school.items(), key=lambda x: -x[1]):
    print(f"  [+] {school}: {count} spells")
print()

print("[+] Spell database test complete!")

