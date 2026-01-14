#!/usr/bin/env python3
"""Restore all character resources after long rest"""

import subprocess
import sys

# Party members with their max HP
party = [
    ("Brevin", 33),
    ("Eglath Bearkiller", 50),
    ("Torgga Brawnanvil", 48),
    ("Vandross Ephrates", 44),
    ("Zephyr Sparkwhistle", 32)
]

print("=" * 60)
print("Restoring Character Resources (Long Rest)")
print("=" * 60)

# Restore HP to max
for char_name, max_hp in party:
    print(f"\nRestoring {char_name}...")
    result = subprocess.run(
        ['python', r'C:\DnD\DnD_Cursor\scripts\update_hp.py', char_name, str(max_hp)],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"  OK: HP restored to {max_hp}")
    else:
        print(f"  ERROR: {result.stderr}")

# Restore spell slots for spellcasters
print("\n--- Restoring Spell Slots ---")

# Torgga (Cleric 5): 4/3/2 (1st/2nd/3rd)
print("\nTorgga (Cleric 5):")
subprocess.run(['python', r'C:\DnD\DnD_Cursor\scripts\update_sheets_data.py', 'spellslot', 'Torgga Brawnanvil', '1st', '--max', '4', '--remaining', '4'])
subprocess.run(['python', r'C:\DnD\DnD_Cursor\scripts\update_sheets_data.py', 'spellslot', 'Torgga Brawnanvil', '2nd', '--max', '3', '--remaining', '3'])
subprocess.run(['python', r'C:\DnD\DnD_Cursor\scripts\update_sheets_data.py', 'spellslot', 'Torgga Brawnanvil', '3rd', '--max', '2', '--remaining', '2'])
print("  OK: Spell slots restored (4/3/2)")

# Zephyr (Wizard 5): 4/3/2 (1st/2nd/3rd)
print("\nZephyr (Wizard 5):")
subprocess.run(['python', r'C:\DnD\DnD_Cursor\scripts\update_sheets_data.py', 'spellslot', 'Zephyr Sparkwhistle', '1st', '--max', '4', '--remaining', '4'])
subprocess.run(['python', r'C:\DnD\DnD_Cursor\scripts\update_sheets_data.py', 'spellslot', 'Zephyr Sparkwhistle', '2nd', '--max', '3', '--remaining', '3'])
subprocess.run(['python', r'C:\DnD\DnD_Cursor\scripts\update_sheets_data.py', 'spellslot', 'Zephyr Sparkwhistle', '3rd', '--max', '2', '--remaining', '2'])
print("  OK: Spell slots restored (4/3/2)")

# Restore resources
print("\n--- Restoring Resources ---")

# Eglath (Barbarian 5): Rage 3/3 (level 3-5: 3 uses)
print("\nEglath (Barbarian 5):")
subprocess.run(['python', r'C:\DnD\DnD_Cursor\scripts\update_sheets_data.py', 'resource', 'Eglath Bearkiller', 'rage', '--max', '3', '--remaining', '3'])
print("  OK: Rage restored (3/3)")

# Vandross (Fighter 5): Action Surge 1/1, Second Wind 1/1, Superiority Dice 4/4
print("\nVandross (Fighter 5):")
subprocess.run(['python', r'C:\DnD\DnD_Cursor\scripts\update_sheets_data.py', 'resource', 'Vandross Ephrates', 'action_surge', '--max', '1', '--remaining', '1'])
subprocess.run(['python', r'C:\DnD\DnD_Cursor\scripts\update_sheets_data.py', 'resource', 'Vandross Ephrates', 'second_wind', '--max', '1', '--remaining', '1'])
subprocess.run(['python', r'C:\DnD\DnD_Cursor\scripts\update_sheets_data.py', 'resource', 'Vandross Ephrates', 'superiority_dice', '--max', '4', '--remaining', '4'])
print("  OK: Action Surge, Second Wind, Superiority Dice restored")

print("\n" + "=" * 60)
print("Long Rest Complete - All Resources Restored!")
print("=" * 60)

















