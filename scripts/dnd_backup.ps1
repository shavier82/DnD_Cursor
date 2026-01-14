# Quick Backup Command
param(
    [Parameter(Mandatory=$true)]
    [string]$Campaign
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$savesDir = "C:\DnD\Campaigns\$Campaign\saves"
$backupDir = "C:\DnD\Campaigns\$Campaign\backups"

# Create backup directory if it doesn't exist
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Backup state files
$files = @("CURRENT_STATE.json", "CAMPAIGN_EVENTS.json")
foreach ($file in $files) {
    $sourcePath = Join-Path $savesDir $file
    if (Test-Path $sourcePath) {
        $backupName = $file -replace '\.json$', "_$timestamp.json"
        $backupPath = Join-Path $backupDir $backupName
        Copy-Item $sourcePath $backupPath
        Write-Host "✅ Backed up: $backupName" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ Backup complete: $timestamp" -ForegroundColor Green
Write-Host "Location: $backupDir" -ForegroundColor Gray










