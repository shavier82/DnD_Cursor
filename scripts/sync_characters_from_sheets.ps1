# PowerShell wrapper for Google Sheets sync
# Makes it easier to run from PowerShell

param(
    [Parameter(Mandatory=$false)]
    [string]$SpreadsheetId = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Range = "Sheet1!A:Z",
    
    [Parameter(Mandatory=$false)]
    [string[]]$Characters = @(),
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigPath = "C:\DnD\DnD_Cursor\config\sheets_config.json"
)

$ErrorActionPreference = "Stop"

# Load config if it exists
$credentialsPath = "C:\DnD\keys\google_sheets_key.json"
$spreadsheetId = $SpreadsheetId

if (Test-Path $ConfigPath) {
    $config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
    if ($config.credentials_path) {
        $credentialsPath = $config.credentials_path
    }
    if (-not $spreadsheetId -and $config.spreadsheet_id) {
        $spreadsheetId = $config.spreadsheet_id
    }
    if (-not $Range -and $config.range) {
        $Range = $config.range
    }
}

if (-not $spreadsheetId) {
    Write-Host "ERROR: Spreadsheet ID required" -ForegroundColor Red
    Write-Host "Usage: .\sync_characters_from_sheets.ps1 -SpreadsheetId 'YOUR_SPREADSHEET_ID'" -ForegroundColor Yellow
    Write-Host "Or set it in: $ConfigPath" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $credentialsPath)) {
    Write-Host "ERROR: Credentials file not found: $credentialsPath" -ForegroundColor Red
    exit 1
}

# Build Python command
$scriptPath = Join-Path $PSScriptRoot "sync_characters_from_sheets.py"
$args = @(
    "--credentials", $credentialsPath,
    "--spreadsheet-id", $spreadsheetId,
    "--range", $Range
)

if ($Characters.Count -gt 0) {
    $args += "--characters"
    $args += $Characters
}

Write-Host "Syncing characters from Google Sheets..." -ForegroundColor Cyan
Write-Host "Spreadsheet ID: $spreadsheetId" -ForegroundColor Gray
Write-Host ""

# Run Python script
python $scriptPath $args

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Sync failed. Check errors above." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Sync complete!" -ForegroundColor Green



