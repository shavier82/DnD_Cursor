#!/usr/bin/env python3
"""
Manage Conditions System
Handles condition_add, condition_remove, condition_tick operations
Uses CSV_Conditions (dictionary) and CSV_ConditionReference (runtime ledger)
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
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

def get_condition_definition(service, spreadsheet_id, condition_name):
    """Get condition definition from CSV_Conditions"""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Conditions!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return None
    
    headers = [h.strip().lower() for h in values[0]]
    
    for row in values[1:]:
        if len(row) > 0 and row[0].strip().lower() == condition_name.lower():
            condition_def = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    condition_def[header] = row[i].strip()
            return condition_def
    
    return None

def add_condition(service, spreadsheet_id, character_id, condition_name, source, 
                  duration_type, duration_value, mechanical_effects=None):
    """Add a condition to CSV_ConditionReference"""
    
    # Get condition definition for defaults
    condition_def = get_condition_definition(service, spreadsheet_id, condition_name)
    
    # Use provided mechanical_effects or inherit from definition
    if mechanical_effects is None or mechanical_effects == "":
        if condition_def and 'mechanical_effects' in condition_def:
            mechanical_effects = condition_def['mechanical_effects']
        else:
            mechanical_effects = ""
    
    # Build duration display string
    duration_map = {
        'rounds': f"{duration_value} rounds",
        'turns': f"{duration_value} turns",
        'minutes': f"{duration_value} minutes",
        'hours': f"{duration_value} hours",
        'until_removed': "until removed",
        'save_ends': "save ends",
        'concentration': "concentration"
    }
    duration_display = duration_map.get(duration_type, str(duration_value))
    
    # Get character name
    char_result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A:B'
    ).execute()
    char_values = char_result.get('values', [])
    character_name = character_id
    for row in char_values[1:]:
        if len(row) >= 2 and row[0].strip().lower() == character_id.lower():
            character_name = row[1].strip()
            break
    
    # Get headers - check if sheet exists and has headers
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='CSV_ConditionReference!A1:Z1'
        ).execute()
        headers = [h.strip().lower() for h in result.get('values', [[]])[0]]
    except HttpError:
        # Sheet might not exist or be empty - create headers
        headers = []
    
    # If sheet is empty or doesn't have proper headers, create them
    if not headers or 'character_id' not in headers:
        # Create header row
        header_row = ['character_id', 'name', 'condition', 'duration_type', 'duration_value', 
                     'duration', 'ticks_remaining', 'source', 'mechanical_effects']
        try:
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='CSV_ConditionReference!A1:I1',
                valueInputOption='RAW',
                body={'values': [header_row]}
            ).execute()
            headers = [h.lower() for h in header_row]
        except HttpError as error:
            print(f"ERROR: Failed to create headers: {error}")
            return False
    
    # Build new row - map to actual column positions
    row_data = [""] * len(headers)
    
    # Map values to columns
    header_map = {
        'character_id': character_id,
        'name': character_name,
        'condition': condition_name,
        'duration_type': duration_type,
        'duration_value': str(duration_value) if duration_value else "",
        'duration': duration_display,
        'ticks_remaining': "" if duration_type in ['until_removed', 'save_ends', 'concentration'] else str(duration_value) if duration_value else "",
        'source': source,
        'mechanical_effects': mechanical_effects
    }
    
    for header, value in header_map.items():
        if header in headers:
            col_index = headers.index(header)
            row_data[col_index] = value
    
    # Append row
    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='CSV_ConditionReference!A:Z',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [row_data]}
        ).execute()
        return True
    except HttpError as error:
        print(f"ERROR: Failed to add condition: {error}")
        return False

def remove_condition(service, spreadsheet_id, character_id, condition_name, source=None):
    """Remove a condition from CSV_ConditionReference"""
    
    # Get all rows
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_ConditionReference!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return False
    
    headers = [h.strip().lower() for h in values[0]]
    
    # Find rows to delete (matching character_id, condition, and optionally source)
    rows_to_delete = []
    for i, row in enumerate(values[1:], start=2):  # Start at row 2 (1-indexed)
        if len(row) > 0:
            row_char_id = row[0].strip().lower() if len(row) > 0 else ""
            row_condition = row[2].strip().lower() if len(row) > 2 else ""
            row_source = row[7].strip().lower() if len(row) > 7 else ""
            
            if (row_char_id == character_id.lower() and 
                row_condition == condition_name.lower()):
                if source is None or row_source == source.lower():
                    rows_to_delete.append(i)
    
    if not rows_to_delete:
        return False
    
    # Delete rows (in reverse order to maintain indices)
    try:
        for row_num in reversed(sorted(rows_to_delete)):
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    'requests': [{
                        'deleteDimension': {
                            'range': {
                                'sheetId': None,  # Will use sheet name
                                'dimension': 'ROWS',
                                'startIndex': row_num - 1,  # 0-indexed
                                'endIndex': row_num
                            }
                        }
                    }]
                }
            ).execute()
        return True
    except HttpError as error:
        print(f"ERROR: Failed to remove condition: {error}")
        return False

def tick_conditions(service, spreadsheet_id, mode='round', amount=1):
    """Tick conditions (decrement ticks_remaining)"""
    
    # Get all active conditions
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_ConditionReference!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return 0
    
    headers = [h.strip().lower() for h in values[0]]
    
    # Find ticks_remaining column
    ticks_col = None
    duration_type_col = None
    for i, header in enumerate(headers):
        if header == 'ticks_remaining':
            ticks_col = i
        if header == 'duration_type':
            duration_type_col = i
    
    if ticks_col is None:
        print("ERROR: ticks_remaining column not found")
        return 0
    
    # Build updates
    updates = []
    rows_to_delete = []
    
    for i, row in enumerate(values[1:], start=2):
        if len(row) <= ticks_col:
            continue
        
        duration_type = row[duration_type_col].strip().lower() if duration_type_col and len(row) > duration_type_col else ""
        ticks_str = row[ticks_col].strip() if len(row) > ticks_col else ""
        
        # Skip conditions that don't tick
        if duration_type in ['until_removed', 'save_ends', 'concentration']:
            continue
        
        # Skip if ticks_remaining is blank
        if not ticks_str:
            continue
        
        try:
            ticks = int(ticks_str)
        except ValueError:
            continue
        
        # Decrement
        new_ticks = ticks - amount
        
        if new_ticks <= 0:
            # Condition expired - mark for deletion
            rows_to_delete.append(i)
        else:
            # Update ticks_remaining
            col_letter = chr(65 + ticks_col)  # A=65
            range_name = f'CSV_ConditionReference!{col_letter}{i}'
            updates.append({
                'range': range_name,
                'values': [[str(new_ticks)]]
            })
    
    # Apply updates
    updated_count = 0
    
    if updates:
        try:
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    'valueInputOption': 'RAW',
                    'data': updates
                }
            ).execute()
            updated_count = len(updates)
        except HttpError as error:
            print(f"ERROR: Failed to tick conditions: {error}")
    
    # Delete expired conditions
    if rows_to_delete:
        # Get sheet ID first
        sheet_meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_id = None
        for sheet in sheet_meta.get('sheets', []):
            if sheet['properties']['title'] == 'CSV_ConditionReference':
                sheet_id = sheet['properties']['sheetId']
                break
        
        if sheet_id:
            # Delete in reverse order
            for row_num in reversed(sorted(rows_to_delete)):
                try:
                    service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body={
                            'requests': [{
                                'deleteDimension': {
                                    'range': {
                                        'sheetId': sheet_id,
                                        'dimension': 'ROWS',
                                        'startIndex': row_num - 1,
                                        'endIndex': row_num
                                    }
                                }
                            }]
                        }
                    ).execute()
                except HttpError as error:
                    print(f"ERROR: Failed to delete expired condition: {error}")
    
    return updated_count + len(rows_to_delete)

def get_active_conditions(service, spreadsheet_id, character_id):
    """Get all active conditions for a character"""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_ConditionReference!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return []
    
    headers = [h.strip().lower() for h in values[0]]
    conditions = []
    
    for row in values[1:]:
        if len(row) > 0 and row[0].strip().lower() == character_id.lower():
            condition = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    condition[header] = row[i].strip()
            conditions.append(condition)
    
    return conditions

def apply_condition_effects(conditions):
    """Parse mechanical_effects from conditions and return combined effects"""
    combined = {
        'ac_mod': 0,
        'attack_advantage': False,
        'attack_disadvantage': False,
        'skill_advantage': [],
        'skill_disadvantage': [],
        'save_advantage': [],
        'save_disadvantage': [],
        'speed_mod': 0,
        'damage_resistance': [],
        'damage_immunity': [],
        'condition_immunity': []
    }
    
    for condition in conditions:
        mech_effects = condition.get('mechanical_effects', '').strip()
        if not mech_effects:
            continue
        
        try:
            effects = json.loads(mech_effects)
        except (json.JSONDecodeError, TypeError):
            continue
        
        # Combine effects
        if 'ac_mod' in effects:
            combined['ac_mod'] += effects['ac_mod']
        
        if effects.get('attack_advantage'):
            combined['attack_advantage'] = True
        if effects.get('attack_disadvantage'):
            combined['attack_disadvantage'] = True
        
        if 'skill_advantage' in effects:
            combined['skill_advantage'].extend(effects['skill_advantage'])
        if 'skill_disadvantage' in effects:
            combined['skill_disadvantage'].extend(effects['skill_disadvantage'])
        
        if 'save_advantage' in effects:
            combined['save_advantage'].extend(effects['save_advantage'])
        if 'save_disadvantage' in effects:
            combined['save_disadvantage'].extend(effects['save_disadvantage'])
        
        if 'speed_mod' in effects:
            combined['speed_mod'] += effects['speed_mod']
        
        if 'damage_resistance' in effects:
            combined['damage_resistance'].extend(effects['damage_resistance'])
        if 'damage_immunity' in effects:
            combined['damage_immunity'].extend(effects['damage_immunity'])
        if 'condition_immunity' in effects:
            combined['condition_immunity'].extend(effects['condition_immunity'])
    
    return combined

def main():
    parser = argparse.ArgumentParser(description='Manage conditions system')
    parser.add_argument('--credentials', default='C:\\DnD\\keys\\google_sheets_key.json', help='Credentials file')
    parser.add_argument('--spreadsheet-id', default='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw', help='Spreadsheet ID')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Add condition
    add_parser = subparsers.add_parser('add', help='Add a condition')
    add_parser.add_argument('character', help='Character name')
    add_parser.add_argument('condition', help='Condition name')
    add_parser.add_argument('source', help='Source of condition')
    add_parser.add_argument('--duration-type', required=True, choices=['rounds', 'turns', 'minutes', 'hours', 'until_removed', 'save_ends', 'concentration'], help='Duration type')
    add_parser.add_argument('--duration-value', type=int, help='Duration value (not needed for until_removed, save_ends, concentration)')
    add_parser.add_argument('--mechanical-effects', help='Mechanical effects JSON (overrides condition definition)')
    
    # Remove condition
    remove_parser = subparsers.add_parser('remove', help='Remove a condition')
    remove_parser.add_argument('character', help='Character name')
    remove_parser.add_argument('condition', help='Condition name')
    remove_parser.add_argument('--source', help='Source (optional, removes all if not specified)')
    
    # Tick conditions
    tick_parser = subparsers.add_parser('tick', help='Tick conditions (decrement duration)')
    tick_parser.add_argument('--mode', choices=['round', 'turn'], default='round', help='Tick mode')
    tick_parser.add_argument('--amount', type=int, default=1, help='Amount to decrement')
    
    # List conditions
    list_parser = subparsers.add_parser('list', help='List active conditions')
    list_parser.add_argument('character', nargs='?', help='Character name (optional, lists all if omitted)')
    
    # Get effects
    effects_parser = subparsers.add_parser('effects', help='Get combined mechanical effects')
    effects_parser.add_argument('character', help='Character name')
    
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
    
    if args.command == 'add':
        character_id = get_character_id_from_name(args.character, service, args.spreadsheet_id)
        if not character_id:
            print(f"ERROR: Character '{args.character}' not found")
            sys.exit(1)
        
        # Validate duration_value
        if args.duration_type in ['rounds', 'turns', 'minutes', 'hours']:
            if args.duration_value is None:
                print(f"ERROR: --duration-value required for duration_type '{args.duration_type}'")
                sys.exit(1)
        else:
            args.duration_value = 0  # Not used
        
        if add_condition(service, args.spreadsheet_id, character_id, args.condition, args.source,
                       args.duration_type, args.duration_value or 0, args.mechanical_effects):
            print(f"OK: Added {args.condition} to {args.character}")
        else:
            print(f"ERROR: Failed to add condition")
            sys.exit(1)
    
    elif args.command == 'remove':
        character_id = get_character_id_from_name(args.character, service, args.spreadsheet_id)
        if not character_id:
            print(f"ERROR: Character '{args.character}' not found")
            sys.exit(1)
        
        if remove_condition(service, args.spreadsheet_id, character_id, args.condition, args.source):
            print(f"OK: Removed {args.condition} from {args.character}")
        else:
            print(f"ERROR: Failed to remove condition")
            sys.exit(1)
    
    elif args.command == 'tick':
        count = tick_conditions(service, args.spreadsheet_id, args.mode, args.amount)
        print(f"OK: Ticked {count} condition(s)")
    
    elif args.command == 'list':
        if args.character:
            character_id = get_character_id_from_name(args.character, service, args.spreadsheet_id)
            if not character_id:
                print(f"ERROR: Character '{args.character}' not found")
                sys.exit(1)
            
            conditions = get_active_conditions(service, args.spreadsheet_id, character_id)
            print(f"Active conditions for {args.character}:")
            for cond in conditions:
                condition_name = cond.get('condition', 'N/A')
                duration = cond.get('duration', 'N/A')
                source = cond.get('source', 'N/A')
                ticks = cond.get('ticks_remaining', 'N/A')
                print(f"  - {condition_name} ({duration}, source: {source}, ticks: {ticks})")
        else:
            # List all
            result = service.spreadsheets().values().get(
                spreadsheetId=args.spreadsheet_id,
                range='CSV_ConditionReference!A:Z'
            ).execute()
            values = result.get('values', [])
            if len(values) < 2:
                print("No active conditions")
            else:
                print("All active conditions:")
                for row in values[1:]:
                    if len(row) >= 3:
                        char_name = row[1] if len(row) > 1 else 'N/A'
                        condition = row[2] if len(row) > 2 else 'N/A'
                        duration = row[5] if len(row) > 5 else 'N/A'
                        print(f"  {char_name}: {condition} ({duration})")
    
    elif args.command == 'effects':
        character_id = get_character_id_from_name(args.character, service, args.spreadsheet_id)
        if not character_id:
            print(f"ERROR: Character '{args.character}' not found")
            sys.exit(1)
        
        conditions = get_active_conditions(service, args.spreadsheet_id, character_id)
        effects = apply_condition_effects(conditions)
        
        print(f"Combined mechanical effects for {args.character}:")
        print(json.dumps(effects, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

