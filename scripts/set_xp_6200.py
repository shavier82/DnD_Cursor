#!/usr/bin/env python3
"""Set all characters' XP to 6200"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from update_sheets_data import load_credentials, get_character_id_from_name, update_character_xp

credentials_path = r'C:\DnD\keys\google_sheets_key.json'
spreadsheet_id = '1Y8qB5v5v5v5v5v5v5v5v5v5v5v5v5v5v5'  # Will be read from config

# Load config
import json
with open(r'C:\DnD\DnD_Cursor\config\sheets_config.json', 'r') as f:
    config = json.load(f)
    spreadsheet_id = config['spreadsheet_id']

credentials = load_credentials(credentials_path)
service = credentials

party = [
    "Brevin",
    "Eglath Bearkiller",
    "Torgga Brawnanvil",
    "Vandross Ephrates",
    "Zephyr Sparkwhistle"
]

target_xp = 6200

for char in party:
    char_id = get_character_id_from_name(char, service, spreadsheet_id)
    if char_id:
        if update_character_xp(service, spreadsheet_id, char_id, target_xp):
            print(f"OK: Set {char} XP to {target_xp}")
        else:
            print(f"ERROR: Failed to update {char} XP")
    else:
        print(f"ERROR: Character '{char}' not found")































