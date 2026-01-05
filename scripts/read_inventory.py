#!/usr/bin/env python3
"""Read inventory items from CSV_Inventory sheet"""

import json
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

def main():
    creds_path = 'C:\\DnD\\keys\\google_sheets_key.json'
    spreadsheet_id = '1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw'
    
    with open(creds_path, 'r') as f:
        creds_data = json.load(f)
    
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Inventory!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if not values:
        print("No inventory data found")
        return
    
    headers = [h.strip().lower() for h in values[0]]
    
    name_idx = headers.index('name') if 'name' in headers else -1
    item_idx = headers.index('now') if 'now' in headers else (headers.index('now ') if 'now ' in headers else -1)
    qty_idx = headers.index('quantity') if 'quantity' in headers else -1
    notes_idx = headers.index('notes') if 'notes' in headers else -1
    
    dragon_items = []
    
    for row in values[1:]:
        if item_idx < 0 or len(row) <= item_idx:
            continue
        
        item_name = row[item_idx].lower() if item_idx >= 0 and len(row) > item_idx else ''
        notes = row[notes_idx].lower() if notes_idx >= 0 and len(row) > notes_idx else ''
        
        # Check if it's dragon-related
        if any(term in item_name for term in ['dragon', 'scale', 'bone', 'hide', 'venomfang', 'green']) or 'venomfang' in notes:
            character = row[name_idx] if name_idx >= 0 and len(row) > name_idx else 'Unknown'
            item = row[item_idx] if item_idx >= 0 and len(row) > item_idx else ''
            quantity = row[qty_idx] if qty_idx >= 0 and len(row) > qty_idx else '1'
            notes_full = row[notes_idx] if notes_idx >= 0 and len(row) > notes_idx else ''
            
            dragon_items.append({
                'character': character,
                'item': item,
                'quantity': quantity,
                'notes': notes_full
            })
    
    print(json.dumps(dragon_items, indent=2))

if __name__ == '__main__':
    main()

