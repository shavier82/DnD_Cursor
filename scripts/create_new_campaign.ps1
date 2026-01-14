# Create New Campaign
# Sets up directory structure and updates paths.json for a new campaign

param(
    [Parameter(Mandatory=$true)]
    [string]$CampaignName,
    
    [Parameter(Mandatory=$false)]
    [string]$SourceName = ""
)

$ErrorActionPreference = "Stop"

# Validate campaign name (no spaces, alphanumeric + underscore/hyphen)
if ($CampaignName -notmatch '^[A-Za-z0-9_-]+$') {
    Write-Error "Campaign name must be alphanumeric with underscores or hyphens only (no spaces)"
    exit 1
}

# Load paths config
$configPath = Join-Path $PSScriptRoot "..\config\paths.json"
if (-not (Test-Path $configPath)) {
    Write-Error "Config file not found: $configPath"
    exit 1
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json
$campaignsRoot = $config.campaigns_root

# Campaign directory
$campaignDir = Join-Path $campaignsRoot $CampaignName

# Check if campaign already exists
if (Test-Path $campaignDir) {
    Write-Warning "Campaign directory already exists: $campaignDir"
    $response = Read-Host "Do you want to continue anyway? (y/n)"
    if ($response -ne 'y') {
        exit 0
    }
}

Write-Host "Creating campaign structure for: $CampaignName"
Write-Host "Campaign directory: $campaignDir"

# Create directory structure
$directories = @(
    "chapters",
    "packs",
    "packs\logs",
    "characters",
    "saves",
    "players",
    "exports",
    "logs"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path $campaignDir $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Force -Path $fullPath | Out-Null
        Write-Host "  Created: $dir"
    } else {
        Write-Host "  Exists: $dir"
    }
}

# Create initial save files
$currentStatePath = Join-Path $campaignDir "saves\CURRENT_STATE.json"
if (-not (Test-Path $currentStatePath)) {
    $initialState = @{
        scene = @{
            location = ""
            area = ""
            description = ""
        }
        gates = @{}
        discoveries = @{}
        encounters = @{}
        combat = @{
            initiated = $false
            ended = $true
        }
    } | ConvertTo-Json -Depth 10
    
    Set-Content -Path $currentStatePath -Value $initialState -Encoding UTF8
    Write-Host "  Created: saves\CURRENT_STATE.json"
}

$campaignEventsPath = Join-Path $campaignDir "saves\CAMPAIGN_EVENTS.json"
if (-not (Test-Path $campaignEventsPath)) {
    $initialEvents = @{
        events = @()
        npcs = @{}
        quests = @{}
        consequences = @{}
    } | ConvertTo-Json -Depth 10
    
    Set-Content -Path $campaignEventsPath -Value $initialEvents -Encoding UTF8
    Write-Host "  Created: saves\CAMPAIGN_EVENTS.json"
}

# Update paths.json
Write-Host "`nUpdating paths.json..."
$config.default_campaign = $CampaignName
$config.default_campaign_dir = $campaignDir
$config.chapters_dir = Join-Path $campaignDir "chapters"
$config.packs_dir = Join-Path $campaignDir "packs"
$config.state_file = $currentStatePath
if ($SourceName) {
    $config.source_name = $SourceName
} elseif (-not $config.source_name) {
    $config.source_name = $CampaignName
}

$configJson = $config | ConvertTo-Json -Depth 10
Set-Content -Path $configPath -Value $configJson -Encoding UTF8
Write-Host "  Updated paths.json to point to: $CampaignName"

# Create initial pack files
Write-Host "`nCreating initial pack files..."

# Session preload
$sessionPreloadPath = Join-Path $campaignDir "packs\session_preload.json"
$sourceName = if ($SourceName) { $SourceName } else { $CampaignName }
$sessionPreload = @{
    pack_type = "session_preload"
    pack_version = "1.0"
    source = $sourceName
    chapter = $null
    cards = @()
} | ConvertTo-Json -Depth 10
Set-Content -Path $sessionPreloadPath -Value $sessionPreload -Encoding UTF8
Write-Host "  Created: packs\session_preload.json"

# Encounter pack
$encounterPackPath = Join-Path $campaignDir "packs\encounter_pack.json"
$encounterPack = @{
    pack_type = "encounter_pack"
    pack_version = "1.0"
    source = $sourceName
    chapter = $null
    cards = @()
} | ConvertTo-Json -Depth 10
Set-Content -Path $encounterPackPath -Value $encounterPack -Encoding UTF8
Write-Host "  Created: packs\encounter_pack.json"

Write-Host "`n✓ Campaign '$CampaignName' created successfully!"
Write-Host "`nNext steps:"
Write-Host "  1. Add chapter text files to: $campaignDir\chapters\"
Write-Host '     Example: chapter_1.txt, chapter_2.txt, etc.'
Write-Host "  2. Build chapter packs using:"
Write-Host '     python scripts\build_chapter_pack.py --chapter [number]'
Write-Host "  3. Or use the PowerShell wrapper:"
Write-Host '     .\scripts\build_chapter_pack.ps1 -Chapter [number]'
Write-Host ''
Write-Host 'Note: The build script will automatically extract mechanic cards (gates)'
Write-Host '      from DC checks and saving throws in your chapter text files.'

