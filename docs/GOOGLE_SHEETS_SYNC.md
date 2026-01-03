# Google Sheets Character Sync

This system can sync character data from Google Sheets to local JSON files, keeping HP, XP, spell slots, rage resources, and inventory up-to-date.

## Setup

### 1. Google Service Account Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable the Google Sheets API
4. Create a Service Account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Give it a name (e.g., "dnd-character-sync")
   - Grant it "Editor" role (or create custom role with Sheets read access)
5. Create a key:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose JSON format
   - Save the JSON file to: `C:\DnD\Campaigns\Phandelver\google_credentials.json`

### 2. Share Google Sheet

1. Open your character sheet in Google Sheets
2. Click "Share" button
3. Add the service account email (found in the credentials JSON file, field: `client_email`)
4. Give it "Viewer" or "Editor" access (depending on if you want read-only or read-write)

### 3. Get Spreadsheet ID

From your Google Sheets URL:
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
```
Copy the `SPREADSHEET_ID` part.

### 4. Configure Sheet Structure

Update `config/sheets_config.json` with:
- `credentials_path`: Path to your credentials JSON file
- `spreadsheet_id`: The spreadsheet ID from step 3
- `column_mappings`: Map your sheet columns to character fields

## Sheet Structure

Your Google Sheet should have:
- **Row 1**: Headers (Name, Class, Level, AC, HP Current, HP Max, etc.)
- **Row 2+**: Character data (one row per character)

### Required Columns

At minimum, your sheet should have:
- Character Name
- Class & Level (e.g., "Rogue 4")
- AC (Armor Class)
- HP Current
- HP Max
- Ability Scores (STR, DEX, CON, INT, WIS, CHA)
- XP

### Optional Columns

- Spell Slots (Level 1, Level 2, etc.)
- Rage (for barbarians, format: "2/3" or just "3")
- Inventory (comma-separated items)
- Features/Notes

## Usage

### Manual Sync

```powershell
python C:\DnD\DnD_Cursor\scripts\sync_characters_from_sheets.py `
  --credentials "C:\DnD\Campaigns\Phandelver\google_credentials.json" `
  --spreadsheet-id "YOUR_SPREADSHEET_ID" `
  --range "Sheet1!A:Z" `
  --characters "Brevin" "Ergath" "Torgga" "Vandross"
```

### Sync All Characters

```powershell
python C:\DnD\DnD_Cursor\scripts\sync_characters_from_sheets.py `
  --credentials "C:\DnD\Campaigns\Phandelver\google_credentials.json" `
  --spreadsheet-id "YOUR_SPREADSHEET_ID" `
  --range "Sheet1!A:Z"
```

### Auto-Sync (Future Enhancement)

The system can be configured to auto-sync before each session or turn. This would require:
- Adding sync call to session initialization
- Or running a background sync process

## Installation

Install required Python packages:

```powershell
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Troubleshooting

### "Credentials file not found"
- Check the path in `config/sheets_config.json`
- Ensure the JSON file exists and is readable

### "Permission denied" or "Access denied"
- Verify the service account email has access to the sheet
- Check that the service account has the correct permissions

### "Character not found in sheet"
- Verify the character name in the sheet matches exactly (case-insensitive)
- Check that the character name is in the first column (or adjust `character_column` in config)

### Column mapping issues
- The script uses flexible header matching (case-insensitive, partial matches)
- If columns aren't being read, check the header names in your sheet
- You may need to adjust the `parse_character_from_sheet` function for your specific sheet structure

## Example Sheet Layout

```
| Name      | Class      | Level | Race      | AC | HP Current | HP Max | STR | DEX | CON | INT | WIS | CHA | XP    | Rage | Inventory        |
|-----------|------------|-------|-----------|----|-----------|--------|-----|-----|-----|-----|-----|-----|-------|------|------------------|
| Brevin    | Rogue      | 4     | Halfling  | 15 | 27        | 27     | 8   | 17  | 12  | 15  | 10  | 15  | 2885  |      | Dagger, Thieves' |
| Ergath    | Barbarian  | 4     | Goliath   | 15 | 41        | 41     | 16  | 15  | 15  | 12  | 10  | 8   | 2925  | 2/3  | Javelin, Shield  |
| Torgga    | Cleric     | 4     | Hill Dwarf| 18 | 39        | 39     | 14  | 8   | 16  | 10  | 17  | 12  | 2700  |      | Mace, Shield     |
| Vandross  | Fighter    | 4     | Human     | 15 | 36        | 36     | 16  | 15  | 15  | 11  | 13  | 9   | 2795  |      | Longsword, Armor |
```



