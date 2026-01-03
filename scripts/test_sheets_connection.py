#!/usr/bin/env python3
"""
Test Google Sheets Connection
Quick test to verify credentials and sheet access
"""

import json
import sys
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("ERROR: Google API libraries not installed.")
    print("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

def test_connection(credentials_path, spreadsheet_id, range_name="Sheet1!A1:Z10"):
    """Test connection to Google Sheets"""
    print(f"[test] Loading credentials from: {credentials_path}")
    
    if not Path(credentials_path).exists():
        print(f"ERROR: Credentials file not found: {credentials_path}")
        return False
    
    try:
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)
        
        credentials = service_account.Credentials.from_service_account_info(
            creds_data,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        print(f"[test] Building Sheets API service...")
        service = build('sheets', 'v4', credentials=credentials)
        
        print(f"[test] Testing connection to spreadsheet: {spreadsheet_id}")
        print(f"[test] Reading range: {range_name}")
        
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("WARNING: No data found in sheet")
            return False
        
        print(f"[test] SUCCESS: Connected! Found {len(values)} rows")
        print(f"[test] First row (headers): {values[0] if values else 'No headers'}")
        
        if len(values) > 1:
            print(f"[test] Second row (sample data): {values[1] if len(values) > 1 else 'No data'}")
        
        return True
        
    except HttpError as error:
        print(f"ERROR: HTTP error occurred: {error}")
        if error.resp.status == 403:
            print("  -> Permission denied. Make sure:")
            print("    1. The service account email has access to the sheet")
            print("    2. The service account email is: dnd-account@dnd-character-sheets-482202.iam.gserviceaccount.com")
            print("    3. Google Sheets API is enabled in the Google Cloud project")
        elif error.resp.status == 404:
            print("  → Spreadsheet not found. Check the spreadsheet ID.")
        return False
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_sheets_connection.py <spreadsheet-id> [range]")
        print("Example: python test_sheets_connection.py '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms' 'Sheet1!A1:Z10'")
        sys.exit(1)
    
    credentials_path = "C:\\DnD\\keys\\google_sheets_key.json"
    spreadsheet_id = sys.argv[1]
    range_name = sys.argv[2] if len(sys.argv) > 2 else "Sheet1!A1:Z10"
    
    success = test_connection(credentials_path, spreadsheet_id, range_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

