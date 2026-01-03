#!/usr/bin/env python3
"""List all sheet names in a Google Spreadsheet"""

import json
import sys
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("ERROR: Google API libraries not installed")
    sys.exit(1)

def list_sheets(credentials_path, spreadsheet_id):
    """List all sheet names"""
    with open(credentials_path, 'r') as f:
        creds_data = json.load(f)
    
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    
    # Get spreadsheet metadata
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = spreadsheet.get('sheets', [])
    
    print(f"Found {len(sheets)} sheet(s):")
    for sheet in sheets:
        props = sheet.get('properties', {})
        title = props.get('title', 'Unknown')
        sheet_id = props.get('sheetId', 'Unknown')
        print(f"  - '{title}' (ID: {sheet_id})")
    
    return [s['properties']['title'] for s in sheets]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python list_sheet_names.py <spreadsheet-id>")
        sys.exit(1)
    
    credentials_path = "C:\\DnD\\keys\\google_sheets_key.json"
    spreadsheet_id = sys.argv[1]
    
    list_sheets(credentials_path, spreadsheet_id)



