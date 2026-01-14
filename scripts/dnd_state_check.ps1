# Quick State Check Command
param(
    [string]$Campaign = "Phandelver"
)

Write-Host "`n=== CURRENT STATE ===" -ForegroundColor Cyan
$statePath = "C:\DnD\Campaigns\$Campaign\saves\CURRENT_STATE.json"
if (Test-Path $statePath) {
    $state = Get-Content $statePath | ConvertFrom-Json
    Write-Host "Location: $($state.location)" -ForegroundColor Yellow
    Write-Host "Chapter: $($state.chapter)" -ForegroundColor Yellow
    Write-Host "Combat Active: $($state.combat.active)" -ForegroundColor Yellow
    Write-Host "Current Turn: $($state.combat.current_turn)" -ForegroundColor Yellow
} else {
    Write-Host "State file not found: $statePath" -ForegroundColor Red
}

Write-Host "`n=== RECENT EVENTS (Last 5) ===" -ForegroundColor Cyan
$eventsPath = "C:\DnD\Campaigns\$Campaign\saves\CAMPAIGN_EVENTS.json"
if (Test-Path $eventsPath) {
    $events = Get-Content $eventsPath | ConvertFrom-Json
    $events.events | Select-Object -Last 5 | ForEach-Object {
        Write-Host "[$($_.timestamp)] $($_.description)" -ForegroundColor Gray
    }
} else {
    Write-Host "Events file not found: $eventsPath" -ForegroundColor Red
}










