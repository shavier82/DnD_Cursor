#!/usr/bin/env python3
"""
Update Google Sheets Data (XP, Currency, Inventory, Resources)
Can update individual fields or sync from local JSON files
"""

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

def get_character_id_from_name(name, service, spreadsheet_id):
    """Find character_id from CSV_Characters by name"""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A:B'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return None
    
    # Name mapping
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

def find_row_by_character_id(service, spreadsheet_id, sheet_name, character_id, id_column=0):
    """Find row index (1-based) for a character_id in a sheet"""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_name}!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return None
    
    for i, row in enumerate(values[1:], start=2):  # Start at row 2 (1-indexed)
        if len(row) > id_column and row[id_column].strip().lower() == character_id.lower():
            return i
    
    return None

def update_character_xp(service, spreadsheet_id, character_id, xp_to_add):
    """Update XP for a character in CSV_Characters
    
    CRITICAL RULE: This function ALWAYS ADDS to current XP (READ → ADD → UPDATE).
    It NEVER overwrites. This prevents data loss.
    
    Args:
        service: Google Sheets service object
        spreadsheet_id: Spreadsheet ID
        character_id: Character ID
        xp_to_add: Amount of XP to ADD to current XP
    """
    # Find the row
    row_index = find_row_by_character_id(service, spreadsheet_id, 'CSV_Characters', character_id)
    if not row_index:
        return False
    
    # Read current XP
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f'CSV_Characters!A{row_index}:Z{row_index}'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values[0]) < 8:
            return False
        
        # XP is column H (index 7)
        current_xp_str = values[0][7].strip().replace(',', '') if len(values[0]) > 7 and values[0][7] else '0'
        try:
            current_xp = int(current_xp_str)
        except (ValueError, TypeError):
            current_xp = 0
        
        # Add new XP
        new_xp = current_xp + xp_to_add
        
        # Update XP
        range_name = f'CSV_Characters!H{row_index}'
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body={'values': [[str(new_xp)]]}
        ).execute()
        return True
    except HttpError as error:
        print(f"ERROR: Failed to update XP: {error}")
        return False
    except Exception as error:
        print(f"ERROR: Failed to read/update XP: {error}")
        return False

def update_character_currency(service, spreadsheet_id, character_id, currency_data):
    """Update currency for a character in CSV_Currency
    
    CRITICAL RULE: This function ALWAYS ADDS to current currency (READ → ADD → UPDATE).
    It NEVER overwrites. This prevents data loss (e.g., zeroing out cp, sp, ep, pp).
    
    Args:
        service: Google Sheets service object
        spreadsheet_id: Spreadsheet ID
        character_id: Character ID
        currency_data: Dict with currency values to ADD {'cp': 0, 'sp': 0, 'ep': 0, 'gp': 0, 'pp': 0}
    """
    # Get headers to find column indices
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Currency!A1:Z1'
    ).execute()
    
    headers = [h.strip().lower() for h in result.get('values', [[]])[0]]
    
    # Find row
    row_index = find_row_by_character_id(service, spreadsheet_id, 'CSV_Currency', character_id)
    if not row_index:
        return False
    
    # CRITICAL: Always read current values first (READ → ADD → UPDATE)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'CSV_Currency!A{row_index}:Z{row_index}'
    ).execute()
    
    row_values = result.get('values', [[]])[0] if result.get('values') else []
    currency_map = {'cp': 'cp', 'sp': 'sp', 'ep': 'ep', 'gp': 'gp', 'pp': 'pp'}
    current_values = {}
    
    # Read current currency values
    for key in currency_map.keys():
        if key in headers:
            col_index = headers.index(key)
            if col_index < len(row_values):
                try:
                    current_values[key] = int(row_values[col_index]) if row_values[col_index] else 0
                except (ValueError, TypeError):
                    current_values[key] = 0
            else:
                current_values[key] = 0
    
    # Build updates (ALWAYS add to current values, never overwrite)
    updates = []
    
    for key, value in currency_data.items():
        if key in currency_map and key in headers:
            col_index = headers.index(key)
            col_letter = chr(65 + col_index)  # A=65
            range_name = f'CSV_Currency!{col_letter}{row_index}'
            
            # ALWAYS add to current value (never overwrite)
            current_amount = current_values.get(key, 0)
            final_value = current_amount + value
            
            updates.append({
                'range': range_name,
                'values': [[str(final_value)]]
            })
    
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
        print(f"ERROR: Failed to update currency: {error}")
        return False

