#!/usr/bin/env python3
"""Update inventory item quantity in CSV_Inventory"""

import json
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def update_item_quantity(character_name, item_name, new_quantity, spreadsheet_id='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw'):
    """Update quantity of an inventory item"""
    creds_path = 'C:\\DnD\\keys\\google_sheets_key.json'
    
    with open(creds_path, 'r') as f:
        creds_data = json.load(f)
    
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    
    # Get all inventory items
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Inventory!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if not values:
        print("No inventory data found")
        return False
    
    headers = [h.strip().lower() for h in values[0]]
    name_idx = headers.index('name') if 'name' in headers else -1
    item_idx = headers.index('now') if 'now' in headers else (headers.index('now ') if 'now ' in headers else -1)
    qty_idx = headers.index('quantity') if 'quantity' in headers else -1
    
    if name_idx < 0 or item_idx < 0 or qty_idx < 0:
        print("ERROR: Required columns not found")
        return False
    
    # Find the item
    for i, row in enumerate(values[1:], start=2):  # Start at row 2 (1-indexed)
        if len(row) > name_idx and len(row) > item_idx:
            if row[name_idx].strip() == character_name and row[item_idx].strip() == item_name:
                # Found it - update quantity
                range_name = f'CSV_Inventory!{chr(65 + qty_idx)}{i}'
                try:
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=range_name,
                        valueInputOption='RAW',
                        body={'values': [[str(new_quantity)]]}
                    ).execute()
                    print(f"OK: Updated {character_name}'s {item_name} quantity to {new_quantity}")
                    return True
                except HttpError as error:
                    print(f"ERROR: Failed to update quantity: {error}")
                    return False
    
    print(f"ERROR: Item '{item_name}' not found for {character_name}")
    return False

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: update_inventory_quantity.py <character_name> <item_name> <new_quantity>")
        sys.exit(1)
    
    character_name = sys.argv[1]
    item_name = sys.argv[2]
    new_quantity = int(sys.argv[3])
    
    update_item_quantity(character_name, item_name, new_quantity)

