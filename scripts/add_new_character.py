"""
Add a new character to Google Sheets CSV_Characters
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

def add_character_to_sheets(service, spreadsheet_id, character_data):
    """Add a new character row to CSV_Characters"""
    # Get headers first
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A1:Z1'
    ).execute()
    
    headers = [h.strip() for h in result.get('values', [[]])[0]]
    
    # Build row data matching headers
    row_data = [''] * len(headers)
    
    # Map character data to columns
    col_map = {h.lower(): i for i, h in enumerate(headers)}
    
    # Set values based on column names
    if 'character_id' in col_map:
        row_data[col_map['character_id']] = character_data.get('character_id', '')
    if 'name' in col_map:
        row_data[col_map['name']] = character_data.get('name', '')
    if 'class_level' in col_map:
        row_data[col_map['class_level']] = character_data.get('class_level', '')
    if 'level' in col_map:
        row_data[col_map['level']] = str(character_data.get('level', ''))
    if 'hp_current' in col_map:
        row_data[col_map['hp_current']] = str(character_data.get('hp_current', ''))
    if 'hp_max' in col_map:
        row_data[col_map['hp_max']] = str(character_data.get('hp_max', ''))
    if 'ac' in col_map:
        row_data[col_map['ac']] = str(character_data.get('ac', ''))
    if 'xp' in col_map:
        row_data[col_map['xp']] = str(character_data.get('xp', ''))
    
    # Append row
    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='CSV_Characters!A:Z',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [row_data]}
        ).execute()
        print(f"OK: Added {character_data.get('name')} to CSV_Characters")
        return True
    except HttpError as error:
        print(f"ERROR: Failed to add character: {error}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Add a new character to Google Sheets CSV_Characters')
    parser.add_argument('character_id', help='Character ID (e.g., zephyr_sparkwhistle)')
    parser.add_argument('name', help='Character name')
    parser.add_argument('class_level', help='Class and level (e.g., "Wizard 3")')
    parser.add_argument('--level', type=int, help='Numeric level')
    parser.add_argument('--hp-current', type=int, dest='hp_current', help='Current HP')
    parser.add_argument('--hp-max', type=int, dest='hp_max', help='Max HP')
    parser.add_argument('--ac', type=int, help='Armor Class')
    parser.add_argument('--xp', type=int, help='Experience points')
    parser.add_argument('--credentials', default=r'C:\DnD\keys\google_sheets_key.json', help='Credentials file')
    parser.add_argument('--spreadsheet-id', default='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw', help='Spreadsheet ID')
    
    args = parser.parse_args()
    
    character_data = {
        'character_id': args.character_id,
        'name': args.name,
        'class_level': args.class_level,
        'level': args.level or 1,
        'hp_current': args.hp_current or 0,
        'hp_max': args.hp_max or 0,
        'ac': args.ac or 10,
        'xp': args.xp or 0
    }
    
    service = get_sheets_service(args.credentials)
    
    if add_character_to_sheets(service, args.spreadsheet_id, character_data):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()

