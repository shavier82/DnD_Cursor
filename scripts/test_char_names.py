#!/usr/bin/env python3
"""Test character names in sheet"""

import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

config = json.load(open('C:/DnD/DnD_Cursor/config/sheets_config.json'))
creds = service_account.Credentials.from_service_account_file(
    config['credentials_path'],
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
service = build('sheets', 'v4', credentials=creds)

result = service.spreadsheets().values().get(
    spreadsheetId=config['spreadsheet_id'],
    range='CSV_Characters!A:B'
).execute()

values = result.get('values', [])
print('Characters in sheet:')
for row in values[1:6]:
    char_id = row[0] if len(row) > 0 else ""
    char_name = row[1] if len(row) > 1 else ""
    print(f'  ID: {char_id}, Name: {char_name}')



