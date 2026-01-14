#!/usr/bin/env python3
"""Update correct HP Max and AC values for all characters"""

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

def load_config():
    """Load paths config"""
    config_path = Path(__file__).parent.parent / "config" / "paths.json"
    with open(config_path, 'r') as f:
        return json.load(f)

# Correct values
correct_stats = {
    'Vandross Ephrates': {'hp_max': 44, 'ac': 19},
    'Brevin': {'hp_max': 33, 'ac': 15},
    'Torgga Brawnanvil': {'hp_max': 48, 'ac': 20},
    'Eglath Bearkiller': {'hp_max': 50, 'ac': 20},
    'Zephyr Sparkwhistle': {'hp_max': 32, 'ac': 13}
}

# Load configs
config = load_config()
players_dir = Path(config['default_campaign_dir']) / "players"
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

print("=" * 60)
print("Updating Correct HP Max and AC Values")
print("=" * 60)

# Update JSON files first
for char_name, stats in correct_stats.items():
    json_file = players_dir / f"{char_name.lower().replace(' ', '_')}.json"
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            char_data = json.load(f)
        
        if 'hit_points' not in char_data:
            char_data['hit_points'] = {}
        char_data['hit_points']['maximum'] = stats['hp_max']
        char_data['armor_class'] = stats['ac']
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(char_data, f, indent=2)
        
        print(f"{char_name}: JSON updated - HP Max: {stats['hp_max']}, AC: {stats['ac']}")

print("\n" + "=" * 60)
print("Updating Google Sheets...")
print("=" * 60)

# Update Google Sheets
for char_name, stats in correct_stats.items():
    print(f"\n--- {char_name} ---")
    
    # Find character_id
    character_id = get_character_id_from_name(char_name, service, spreadsheet_id)
    if not character_id:
        print(f"  ERROR: Character not found in sheets")
        continue
    
    row_index = find_row_by_character_id(service, spreadsheet_id, 'CSV_Characters', character_id)
    if not row_index:
        print(f"  ERROR: Row not found")
        continue
    
    # Build updates
    updates = []
    
    # HP Max
    if 'hp_max' in headers:
        col_index = headers.index('hp_max')
        col_letter = chr(65 + col_index)
        updates.append({
            'range': f'CSV_Characters!{col_letter}{row_index}',
            'values': [[str(stats['hp_max'])]]
        })
    
    # AC
    if 'ac' in headers:
        col_index = headers.index('ac')
        col_letter = chr(65 + col_index)
        updates.append({
            'range': f'CSV_Characters!{col_letter}{row_index}',
            'values': [[str(stats['ac'])]]
        })
    
    if updates:
        body = {
            'valueInputOption': 'RAW',
            'data': updates
        }
        
        try:
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            print(f"  OK: HP Max: {stats['hp_max']}, AC: {stats['ac']}")
        except Exception as error:
            print(f"  ERROR: {error}")

print("\n" + "=" * 60)
print("Update Complete!")
print("=" * 60)

















