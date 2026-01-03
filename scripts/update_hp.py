#!/usr/bin/env python3
"""
Update character HP in Google Sheets
"""

import json
import sys
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Google API libraries not installed")
    sys.exit(1)

def load_config():
    """Load sheets config"""
    config_path = Path("C:/DnD/DnD_Cursor/config/sheets_config.json")
    with open(config_path, 'r') as f:
        return json.load(f)

def get_character_row(service, spreadsheet_id, character_name):
    """Find character row in CSV_Characters"""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return None, None
    
    headers = [h.strip().lower() for h in values[0]]
    
    # Name mapping (character_id -> sheet name)
    name_mapping = {
        'brevin': 'brevin',  # Sheet name is "Brevin"
        'brovin': 'brevin',
        'ergath': 'eglath bearkiller',
        'eglath': 'eglath bearkiller'
    }
    
    name_lower = character_name.lower()
    mapped_name = name_mapping.get(name_lower, name_lower)
    
    # Find row - check both character_id (column A) and name (column B)
    for i, row in enumerate(values[1:], start=2):
        if len(row) >= 2:
            char_id = row[0].strip().lower() if len(row) > 0 else ""
            char_name = row[1].strip().lower() if len(row) > 1 else ""
            # Match by name or by character_id
            if char_name == mapped_name or char_id == name_lower.replace(' ', '_'):
                return i, headers
    
    return None, None

def update_hp(character_name, new_hp):
    """Update HP in Google Sheets"""
    config = load_config()
    
    # Load credentials
    credentials = service_account.Credentials.from_service_account_file(
        config['credentials_path'],
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    spreadsheet_id = config['spreadsheet_id']
    
    # Find character row
    row_idx, headers = get_character_row(service, spreadsheet_id, character_name)
    if not row_idx:
        print(f"ERROR: Character '{character_name}' not found in CSV_Characters")
        return False
    
    # Find hp_current column
    if 'hp_current' not in headers:
        print("ERROR: hp_current column not found")
        return False
    
    hp_col_idx = headers.index('hp_current')
    col_letter = chr(65 + hp_col_idx)  # A=0, B=1, etc.
    
    # Update HP
    range_name = f'CSV_Characters!{col_letter}{row_idx}'
    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body={'values': [[str(new_hp)]]}
        ).execute()
        
        print(f"OK: Updated {character_name} HP to {new_hp}")
        return True
    except HttpError as error:
        print(f"ERROR: Failed to update HP: {error}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python update_hp.py <character_name> <new_hp>")
        sys.exit(1)
    
    character_name = sys.argv[1]
    try:
        new_hp = int(sys.argv[2])
    except ValueError:
        print(f"ERROR: Invalid HP value: {sys.argv[2]}")
        sys.exit(1)
    
    if update_hp(character_name, new_hp):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

