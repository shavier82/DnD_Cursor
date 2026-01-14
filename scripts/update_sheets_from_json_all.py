#!/usr/bin/env python3
"""Update Google Sheets with all stats from JSON files"""

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

# Find all JSON files
json_files = list(players_dir.glob("*.json"))
json_files = [f for f in json_files if f.stem in ['brevin', 'eglath_bearkiller', 'torgga_brawnanvil', 'vandross_ephrates', 'zephyr_sparkwhistle']]

print("=" * 60)
print("Updating Google Sheets from JSON files")
print("=" * 60)

for json_file in json_files:
    with open(json_file, 'r', encoding='utf-8') as f:
        char_data = json.load(f)
    
    char_name = char_data.get('character_name', '')
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
    if 'hit_points' in char_data and 'maximum' in char_data['hit_points']:
        if 'hp_max' in headers:
            col_index = headers.index('hp_max')
            col_letter = chr(65 + col_index)
            updates.append({
                'range': f'CSV_Characters!{col_letter}{row_index}',
                'values': [[str(char_data['hit_points']['maximum'])]]
            })
            print(f"  HP Max: {char_data['hit_points']['maximum']}")
    
    # AC
    if 'armor_class' in char_data:
        if 'ac' in headers:
            col_index = headers.index('ac')
            col_letter = chr(65 + col_index)
            updates.append({
                'range': f'CSV_Characters!{col_letter}{row_index}',
                'values': [[str(char_data['armor_class'])]]
            })
            print(f"  AC: {char_data['armor_class']}")
    
    # Ability Scores (if columns exist)
    if 'ability_scores' in char_data:
        for ability, score in char_data['ability_scores'].items():
            # Try different column name formats
            col_names = [
                ability.lower(),
                ability[:3].lower(),
                'str' if ability == 'strength' else ability[:3].lower()
            ]
            for col_name in col_names:
                if col_name in headers:
                    col_index = headers.index(col_name)
                    col_letter = chr(65 + col_index)
                    updates.append({
                        'range': f'CSV_Characters!{col_letter}{row_index}',
                        'values': [[str(score)]]
                    })
                    break
    
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
            print(f"  OK: Updated {len(updates)} field(s)")
        except Exception as error:
            print(f"  ERROR: {error}")

print("\n" + "=" * 60)
print("Done!")
print("=" * 60)

















