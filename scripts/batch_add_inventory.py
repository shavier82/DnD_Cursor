#!/usr/bin/env python3
"""
Batch add multiple inventory items in one API call for performance
"""

import json
import sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def batch_add_inventory(character_name, items, spreadsheet_id='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw'):
    """Add multiple inventory items in one batch operation"""
    creds_path = 'C:\\DnD\\keys\\google_sheets_key.json'
    
    with open(creds_path, 'r') as f:
        creds_data = json.load(f)
    
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    
    # Get character_id from CSV_Characters
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A:B'
    ).execute()
    
    values = result.get('values', [])
    character_id = None
    for row in values[1:]:
        if len(row) >= 2 and row[1].strip().lower() == character_name.lower():
            character_id = row[0].strip()
            break
    
    # Name mapping
    name_mapping = {
        'brevin': 'halfling rogue',
        'brovin': 'halfling rogue',
        'ergath': 'eglath bearkiller',
        'eglath': 'eglath bearkiller',
        'vandross': 'vandross ephrates',
        'torgga': 'torgga brawnanvil',
        'zephyr': 'zephyr sparkwhistle'
    }
    
    if not character_id and character_name.lower() in name_mapping:
        mapped = name_mapping[character_name.lower()]
        for row in values[1:]:
            if len(row) >= 2 and row[1].strip().lower() == mapped:
                character_id = row[0].strip()
                break
    
    if not character_id:
        print(f"ERROR: Character '{character_name}' not found")
        return False
    
    # Get actual character name
    actual_name = character_name
    for row in values[1:]:
        if len(row) >= 2 and row[0].strip().lower() == character_id.lower():
            actual_name = row[1].strip()
            break
    
    # Get headers from CSV_Inventory
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Inventory!A1:Z1'
    ).execute()
    
    headers = [h.strip() for h in result.get('values', [[]])[0]]
    
    # Find column indices
    col_map = {}
    for i, header in enumerate(headers):
        col_map[header.lower()] = i
    
    # Build all row data
    all_rows = []
    for item in items:
        row_data = [''] * len(headers)
        
        if 'character_id' in col_map:
            row_data[col_map['character_id']] = character_id
        if 'name' in col_map:
            row_data[col_map['name']] = actual_name
        if 'now ' in col_map:
            row_data[col_map['now ']] = item.get('item', item.get('item_name', ''))
        elif 'now' in col_map:
            row_data[col_map['now']] = item.get('item', item.get('item_name', ''))
        if 'quantity' in col_map:
            row_data[col_map['quantity']] = str(item.get('quantity', 1))
        if 'type' in col_map:
            row_data[col_map['type']] = item.get('type', item.get('item_type', ''))
        if 'equipped' in col_map:
            row_data[col_map['equipped']] = item.get('equipped', 'No')
        if 'notes' in col_map:
            row_data[col_map['notes']] = item.get('notes', '')
        if 'weight_lbs' in col_map:
            row_data[col_map['weight_lbs']] = str(item.get('weight', item.get('weight_lbs', ''))) if item.get('weight') or item.get('weight_lbs') else ''
        
        all_rows.append(row_data)
    
    # Batch append all rows in one API call
    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='CSV_Inventory!A:Z',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': all_rows}
        ).execute()
        print(f"OK: Added {len(items)} items to {actual_name}'s inventory")
        return True
    except HttpError as error:
        print(f"ERROR: Failed to add inventory items: {error}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: batch_add_inventory.py <json_file>")
        print("   or: batch_add_inventory.py <character_name> <items_json_string>")
        sys.exit(1)
    
    # Check if first arg is a file
    if Path(sys.argv[1]).exists():
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
        character_name = data.get('character', '')
        items = data.get('items', [])
    else:
        if len(sys.argv) < 3:
            print("Usage: batch_add_inventory.py <character_name> <items_json>")
            sys.exit(1)
        character_name = sys.argv[1]
        items_json = json.loads(sys.argv[2])
        items = items_json.get('items', items_json) if isinstance(items_json, dict) else items_json
    
    if not character_name or not items:
        print("ERROR: Character name and items required")
        sys.exit(1)
    
    if batch_add_inventory(character_name, items):
        sys.exit(0)
    else:
        sys.exit(1)

