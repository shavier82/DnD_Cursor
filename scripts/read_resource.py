#!/usr/bin/env python3
"""Read a specific resource value from CSV_Resources"""

import json
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

def main():
    if len(sys.argv) < 3:
        print("Usage: python read_resource.py <character_name> <resource_name>")
        sys.exit(1)
    
    character_name = sys.argv[1]
    resource_name = sys.argv[2]
    
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
        range='CSV_Resources!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if not values:
        print("No resources data found")
        sys.exit(1)
    
    headers = [h.strip().lower() for h in values[0]]
    char_col = headers.index('character_id') if 'character_id' in headers else (headers.index('name') if 'name' in headers else 0)
    res_col = headers.index('resource') if 'resource' in headers else 2
    max_col = headers.index('max') if 'max' in headers else 3
    rem_col = headers.index('remaining') if 'remaining' in headers else 4
    
    for row in values[1:]:
        if len(row) > char_col and character_name.lower() in row[char_col].lower():
            if len(row) > res_col and resource_name.lower() in row[res_col].lower():
                max_val = row[max_col] if len(row) > max_col else '0'
                rem_val = row[rem_col] if len(row) > rem_col else '0'
                print(f"{max_val},{rem_val}")
                sys.exit(0)
    
    print("Resource not found")
    sys.exit(1)

if __name__ == "__main__":
    main()
