def update_character_resources(service, spreadsheet_id, character_id, resources_data):
    """Update resources for a character in CSV_Resources"""
    # resources_data should be: {'rage': {'max': 3, 'remaining': 2, 'active': False}, ...}
    
    # Get current resources for this character
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Resources!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return False
    
    headers = [h.strip().lower() for h in values[0]]
    
    # Find all rows for this character
    updates = []
    for i, row in enumerate(values[1:], start=2):
        if len(row) > 0 and row[0].strip().lower() == character_id.lower():
            resource_name = row[2].strip().lower() if len(row) > 2 else ''
            
            if resource_name in resources_data:
                res_data = resources_data[resource_name]
                
                # Update max, remaining, active columns
                if 'max' in headers:
                    max_col = headers.index('max')
                    max_letter = chr(65 + max_col)
                    updates.append({
                        'range': f'CSV_Resources!{max_letter}{i}',
                        'values': [[str(res_data.get('max', 0))]]
                    })
                
                if 'remaining' in headers:
                    rem_col = headers.index('remaining')
                    rem_letter = chr(65 + rem_col)
                    updates.append({
                        'range': f'CSV_Resources!{rem_letter}{i}',
                        'values': [[str(res_data.get('remaining', 0))]]
                    })
                
                if 'active' in headers:
                    active_col = headers.index('active')
                    active_letter = chr(65 + active_col)
                    active_value = 'Yes' if res_data.get('active', False) else 'No'
                    updates.append({
                        'range': f'CSV_Resources!{active_letter}{i}',
                        'values': [[active_value]]
                    })
    
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
        print(f"ERROR: Failed to update resources: {error}")
        return False

def update_character_spell_slots(service, spreadsheet_id, character_id, slot_level, max_slots=None, remaining=None):
    """Update spell slots for a character in CSV_SpellSlots"""
    # Get current spell slots for this character
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_SpellSlots!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return False
    
    headers = [h.strip().lower() for h in values[0]]
    
    # Find column indices
    slot_level_col = headers.index('slot_level') if 'slot_level' in headers else None
    max_col = headers.index('max') if 'max' in headers else None
    remaining_col = headers.index('remaining') if 'remaining' in headers else None
    
    if slot_level_col is None:
        return False
    
    # Find the row for this character and slot level
    updates = []
    for i, row in enumerate(values[1:], start=2):
        if len(row) > 0 and row[0].strip().lower() == character_id.lower():
            if len(row) > slot_level_col:
                row_slot_level = row[slot_level_col].strip().lower() if row[slot_level_col] else ''
                if row_slot_level == slot_level.lower():
                    # Found the matching row
                    if max_col is not None and max_slots is not None:
                        max_letter = chr(65 + max_col)
                        updates.append({
                            'range': f'CSV_SpellSlots!{max_letter}{i}',
                            'values': [[str(max_slots)]]
                        })
                    
                    if remaining_col is not None and remaining is not None:
                        rem_letter = chr(65 + remaining_col)
                        updates.append({
                            'range': f'CSV_SpellSlots!{rem_letter}{i}',
                            'values': [[str(remaining)]]
                        })
                    break
    
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
        print(f"ERROR: Failed to update spell slots: {error}")
        return False

