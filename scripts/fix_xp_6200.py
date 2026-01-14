#!/usr/bin/env python3
"""Set all characters' XP to exactly 6200"""

import subprocess

party = [
    "Brevin",
    "Eglath Bearkiller", 
    "Torgga Brawnanvil",
    "Vandross Ephrates",
    "Zephyr Sparkwhistle"
]

for char in party:
    result = subprocess.run(
        ['python', r'C:\DnD\DnD_Cursor\scripts\update_sheets_data.py', 'xp', char, '6200'],
        capture_output=True,
        text=True
    )
    print(f"{char}: {result.stdout.strip()}")

print("\nVerifying XP values...")
result = subprocess.run(
    ['python', r'C:\DnD\DnD_Cursor\scripts\read_all_xp.py'],
    capture_output=True,
    text=True
)
print(result.stdout)

















