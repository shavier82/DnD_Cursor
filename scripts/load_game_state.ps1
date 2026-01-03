# Load Game State
# Loads current game state from campaign save file

param(
    [Parameter(Mandatory=$false)]
    [string]$Campaign = "Phandelver"
)

$ErrorActionPreference = "Stop"

# Load paths config
$configPath = Join-Path $PSScriptRoot "..\config\paths.json"
if (-not (Test-Path $configPath)) {
    Write-Output "ERROR: Config file not found: $configPath"
    exit 1
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json
$stateFile = $config.state_file

if (-not (Test-Path $stateFile)) {
    Write-Output "No save state found. Starting fresh campaign."
    exit 0
}

try {
    $state = Get-Content $stateFile -Raw -Encoding UTF8 | ConvertFrom-Json
    
    Write-Output "=== Campaign State ==="
    Write-Output "Last Saved: $($state.timestamp)"
    if ($state.scene) {
        Write-Output "Current Scene: $($state.scene.area) - $($state.scene.location)"
    }
    if ($state.combat -and $state.combat.initiated) {
        Write-Output "Combat: Active"
    }
    if ($state.encounters) {
        Write-Output "Completed Encounters: $($state.encounters.Count)"
    }
    
    # Output full state as JSON
    ($state | ConvertTo-Json -Depth 10)
    
} catch {
    Write-Output "ERROR: Failed to load game state: $($_.Exception.Message)"
    exit 1
}



