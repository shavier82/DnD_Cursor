#!/usr/bin/env python3
"""
Update Google Sheets CSV_Characters with level 5 stats from imported JSON files
"""

import json
import sys
from pathlib import Path

# Import update_sheets_data functions
sys.path.insert(0, str(Path(__file__).parent))
from update_sheets_data import (
    load_credentials, get_character_id_from_name, find_row_by_character_id
)
from googleapiclient.discovery import build

# Character mapping
CHARACTER_MAPPING = {
    'Brevin': 'halfling_rogue',
    'Eglath Bearkiller': 'eglath_bearkiller',
    'Torgga Brawnanvil': 'torgga_brawnanvil',
    'Vandross Ephrates': 'vandross_ephrates',
    'Zephyr Sparkwhistle': 'zephyr_sparkwhistle'
}

def load_config():
    """Load paths config"""
    config_path = Path(__file__).parent.parent / "config" / "paths.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def get_sheets_config():
    """Load sheets config"""
    config_path = Path(__file__).parent.parent / "config" / "sheets_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def update_character_stats(service, spreadsheet_id, character_id, char_data):
    """Update character stats in CSV_Characters"""
    row_index = find_row_by_character_id(service, spreadsheet_id, 'CSV_Characters', character_id)
    if not row_index:
        print(f"  ERROR: Character ID '{character_id}' not found in CSV_Characters")
        return False
    
    # Get headers to find column indices
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A1:Z1'
    ).execute()
    
    headers = [h.strip().lower() for h in result.get('values', [[]])[0]]
    
    # Build updates
    updates = []
    
    # Level
    if 'level' in char_data:
        if 'level' in headers:
            col_index = headers.index('level')
            col_letter = chr(65 + col_index)
            updates.append({
                'range': f'CSV_Characters!{col_letter}{row_index}',
                'values': [[str(char_data['level'])]]
            })
    
    # AC
    if 'armor_class' in char_data:
        if 'ac' in headers:
            col_index = headers.index('ac')
            col_letter = chr(65 + col_index)
            updates.append({
                'range': f'CSV_Characters!{col_letter}{row_index}',
                'values': [[str(char_data['armor_class'])]]
            })
    
    # HP Max
    if 'hit_points' in char_data and 'maximum' in char_data['hit_points']:
        if 'hp_max' in headers:
            col_index = headers.index('hp_max')
            col_letter = chr(65 + col_index)
            updates.append({
                'range': f'CSV_Characters!{col_letter}{row_index}',
                'values': [[str(char_data['hit_points']['maximum'])]]
            })
    
    # Class/Level combo
    if 'class' in char_data and 'level' in char_data:
        if 'class_level' in headers:
            col_index = headers.index('class_level')
            col_letter = chr(65 + col_index)
            updates.append({
                'range': f'CSV_Characters!{col_letter}{row_index}',
                'values': [[f"{char_data['class']} {char_data['level']}"]]
            })
    
    # Proficiency Bonus
    if 'proficiency_bonus' in char_data:
        if 'proficiency_bonus' in headers:
            col_index = headers.index('proficiency_bonus')
            col_letter = chr(65 + col_index)
            updates.append({
                'range': f'CSV_Characters!{col_letter}{row_index}',
                'values': [[str(char_data['proficiency_bonus'])]]
            })
    
    # Ability Scores (if columns exist)
    if 'ability_scores' in char_data:
        for ability, score in char_data['ability_scores'].items():
            # Try different column name formats
            col_names = [ability.lower(), f'str' if ability == 'strength' else ability[:3].lower()]
            for col_name in col_names:
                if col_name in headers:
                    col_index = headers.index(col_name)
                    col_letter = chr(65 + col_index)
                    updates.append({
                        'range': f'CSV_Characters!{col_letter}{row_index}',
                        'values': [[str(score)]]
                    })
                    break
    
    if not updates:
        print(f"  WARNING: No valid columns to update")
        return False
    
    # Batch update
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
        return True
    except Exception as error:
        print(f"  ERROR: Failed to update: {error}")
        return False

def main():
    print("=" * 60)
    print("Updating Google Sheets with Level 5 Stats")
    print("=" * 60)
    
    # Load configs
    config = load_config()
    sheets_config = get_sheets_config()
    
    players_dir = Path(config['default_campaign_dir']) / "players"
    credentials_path = Path(__file__).parent.parent.parent / "keys" / "google_sheets_key.json"
    spreadsheet_id = sheets_config['spreadsheet_id']
    
    # Load credentials
    credentials = load_credentials(str(credentials_path))
    service = build('sheets', 'v4', credentials=credentials)
    
    # Find all character JSON files
    json_files = list(players_dir.glob("*.json"))
    
    updated_count = 0
    
    for json_file in json_files:
        print(f"\n--- Processing {json_file.name} ---")
        
        # Load character data
        with open(json_file, 'r', encoding='utf-8') as f:
            char_data = json.load(f)
        
        # Get character name
        char_name = char_data.get('character_name') or char_data.get('name') or ''
        if not char_name:
            # Try to infer from filename
            char_name = json_file.stem.replace('_', ' ').title()
            print(f"  Inferred name from filename: {char_name}")
        
        print(f"  Character: {char_name}")
        print(f"  Level: {char_data.get('level', 'N/A')}")
        print(f"  Class: {char_data.get('class', 'N/A')}")
        print(f"  AC: {char_data.get('armor_class', 'N/A')}")
        print(f"  HP Max: {char_data.get('hit_points', {}).get('maximum', 'N/A')}")
        
        # Find character_id
        character_id = None
        for mapped_name, mapped_id in CHARACTER_MAPPING.items():
            if char_name.lower() == mapped_name.lower():
                character_id = mapped_id
                break
        
        if not character_id:
            # Try to find by name in sheets
            character_id = get_character_id_from_name(char_name, service, spreadsheet_id)
        
        if not character_id:
            print(f"  WARNING: Could not find character_id for '{char_name}'")
            continue
        
        print(f"  Character ID: {character_id}")
        
        # Update stats
        if update_character_stats(service, spreadsheet_id, character_id, char_data):
            updated_count += 1
    
    print("\n" + "=" * 60)
    print(f"Update Complete! Updated {updated_count} character(s)")
    print("=" * 60)

if __name__ == '__main__':
    main()

