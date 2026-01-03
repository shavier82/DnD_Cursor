# Enable Google Sheets API

The Google Sheets API needs to be enabled in your Google Cloud project before the sync script can work.

## Steps

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Select your project:**
   - Your project ID is: `dnd-character-sheets-482202`
   - If you don't see it, make sure you're logged in with the correct Google account

3. **Enable Google Sheets API:**
   - Go to: https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=dnd-character-sheets-482202
   - Or navigate: APIs & Services → Library → Search "Google Sheets API" → Enable

4. **Wait a few minutes** for the API to propagate

5. **Test the connection:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\test_sheets_connection.py "1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw"
   ```

## Share the Sheet

After enabling the API, make sure the service account has access:

1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw
2. Click "Share" button
3. Add this email: `dnd-account@dnd-character-sheets-482202.iam.gserviceaccount.com`
4. Give it "Viewer" access (or "Editor" if you want write-back)
5. Click "Send"

## Quick Enable Link

Click here to enable the API directly:
https://console.cloud.google.com/apis/api/sheets.googleapis.com/overview?project=dnd-character-sheets-482202



