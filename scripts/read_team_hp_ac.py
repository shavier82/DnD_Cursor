#!/usr/bin/env python3
"""Read team HP and AC from Google Sheets"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from update_sheets_data import load_credentials, get_character_id_from_name, find_row_by_character_id
from googleapiclient.discovery import build

def get_sheets_config():
    """Load sheets config"""
    config_path = Path(__file__).parent.parent / "config" / "sheets_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

# Party members
party = [
    ("Brevin", "halfling_rogue"),
    ("Eglath Bearkiller", "eglath_bearkiller"),
    ("Torgga Brawnanvil", "torgga_brawnanvil"),
    ("Vandross Ephrates", "vandross_ephrates"),
    ("Zephyr Sparkwhistle", "zephyr_sparkwhistle")
]

# Load configs
credentials_path = Path(__file__).parent.parent.parent / "keys" / "google_sheets_key.json"
sheets_config = get_sheets_config()
spreadsheet_id = sheets_config['spreadsheet_id']

# Load credentials
credentials = load_credentials(str(credentials_path))
service = build('sheets', 'v4', credentials=credentials)

# Get headers
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='CSV_Characters!A1:Z1'
).execute()

headers = [h.strip().lower() for h in result.get('values', [[]])[0]]

# Find column indices
hp_current_idx = headers.index('hp_current') if 'hp_current' in headers else None
hp_max_idx = headers.index('hp_max') if 'hp_max' in headers else None
ac_idx = headers.index('ac') if 'ac' in headers else None
level_idx = headers.index('level') if 'level' in headers else None
name_idx = headers.index('character_name') if 'character_name' in headers else 1

print("=" * 60)
print("Team HP and AC Status")
print("=" * 60)
print(f"{'Character':<20} {'Level':<6} {'HP':<12} {'AC':<4}")
print("-" * 60)

# Read all character data
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='CSV_Characters!A:Z'
).execute()

values = result.get('values', [])
if len(values) < 2:
    print("ERROR: No character data found")
    sys.exit(1)

# Find each party member
for char_name, char_id in party:
    for row in values[1:]:  # Skip header
        if len(row) > 0 and row[0].strip().lower() == char_id.lower():
            # Extract values
            level = row[level_idx] if level_idx and level_idx < len(row) else "?"
            hp_current = row[hp_current_idx] if hp_current_idx and hp_current_idx < len(row) else "?"
            hp_max = row[hp_max_idx] if hp_max_idx and hp_max_idx < len(row) else "?"
            ac = row[ac_idx] if ac_idx and ac_idx < len(row) else "?"
            
            # Format HP display
            if hp_current != "?" and hp_max != "?":
                hp_display = f"{hp_current}/{hp_max}"
            elif hp_max != "?":
                hp_display = f"?/{hp_max}"
            elif hp_current != "?":
                hp_display = f"{hp_current}/?"
            else:
                hp_display = "?/?"
            
            print(f"{char_name:<20} {str(level):<6} {hp_display:<12} {str(ac):<4}")
            break
    else:
        print(f"{char_name:<20} {'?':<6} {'?/?':<12} {'?':<4}")

print("=" * 60)

