def add_inventory_item(service, spreadsheet_id, character_id, item_name, quantity=1, item_type='', equipped='No', notes='', weight_lbs=''):
    """Add an inventory item to CSV_Inventory sheet"""
    # Get character name from CSV_Characters
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A:B'
    ).execute()
    
    values = result.get('values', [])
    character_name = ''
    for row in values[1:]:
        if len(row) >= 2 and row[0].strip().lower() == character_id.lower():
            character_name = row[1].strip()
            break
    
    if not character_name:
        print(f"ERROR: Character ID '{character_id}' not found")
        return False
    
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
    
    # Build row data
    row_data = [''] * len(headers)
    
    # Map columns (note: "Now " has trailing space)
    if 'character_id' in col_map:
        row_data[col_map['character_id']] = character_id
    if 'name' in col_map:
        row_data[col_map['name']] = character_name
    if 'now ' in col_map:  # Note the trailing space
        row_data[col_map['now ']] = item_name
    elif 'now' in col_map:
        row_data[col_map['now']] = item_name
    if 'quantity' in col_map:
        row_data[col_map['quantity']] = str(quantity)
    if 'type' in col_map:
        row_data[col_map['type']] = item_type
    if 'equipped' in col_map:
        row_data[col_map['equipped']] = equipped
    if 'notes' in col_map:
        row_data[col_map['notes']] = notes
    if 'weight_lbs' in col_map:
        row_data[col_map['weight_lbs']] = str(weight_lbs) if weight_lbs else ''
    
    # Append row to CSV_Inventory
    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='CSV_Inventory!A:Z',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [row_data]}
        ).execute()
        return True
    except HttpError as error:
        print(f"ERROR: Failed to add inventory item: {error}")
        return False

def add_inventory_items_batch(service, spreadsheet_id, character_id, items):
    """Add multiple inventory items to CSV_Inventory sheet in one batch operation
    items: list of dicts with keys: item_name, quantity, item_type, equipped, notes, weight_lbs
    """
    # Get character name from CSV_Characters (once)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A:B'
    ).execute()
    
    values = result.get('values', [])
    character_name = ''
    for row in values[1:]:
        if len(row) >= 2 and row[0].strip().lower() == character_id.lower():
            character_name = row[1].strip()
            break
    
    if not character_name:
        print(f"ERROR: Character ID '{character_id}' not found")
        return False
    
    # Get headers from CSV_Inventory (once)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Inventory!A1:Z1'
    ).execute()
    
    headers = [h.strip() for h in result.get('values', [[]])[0]]
    
    # Find column indices (once)
    col_map = {}
    for i, header in enumerate(headers):
        col_map[header.lower()] = i
    
    # Build all row data
    all_rows = []
    for item in items:
        row_data = [''] * len(headers)
        
        # Map columns (note: "Now " has trailing space)
        if 'character_id' in col_map:
            row_data[col_map['character_id']] = character_id
        if 'name' in col_map:
            row_data[col_map['name']] = character_name
        if 'now ' in col_map:  # Note the trailing space
            row_data[col_map['now ']] = item.get('item_name', '')
        elif 'now' in col_map:
            row_data[col_map['now']] = item.get('item_name', '')
        if 'quantity' in col_map:
            row_data[col_map['quantity']] = str(item.get('quantity', 1))
        if 'type' in col_map:
            row_data[col_map['type']] = item.get('item_type', '')
        if 'equipped' in col_map:
            row_data[col_map['equipped']] = item.get('equipped', 'No')
        if 'notes' in col_map:
            row_data[col_map['notes']] = item.get('notes', '')
        if 'weight_lbs' in col_map:
            row_data[col_map['weight_lbs']] = str(item.get('weight_lbs', '')) if item.get('weight_lbs') else ''
        
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
        return True
    except HttpError as error:
        print(f"ERROR: Failed to add inventory items: {error}")
        return False

