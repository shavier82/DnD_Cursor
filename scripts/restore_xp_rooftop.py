#!/usr/bin/env python3
"""Restore XP to 5800, then add 400 for rooftop encounter = 6200"""

import subprocess
import sys

# Party members
party = [
    "Brevin",
    "Eglath Bearkiller",
    "Torgga Brawnanvil",
    "Vandross Ephrates",
    "Zephyr Sparkwhistle"
]

# Set XP to 6200 (5800 base + 400 from rooftop encounter)
target_xp = 6200

print(f"Setting all characters' XP to {target_xp} (5800 base + 400 rooftop encounter)")

for char in party:
    cmd = f'python C:\\DnD\\DnD_Cursor\\scripts\\update_sheets_data.py xp "{char}" {target_xp}'
    print(f"\nSetting {char} XP to {target_xp}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
    else:
        print(f"  OK: {result.stdout.strip()}")

print("\nOK: XP restoration complete!")































