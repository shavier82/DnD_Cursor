#!/usr/bin/env python3
"""Award XP and distribute currency from rooftop encounter"""

import subprocess
import sys

# XP values from bestiary:
# Goblin Psi Commander: Challenge 4 (1,100 XP)
# Goblin Psi Brawler: Challenge 2 (450 XP)

xp_commander = 1100
xp_brawler = 450
total_xp = xp_commander + (xp_brawler * 2)  # 1 commander + 2 brawlers
xp_per_character = total_xp // 5  # 5 party members

print(f"Total XP: {total_xp} (Commander: {xp_commander}, 2x Brawlers: {xp_brawler * 2})")
print(f"XP per character: {xp_per_character}")

# Currency: 10 gp, 14 sp, 17 cp
# Distribute evenly among 5 party members
gp_per_char = 10 // 5  # 2 gp each
sp_per_char = 14 // 5  # 2 sp each (4 sp remainder)
cp_per_char = 17 // 5  # 3 cp each (2 cp remainder)

gp_remainder = 10 % 5  # 0
sp_remainder = 14 % 5  # 4 sp
cp_remainder = 17 % 5  # 2 cp

print(f"\nCurrency distribution:")
print(f"Each character: {gp_per_char} gp, {sp_per_char} sp, {cp_per_char} cp")
print(f"Remainder: {gp_remainder} gp, {sp_remainder} sp, {cp_remainder} cp")

# Party members
party = [
    "Brevin",
    "Eglath Bearkiller",
    "Torgga Brawnanvil",
    "Vandross Ephrates",
    "Zephyr Sparkwhistle"
]

# Update XP for each character
for char in party:
    cmd = f'python C:\\DnD\\DnD_Cursor\\scripts\\update_sheets_data.py xp "{char}" {xp_per_character}'
    print(f"\nUpdating {char} XP: +{xp_per_character}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
    else:
        print(f"  OK: {result.stdout.strip()}")

# Update currency for each character (always adds)
for char in party:
    cmd = f'python C:\\DnD\\DnD_Cursor\\scripts\\update_sheets_data.py currency "{char}" --gp {gp_per_char} --sp {sp_per_char} --cp {cp_per_char}'
    print(f"\nUpdating {char} currency: +{gp_per_char} gp, +{sp_per_char} sp, +{cp_per_char} cp")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
    else:
        print(f"  OK: {result.stdout.strip()}")

# Handle remainder - give to first character (Brevin)
if sp_remainder > 0 or cp_remainder > 0:
    print(f"\nDistributing remainder to Brevin: +{sp_remainder} sp, +{cp_remainder} cp")
    cmd = f'python C:\\DnD\\DnD_Cursor\\scripts\\update_sheets_data.py currency "Brevin" --sp {sp_remainder} --cp {cp_remainder}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
    else:
        print(f"  OK: {result.stdout.strip()}")

print("\nOK: XP and currency distribution complete!")