def sync_from_json(service, spreadsheet_id, json_file_path):
    """Sync character data from local JSON file to sheets"""
    with open(json_file_path, 'r', encoding='utf-8-sig') as f:
        char_data = json.load(f)
    
    char_name = char_data.get('name', '')
    if not char_name:
        print(f"ERROR: Character name not found in {json_file_path}")
        return False
    
    character_id = get_character_id_from_name(char_name, service, spreadsheet_id)
    if not character_id:
        print(f"ERROR: Character '{char_name}' not found in CSV_Characters")
        return False
    
    print(f"[sync] Syncing {char_name} ({character_id})...")
    
    # Update XP
    if 'xp' in char_data:
        if update_character_xp(service, spreadsheet_id, character_id, char_data['xp']):
            print(f"  OK: Updated XP to {char_data['xp']}")
    
    # Update currency
    if 'currency' in char_data:
        if update_character_currency(service, spreadsheet_id, character_id, char_data['currency']):
            print(f"  OK: Updated currency")
    
    # Update resources
    if 'resources' in char_data:
        if update_character_resources(service, spreadsheet_id, character_id, char_data['resources']):
            print(f"  OK: Updated resources")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Update Google Sheets data (XP, Currency, Resources, Spell Slots, Inventory)')
    parser.add_argument('--credentials', default='C:\\DnD\\keys\\google_sheets_key.json', help='Credentials file')
    parser.add_argument('--spreadsheet-id', default='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw', help='Spreadsheet ID')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # XP update
    xp_parser = subparsers.add_parser('xp', help='Update XP')
    xp_parser.add_argument('character', help='Character name')
    xp_parser.add_argument('xp', type=int, help='XP value')
    
    # Currency update
    currency_parser = subparsers.add_parser('currency', help='Update currency')
    currency_parser.add_argument('character', help='Character name')
    currency_parser.add_argument('--cp', type=int, default=0, help='Copper pieces to ADD (always adds, never overwrites)')
    currency_parser.add_argument('--sp', type=int, default=0, help='Silver pieces to ADD (always adds, never overwrites)')
    currency_parser.add_argument('--ep', type=int, default=0, help='Electrum pieces to ADD (always adds, never overwrites)')
    currency_parser.add_argument('--gp', type=int, default=0, help='Gold pieces to ADD (always adds, never overwrites)')
    currency_parser.add_argument('--pp', type=int, default=0, help='Platinum pieces to ADD (always adds, never overwrites)')
    
    # Resource update
    resource_parser = subparsers.add_parser('resource', help='Update resource')
    resource_parser.add_argument('character', help='Character name')
    resource_parser.add_argument('resource_name', help='Resource name (e.g., rage, superiority_dice)')
    resource_parser.add_argument('--max', type=int, help='Max value')
    resource_parser.add_argument('--remaining', type=int, help='Remaining value')
    resource_parser.add_argument('--active', action='store_true', help='Set as active')
    
    # Sync from JSON
    sync_parser = subparsers.add_parser('sync', help='Sync from local JSON file')
    sync_parser.add_argument('json_file', help='Path to character JSON file')
    
    # Inventory add
    inventory_parser = subparsers.add_parser('inventory', help='Add inventory item')
    inventory_parser.add_argument('character', help='Character name')
    inventory_parser.add_argument('item', help='Item name')
    inventory_parser.add_argument('--quantity', type=int, default=1, help='Quantity')
    inventory_parser.add_argument('--type', default='', help='Item type')
    inventory_parser.add_argument('--equipped', default='No', choices=['Yes', 'No'], help='Equipped status')
    inventory_parser.add_argument('--notes', default='', help='Item notes')
    inventory_parser.add_argument('--weight', default='', help='Weight in lbs')
    
    # Spell slots update
    spellslot_parser = subparsers.add_parser('spellslot', help='Update spell slots')
    spellslot_parser.add_argument('character', help='Character name')
    spellslot_parser.add_argument('slot_level', help='Spell slot level (e.g., 1st, 2nd, 3rd)')
    spellslot_parser.add_argument('--max', type=int, help='Max spell slots')
    spellslot_parser.add_argument('--remaining', type=int, help='Remaining spell slots')
    
    args = parser.parse_args()
    
    if not GOOGLE_AVAILABLE:
        print("ERROR: Google API libraries not installed")
        sys.exit(1)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Load credentials
    credentials = load_credentials(args.credentials)
    service = build('sheets', 'v4', credentials=credentials)
    
    if args.command == 'xp':
        character_id = get_character_id_from_name(args.character, service, args.spreadsheet_id)
        if not character_id:
            print(f"ERROR: Character '{args.character}' not found")
            sys.exit(1)
        
        if update_character_xp(service, args.spreadsheet_id, character_id, args.xp):
            print(f"OK: Updated {args.character} XP to {args.xp}")
        else:
            print(f"ERROR: Failed to update XP")
            sys.exit(1)
    
    elif args.command == 'currency':
        character_id = get_character_id_from_name(args.character, service, args.spreadsheet_id)
        if not character_id:
            print(f"ERROR: Character '{args.character}' not found")
            sys.exit(1)
        
        currency_data = {
            'cp': args.cp,
            'sp': args.sp,
            'ep': args.ep,
            'gp': args.gp,
            'pp': args.pp
        }
        
        # CRITICAL: update_character_currency ALWAYS adds to current (never overwrites)
        if update_character_currency(service, args.spreadsheet_id, character_id, currency_data):
            print(f"OK: Added currency to {args.character}")
        else:
            print(f"ERROR: Failed to update currency")
            sys.exit(1)
    
    elif args.command == 'resource':
        character_id = get_character_id_from_name(args.character, service, args.spreadsheet_id)
        if not character_id:
            print(f"ERROR: Character '{args.character}' not found")
            sys.exit(1)
        
        resource_data = {}
        if args.max is not None:
            resource_data['max'] = args.max
        if args.remaining is not None:
            resource_data['remaining'] = args.remaining
        if args.active:
            resource_data['active'] = True
        
        resources = {args.resource_name: resource_data}
        
        if update_character_resources(service, args.spreadsheet_id, character_id, resources):
            print(f"OK: Updated {args.character} {args.resource_name}")
        else:
            print(f"ERROR: Failed to update resource")
            sys.exit(1)
    
    elif args.command == 'sync':
        json_path = Path(args.json_file)
        if not json_path.exists():
            print(f"ERROR: JSON file not found: {json_path}")
            sys.exit(1)
        
        if sync_from_json(service, args.spreadsheet_id, json_path):
            print("OK: Sync completed")
        else:
            print("ERROR: Sync failed")
            sys.exit(1)
    
    elif args.command == 'inventory':
        character_id = get_character_id_from_name(args.character, service, args.spreadsheet_id)
        if not character_id:
            print(f"ERROR: Character '{args.character}' not found")
            sys.exit(1)
        
        if add_inventory_item(service, args.spreadsheet_id, character_id, args.item,
                              quantity=args.quantity, item_type=args.type,
                              equipped=args.equipped, notes=args.notes, weight_lbs=args.weight):
            print(f"OK: Added {args.item} to {args.character}'s inventory")
        else:
            print(f"ERROR: Failed to add inventory item")
            sys.exit(1)
    
    elif args.command == 'spellslot':
        character_id = get_character_id_from_name(args.character, service, args.spreadsheet_id)
        if not character_id:
            print(f"ERROR: Character '{args.character}' not found")
            sys.exit(1)
        
        if update_character_spell_slots(service, args.spreadsheet_id, character_id, args.slot_level,
                                       max_slots=args.max, remaining=args.remaining):
            print(f"OK: Updated {args.character} spell slots ({args.slot_level})")
        else:
            print(f"ERROR: Failed to update spell slots")
            sys.exit(1)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())