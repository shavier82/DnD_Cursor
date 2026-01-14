#!/usr/bin/env python3
"""Update Zephyr's level to 5 in Google Sheets"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from update_sheets_data import (
    load_credentials, get_character_id_from_name, find_row_by_character_id
)
from googleapiclient.discovery import build

def get_sheets_config():
    """Load sheets config"""
    config_path = Path(__file__).parent.parent / "config" / "sheets_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

import json

# Load configs
credentials_path = Path(__file__).parent.parent.parent / "keys" / "google_sheets_key.json"
sheets_config = get_sheets_config()
spreadsheet_id = sheets_config['spreadsheet_id']

# Load credentials
credentials = load_credentials(str(credentials_path))
service = build('sheets', 'v4', credentials=credentials)

# Find Zephyr's character_id
character_id = get_character_id_from_name("Zephyr Sparkwhistle", service, spreadsheet_id)
if not character_id:
    print("ERROR: Could not find Zephyr Sparkwhistle in CSV_Characters")
    sys.exit(1)

print(f"Found Zephyr: {character_id}")

# Find row
row_index = find_row_by_character_id(service, spreadsheet_id, 'CSV_Characters', character_id)
if not row_index:
    print("ERROR: Could not find row for Zephyr")
    sys.exit(1)

# Get headers
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='CSV_Characters!A1:Z1'
).execute()

headers = [h.strip().lower() for h in result.get('values', [[]])[0]]

# Update level to 5
if 'level' in headers:
    col_index = headers.index('level')
    col_letter = chr(65 + col_index)
    range_name = f'CSV_Characters!{col_letter}{row_index}'
    
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body={'values': [['5']]}
    ).execute()
    print(f"OK: Updated Zephyr's level to 5")

# Update class_level if it exists
if 'class_level' in headers:
    col_index = headers.index('class_level')
    col_letter = chr(65 + col_index)
    range_name = f'CSV_Characters!{col_letter}{row_index}'
    
    # Get current class
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'CSV_Characters!A{row_index}:Z{row_index}'
    ).execute()
    
    values = result.get('values', [[]])[0]
    if 'class' in headers:
        class_col = headers.index('class')
        if class_col < len(values):
            char_class = values[class_col] if class_col < len(values) else 'Wizard'
        else:
            char_class = 'Wizard'
    else:
        char_class = 'Wizard'
    
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body={'values': [[f"{char_class} 5"]]}
    ).execute()
    print(f"OK: Updated Zephyr's class_level to {char_class} 5")

print("Done!")

















