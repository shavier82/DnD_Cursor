#!/usr/bin/env python3
"""Verify sheet updates"""

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

headers = [h.strip().lower() for h in data[0]]
print("Updated characters in Google Sheets:")
print()

for row in data[1:]:
    if len(row) >= 7:
        name = row[1] if len(row) > 1 else 'N/A'
        class_level = row[2] if len(row) > 2 else 'N/A'
        level = row[3] if len(row) > 3 else 'N/A'
        ac = row[6] if len(row) > 6 else 'N/A'
        speed = row[8] if len(row) > 8 else 'N/A'
        notes = row[15] if len(row) > 15 else ''
        
        print(f"{name}:")
        print(f"  Class/Level: {class_level}")
        print(f"  Level: {level}")
        print(f"  AC: {ac}")
        if speed:
            print(f"  Speed: {speed} ft")
        if notes:
            print(f"  Features: {notes[:80]}...")
        print()



