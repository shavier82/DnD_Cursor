# Combine Combat Narrative
# Combines turn-by-turn narratives into a single encounter narrative and saves to files

param(
    [Parameter(Mandatory=$true)]
    [string]$Campaign = "Phandelver",
    
    [Parameter(Mandatory=$false)]
    [string]$StateFile = ""
)

$ErrorActionPreference = "Stop"

# Load paths config
$configPath = Join-Path $PSScriptRoot "..\config\paths.json"
if (-not (Test-Path $configPath)) {
    Write-Output "ERROR: Config file not found: $configPath"
    exit 1
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Determine state file path
if (-not $StateFile) {
    $campaignDir = Join-Path $config.campaigns_root $Campaign
    $StateFile = Join-Path $campaignDir "saves\CURRENT_STATE.json"
}

if (-not (Test-Path $StateFile)) {
    Write-Output "ERROR: State file not found: $StateFile"
    exit 1
}

# Load state
$state = Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json

# Check if combat ended and has narratives
if (-not $state.combat -or -not $state.combat.ended -or -not $state.combat.turn_narratives) {
    Write-Output "INFO: Combat not ended or no narratives to combine"
    exit 0
}

$turnNarratives = $state.combat.turn_narratives
if ($turnNarratives.Count -eq 0) {
    Write-Output "INFO: No turn narratives to combine"
    exit 0
}

# Get encounter details
$location = if ($state.scene.location) { $state.scene.location } else { "unknown_location" }
$participants = @()
if ($state.combat.combatants) {
    $participants = $state.combat.combatants.PSObject.Properties.Name
}
$rounds = if ($state.combat.round) { $state.combat.round } else { 1 }
$encounterId = "encounter_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Combine narratives
$combinedNarrative = ""
$currentRound = 0

foreach ($turn in $turnNarratives | Sort-Object { $_.round }, { $_.turn_order }) {
    if ($turn.round -ne $currentRound) {
        if ($currentRound -gt 0) {
            $combinedNarrative += "`n`n"
        }
        $combinedNarrative += "**Round $($turn.round)**`n`n"
        $currentRound = $turn.round
    }
    $combinedNarrative += "$($turn.narrative)`n`n"
}

# Create narrative object
$narrativeData = @{
    encounter_id = $encounterId
    location = $location
    timestamp = (Get-Date).ToString("o")
    participants = $participants
    rounds = $rounds
    turn_narratives = $turnNarratives
    combined_narrative = $combinedNarrative
}

# Save to combat_narratives.json
$campaignDir = Join-Path $config.campaigns_root $Campaign
$savesDir = Join-Path $campaignDir "saves"
if (-not (Test-Path $savesDir)) {
    New-Item -ItemType Directory -Force -Path $savesDir | Out-Null
}

$narrativesFile = Join-Path $savesDir "combat_narratives.json"

# Load existing narratives or create new
$allNarratives = @()
if (Test-Path $narrativesFile) {
    try {
        $existing = Get-Content $narrativesFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($existing -is [Array]) {
            $allNarratives = $existing
        } elseif ($existing.encounters) {
            $allNarratives = $existing.encounters
        }
    } catch {
        # If file is invalid, start fresh
        $allNarratives = @()
    }
}

# Add new narrative
$allNarratives += $narrativeData

# Save to JSON file
$output = @{
    last_updated = (Get-Date).ToString("o")
    encounters = $allNarratives
}
($output | ConvertTo-Json -Depth 10) | Set-Content -Path $narrativesFile -Encoding UTF8

# Append to combat log text file
$logFile = Join-Path $savesDir "combat_log.txt"
$logEntry = @"

================================================================================
ENCOUNTER: $encounterId
Location: $location
Date: $($narrativeData.timestamp)
Participants: $($participants -join ", ")
Rounds: $rounds
================================================================================

$combinedNarrative

"@

Add-Content -Path $logFile -Value $logEntry -Encoding UTF8

Write-Output "OK: Combined narrative saved to $narrativesFile and appended to $logFile"

