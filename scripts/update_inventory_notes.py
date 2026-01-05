#!/usr/bin/env python3
"""Update inventory item notes in CSV_Inventory"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("ERROR: Google API libraries not installed")

def load_credentials(credentials_path):
    """Load service account credentials"""
    with open(credentials_path, 'r') as f:
        creds_data = json.load(f)
    
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return credentials

def get_sheets_service(credentials_path):
    """Build and return a Google Sheets service object"""
    if not GOOGLE_AVAILABLE:
        print("ERROR: Google API libraries not available. Cannot connect to Sheets.")
        sys.exit(1)
    
    try:
        credentials = load_credentials(credentials_path)
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"ERROR: Failed to get Google Sheets service: {e}")
        sys.exit(1)

def get_character_id_from_name(name, service, spreadsheet_id):
    """Find character_id from CSV_Characters by name"""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A:B'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return None
    
    name_mapping = {
        'brevin': 'halfling rogue',
        'brovin': 'halfling rogue',
        'ergath': 'eglath bearkiller'
    }
    
    name_lower = name.lower()
    
    # Direct match
    for row in values[1:]:
        if len(row) >= 2 and row[1].strip().lower() == name_lower:
            return row[0].strip()
    
    # Mapped name
    if name_lower in name_mapping:
        mapped = name_mapping[name_lower]
        for row in values[1:]:
            if len(row) >= 2 and row[1].strip().lower() == mapped:
                return row[0].strip()
    
    return None

def update_inventory_notes(service, spreadsheet_id, character_name, item_name, new_notes, append=False):
    """Update the notes field of an existing inventory item in CSV_Inventory"""
    
    # Get all inventory data
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Inventory!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if not values:
        print("ERROR: No inventory data found.")
        return False
    
    headers = [h.strip().lower() for h in values[0]]
    
    name_col = headers.index('name') if 'name' in headers else -1
    item_col = headers.index('item') if 'item' in headers else (headers.index('now') if 'now' in headers else (headers.index('now ') if 'now ' in headers else -1))
    notes_col = headers.index('notes') if 'notes' in headers else -1
    
    if name_col == -1 or item_col == -1 or notes_col == -1:
        print("ERROR: Required columns (name, item, notes) not found in CSV_Inventory.")
        return False
    
    updates = []
    found_item = False
    
    for i, row in enumerate(values[1:], start=2): # Start from row 2 (1-indexed)
        current_char_name = row[name_col].strip() if len(row) > name_col else ''
        current_item_name = row[item_col].strip() if len(row) > item_col else ''
        
        if current_char_name.lower() == character_name.lower() and current_item_name.lower() == item_name.lower():
            found_item = True
            # Update notes
            if append:
                old_notes = row[notes_col].strip() if len(row) > notes_col else ''
                new_notes_value = f"{new_notes} {old_notes}" if old_notes else new_notes
            else:
                new_notes_value = new_notes
            
            notes_letter = chr(65 + notes_col)
            updates.append({
                'range': f'CSV_Inventory!{notes_letter}{i}',
                'values': [[new_notes_value]]
            })
            break # Assuming one entry per item per character for simplicity
    
    if not found_item:
        print(f"ERROR: Item '{item_name}' not found for character '{character_name}' in inventory.")
        return False
    
    if not updates:
        return False
    
    try:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                'valueInputOption': 'RAW',
                'data': updates
            }
        ).execute()
        return True
    except HttpError as error:
        print(f"ERROR: Failed to update inventory notes: {error}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Update inventory item notes in Google Sheets')
    parser.add_argument('character', help='Character name')
    parser.add_argument('item', help='Item name')
    parser.add_argument('notes', help='New notes text (or text to append if --append is used)')
    parser.add_argument('--append', action='store_true', help='Append notes to existing notes instead of replacing')
    parser.add_argument('--credentials', default='C:\\DnD\\keys\\google_sheets_key.json', help='Credentials file')
    parser.add_argument('--spreadsheet-id', default='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw', help='Spreadsheet ID')
    
    args = parser.parse_args()
    
    service = get_sheets_service(args.credentials)
    
    if update_inventory_notes(service, args.spreadsheet_id, args.character, args.item, args.notes, args.append):
        action = "appended to" if args.append else "updated"
        print(f"OK: {action} notes for {args.character}'s {args.item}")
    else:
        print(f"ERROR: Could not update notes for {args.character}'s {args.item}")
        sys.exit(1)

if __name__ == '__main__':
    main()

