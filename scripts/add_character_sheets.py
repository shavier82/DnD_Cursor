"""
Add a new character to all Google Sheets (CSV_Characters, CSV_SpellSlots, CSV_Currency, CSV_Resources)
"""
import json
import sys
import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def load_credentials(credentials_path):
    with open(credentials_path, 'r') as f:
        creds_data = json.load(f)
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return credentials

def get_sheets_service(credentials_path):
    try:
        credentials = load_credentials(credentials_path)
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"ERROR: Failed to get Google Sheets service: {e}")
        sys.exit(1)

def add_to_sheet(service, spreadsheet_id, sheet_name, row_data):
    """Add a row to a sheet"""
    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}!A:Z',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [row_data]}
        ).execute()
        return True
    except HttpError as error:
        print(f"ERROR: Failed to add to {sheet_name}: {error}")
        return False

def get_headers(service, spreadsheet_id, sheet_name):
    """Get headers from a sheet"""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_name}!A1:Z1'
    ).execute()
    return [h.strip() for h in result.get('values', [[]])[0]]

def add_character_complete(service, spreadsheet_id, character_id, name, level, hp_current, hp_max, ac, xp):
    """Add character to all necessary sheets"""
    success = True
    
    # 1. CSV_Characters (already done, but verify)
    print(f"Adding {name} to all sheets...")
    
    # 2. CSV_SpellSlots - Add entries for 1st and 2nd level slots
    headers = get_headers(service, spreadsheet_id, 'CSV_SpellSlots')
    col_map = {h.lower(): i for i, h in enumerate(headers)}
    row_1st = [''] * len(headers)
    row_2nd = [''] * len(headers)
    
    if 'character_id' in col_map:
        row_1st[col_map['character_id']] = character_id
        row_2nd[col_map['character_id']] = character_id
    if 'name' in col_map:
        row_1st[col_map['name']] = name
        row_2nd[col_map['name']] = name
    if 'slot_level' in col_map:
        row_1st[col_map['slot_level']] = '1st'
        row_2nd[col_map['slot_level']] = '2nd'
    if 'max' in col_map:
        row_1st[col_map['max']] = '4'
        row_2nd[col_map['max']] = '2'
    if 'remaining' in col_map:
        row_1st[col_map['remaining']] = '4'
        row_2nd[col_map['remaining']] = '2'
    
    if not add_to_sheet(service, spreadsheet_id, 'CSV_SpellSlots', row_1st):
        success = False
    if not add_to_sheet(service, spreadsheet_id, 'CSV_SpellSlots', row_2nd):
        success = False
    
    # 3. CSV_Currency
    headers = get_headers(service, spreadsheet_id, 'CSV_Currency')
    col_map = {h.lower(): i for i, h in enumerate(headers)}
    row = [''] * len(headers)
    
    if 'character_id' in col_map:
        row[col_map['character_id']] = character_id
    if 'name' in col_map:
        row[col_map['name']] = name
    if 'cp' in col_map:
        row[col_map['cp']] = '0'
    if 'sp' in col_map:
        row[col_map['sp']] = '5'
    if 'ep' in col_map:
        row[col_map['ep']] = '0'
    if 'gp' in col_map:
        row[col_map['gp']] = '10'
    if 'pp' in col_map:
        row[col_map['pp']] = '0'
    
    if not add_to_sheet(service, spreadsheet_id, 'CSV_Currency', row):
        success = False
    
    return success

def main():
    parser = argparse.ArgumentParser(description='Add character to all Google Sheets')
    parser.add_argument('character_id', help='Character ID')
    parser.add_argument('name', help='Character name')
    parser.add_argument('--level', type=int, default=3, help='Level')
    parser.add_argument('--hp-current', type=int, dest='hp_current', default=20, help='Current HP')
    parser.add_argument('--hp-max', type=int, dest='hp_max', default=20, help='Max HP')
    parser.add_argument('--ac', type=int, default=12, help='AC')
    parser.add_argument('--xp', type=int, default=900, help='XP')
    parser.add_argument('--credentials', default=r'C:\DnD\keys\google_sheets_key.json', help='Credentials file')
    parser.add_argument('--spreadsheet-id', default='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw', help='Spreadsheet ID')
    
    args = parser.parse_args()
    
    service = get_sheets_service(args.credentials)
    
    if add_character_complete(service, args.spreadsheet_id, args.character_id, args.name, 
                             args.level, args.hp_current, args.hp_max, args.ac, args.xp):
        print(f"OK: Added {args.name} to all sheets")
        sys.exit(0)
    else:
        print(f"ERROR: Some operations failed")
        sys.exit(1)

if __name__ == '__main__':
    main()

