#!/usr/bin/env python3
"""Check character names from CSV_Characters"""

import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_info(
    json.load(open('C:/DnD/keys/google_sheets_key.json')),
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)
service = build('sheets', 'v4', credentials=creds)

data = service.spreadsheets().values().get(
    spreadsheetId='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw',
    range='CSV_Characters!A:Z'
).execute().get('values', [])

print("Character names from CSV_Characters:")
for row in data[1:]:
    if len(row) >= 2:
        print(f"  {row[1]} (ID: {row[0]})")



