#!/usr/bin/env python3
"""Read currency from CSV_Currency sheet"""

import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def main():
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
        range='CSV_Currency!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if not values:
        print("No currency data found")
        return
    
    headers = [h.strip().lower() for h in values[0]]
    
    name_idx = headers.index('name') if 'name' in headers else -1
    gp_idx = headers.index('gp') if 'gp' in headers else -1
    pp_idx = headers.index('pp') if 'pp' in headers else -1
    ep_idx = headers.index('ep') if 'ep' in headers else -1
    sp_idx = headers.index('sp') if 'sp' in headers else -1
    cp_idx = headers.index('cp') if 'cp' in headers else -1
    
    chars = {}
    total_gp = 0.0
    
    for row in values[1:]:
        if name_idx < 0 or len(row) <= name_idx:
            continue
        
        name = row[name_idx]
        gp = int(row[gp_idx].replace(',', '')) if gp_idx >= 0 and len(row) > gp_idx and row[gp_idx].strip() else 0
        pp = int(row[pp_idx].replace(',', '')) if pp_idx >= 0 and len(row) > pp_idx and row[pp_idx].strip() else 0
        ep = int(row[ep_idx].replace(',', '')) if ep_idx >= 0 and len(row) > ep_idx and row[ep_idx].strip() else 0
        sp = int(row[sp_idx].replace(',', '')) if sp_idx >= 0 and len(row) > sp_idx and row[sp_idx].strip() else 0
        cp = int(row[cp_idx].replace(',', '')) if cp_idx >= 0 and len(row) > cp_idx and row[cp_idx].strip() else 0
        
        # Convert to GP equivalent
        gp_equiv = pp * 10 + gp + ep * 0.5 + sp * 0.1 + cp * 0.01
        total_gp += gp_equiv
        
        chars[name] = {
            'pp': pp,
            'gp': gp,
            'ep': ep,
            'sp': sp,
            'cp': cp,
            'gp_equivalent': round(gp_equiv, 2)
        }
    
    print(json.dumps(chars, indent=2))
    print(f'\nTotal GP equivalent: {total_gp:.2f} gp')
    print(f'Option 3 cost: 480 gp')
    print(f'Can afford Option 3: {"YES" if total_gp >= 480 else "NO"}')

if __name__ == '__main__':
    main()

