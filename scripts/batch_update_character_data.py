#!/usr/bin/env python3
"""
Batch Update Character Data in Google Sheets
Updates HP, spell slots, resources, and other character data in a single batch operation.
This dramatically reduces API calls and speeds up combat processing.
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

# Import helper functions from update_sheets_data.py
sys.path.insert(0, str(Path(__file__).parent))
from update_sheets_data import (
    load_credentials,
    get_character_id_from_name,
    find_row_by_character_id,
    update_character_xp,
    update_character_currency,
    update_character_resources,
    update_character_spell_slots,
    add_inventory_item
)

def batch_update_character_data(
    service,
    spreadsheet_id: str,
    character_id: str,
    updates: Dict[str, Any]
) -> bool:
    """
    Batch update multiple character data fields in a single API call.
    
    Args:
        service: Google Sheets API service object
        spreadsheet_id: Spreadsheet ID
        character_id: Character ID
        updates: Dictionary of updates to apply:
            {
                'hp': <new_hp>,
                'ac': <new_ac>,
                'xp': <new_xp>,
                'currency': {'cp': 0, 'sp': 0, 'ep': 0, 'gp': 0, 'pp': 0},
                'spell_slots': {'1st': {'max': 4, 'remaining': 3}, ...},
                'resources': {'rage': {'max': 3, 'remaining': 2, 'active': False}, ...},
                'inventory': [{'item': '...', 'quantity': 1, ...}, ...]
            }
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Collect all batch update operations
        batch_updates = []
        
        # Update HP if specified
        if 'hp' in updates:
            row_index = find_row_by_character_id(service, spreadsheet_id, 'CSV_Characters', character_id)
            if row_index:
                batch_updates.append({
                    'range': f'CSV_Characters!E{row_index}',  # hp_current column
                    'values': [[str(updates['hp'])]]
                })
        
        # Update AC if specified
        if 'ac' in updates:
            row_index = find_row_by_character_id(service, spreadsheet_id, 'CSV_Characters', character_id)
            if row_index:
                batch_updates.append({
                    'range': f'CSV_Characters!F{row_index}',  # ac column
                    'values': [[str(updates['ac'])]]
                })
        
        # Update XP if specified
        if 'xp' in updates:
            row_index = find_row_by_character_id(service, spreadsheet_id, 'CSV_Characters', character_id)
            if row_index:
                batch_updates.append({
                    'range': f'CSV_Characters!H{row_index}',  # xp column
                    'values': [[str(updates['xp'])]]
                })
        
        # Update currency if specified
        if 'currency' in updates:
            currency = updates['currency']
            row_index = find_row_by_character_id(service, spreadsheet_id, 'CSV_Currency', character_id)
            if row_index:
                # Get headers to find column indices
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range='CSV_Currency!A1:Z1'
                ).execute()
                headers = [h.strip().lower() for h in result.get('values', [[]])[0]]
                
                col_map = {}
                for i, header in enumerate(headers):
                    col_map[header] = i
                
                # Update currency columns
                for currency_type in ['cp', 'sp', 'ep', 'gp', 'pp']:
                    if currency_type in currency and currency_type in col_map:
                        col_letter = chr(65 + col_map[currency_type])  # A=65
                        batch_updates.append({
                            'range': f'CSV_Currency!{col_letter}{row_index}',
                            'values': [[str(currency[currency_type])]]
                        })
        
        # Update spell slots if specified
        if 'spell_slots' in updates:
            for slot_level, slot_data in updates['spell_slots'].items():
                # Find row for this character and slot level
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range='CSV_SpellSlots!A:Z'
                ).execute()
                values = result.get('values', [])
                headers = [h.strip().lower() for h in values[0]] if values else []
                
                char_col = headers.index('character_id') if 'character_id' in headers else 0
                slot_col = headers.index('slot_level') if 'slot_level' in headers else 2
                max_col = headers.index('max') if 'max' in headers else 3
                rem_col = headers.index('remaining') if 'remaining' in headers else 4
                
                for i, row in enumerate(values[1:], start=2):
                    if (len(row) > char_col and row[char_col].strip().lower() == character_id.lower() and
                        len(row) > slot_col and row[slot_col].strip().lower() == slot_level.lower()):
                        if 'max' in slot_data:
                            max_letter = chr(65 + max_col)
                            batch_updates.append({
                                'range': f'CSV_SpellSlots!{max_letter}{i}',
                                'values': [[str(slot_data['max'])]]
                            })
                        if 'remaining' in slot_data:
                            rem_letter = chr(65 + rem_col)
                            batch_updates.append({
                                'range': f'CSV_SpellSlots!{rem_letter}{i}',
                                'values': [[str(slot_data['remaining'])]]
                            })
                        break
        
        # Update resources if specified (requires individual resource updates)
        # Resources are complex and need individual API calls, but we can batch them
        if 'resources' in updates:
            # Resources will be handled separately via update_character_resources
            # (it already uses batchUpdate internally)
            pass
        
        # Execute batch update
        if batch_updates:
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    'valueInputOption': 'RAW',
                    'data': batch_updates
                }
            ).execute()
        
        # Handle resources separately (uses its own batch update)
        if 'resources' in updates:
            update_character_resources(service, spreadsheet_id, character_id, updates['resources'])
        
        # Handle inventory separately (each item is added individually)
        if 'inventory' in updates:
            for item in updates['inventory']:
                add_inventory_item(
                    service, spreadsheet_id, character_id,
                    item.get('item', ''),
                    quantity=item.get('quantity', 1),
                    item_type=item.get('type', ''),
                    equipped=item.get('equipped', 'No'),
                    notes=item.get('notes', ''),
                    weight_lbs=item.get('weight', '')
                )
        
        return True
    
    except HttpError as error:
        print(f"ERROR: Failed to batch update character data: {error}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Batch update character data in Google Sheets'
    )
    parser.add_argument(
        '--credentials',
        default='C:\\DnD\\keys\\google_sheets_key.json',
        help='Credentials file'
    )
    parser.add_argument(
        '--spreadsheet-id',
        default='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw',
        help='Spreadsheet ID'
    )
    parser.add_argument(
        'character',
        help='Character name'
    )
    parser.add_argument(
        '--json',
        help='Path to JSON file with updates (alternative to command-line flags)'
    )
    parser.add_argument('--hp', type=int, help='New HP value')
    parser.add_argument('--ac', type=int, help='New AC value')
    parser.add_argument('--xp', type=int, help='New XP value')
    parser.add_argument('--cp', type=int, help='Copper pieces')
    parser.add_argument('--sp', type=int, help='Silver pieces')
    parser.add_argument('--ep', type=int, help='Electrum pieces')
    parser.add_argument('--gp', type=int, help='Gold pieces')
    parser.add_argument('--pp', type=int, help='Platinum pieces')
    
    args = parser.parse_args()
    
    if not GOOGLE_AVAILABLE:
        print("ERROR: Google API libraries not installed")
        sys.exit(1)
    
    # Load credentials
    credentials = load_credentials(args.credentials)
    service = build('sheets', 'v4', credentials=credentials)
    
    # Get character ID
    character_id = get_character_id_from_name(args.character, service, args.spreadsheet_id)
    if not character_id:
        print(f"ERROR: Character '{args.character}' not found")
        sys.exit(1)
    
    # Build updates dictionary
    updates = {}
    
    if args.json:
        # Load from JSON file
        with open(args.json, 'r', encoding='utf-8') as f:
            updates = json.load(f)
    else:
        # Build from command-line arguments
        if args.hp is not None:
            updates['hp'] = args.hp
        if args.ac is not None:
            updates['ac'] = args.ac
        if args.xp is not None:
            updates['xp'] = args.xp
        
        currency = {}
        if args.cp is not None:
            currency['cp'] = args.cp
        if args.sp is not None:
            currency['sp'] = args.sp
        if args.ep is not None:
            currency['ep'] = args.ep
        if args.gp is not None:
            currency['gp'] = args.gp
        if args.pp is not None:
            currency['pp'] = args.pp
        if currency:
            updates['currency'] = currency
    
    if not updates:
        print("ERROR: No updates specified")
        parser.print_help()
        sys.exit(1)
    
    # Execute batch update
    if batch_update_character_data(service, args.spreadsheet_id, character_id, updates):
        print(f"OK: Batch updated {args.character}")
    else:
        print("ERROR: Failed to batch update")
        sys.exit(1)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
































