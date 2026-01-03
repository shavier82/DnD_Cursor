# Auto Event Tracker
# Automatically detects milestones and updates CAMPAIGN_EVENTS.json
# Called from merge_outputs.ps1 after state patches are applied

param(
    [Parameter(Mandatory=$true)]
    [string]$Campaign,
    
    [Parameter(Mandatory=$true)]
    [string]$StateFile,
    
    [Parameter(Mandatory=$true)]
    [array]$Patches
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Load current state first to get campaign name if needed
$state = $null
if (Test-Path $StateFile) {
    try {
        $state = Get-Content $StateFile -Raw | ConvertFrom-Json
        # Get campaign name from state if not provided
        if ([string]::IsNullOrWhiteSpace($Campaign) -and $state.campaign) {
            $Campaign = $state.campaign
        }
    } catch {
        # Invalid state, skip tracking
        return
    }
} else {
    return  # No state file, skip tracking
}

if ([string]::IsNullOrWhiteSpace($Campaign)) {
    $Campaign = "Phandelver"  # Default fallback
}

# Load paths config
$configPath = "C:\DnD\DnD_Cursor\config\paths.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath -Raw | ConvertFrom-Json
    if ($config.default_campaign_dir) {
        $campaignDir = $config.default_campaign_dir -replace "Phandelver", $Campaign
    } else {
        $campaignDir = "C:\DnD\Campaigns\$Campaign"
    }
} else {
    $campaignDir = "C:\DnD\Campaigns\$Campaign"
}

$eventsFile = Join-Path $campaignDir "saves\CAMPAIGN_EVENTS.json"

# Load or create events file
$events = @{
    campaign = $Campaign
    last_updated = (Get-Date).ToString("o")
    events = @()
    npcs = @{}
    quests = @{}
    choices_log = @()
    consequences = @{}
}

if (Test-Path $eventsFile) {
    try {
        $existing = Get-Content $eventsFile -Raw | ConvertFrom-Json
        $events.campaign = $existing.campaign
        $events.events = if ($existing.events) { $existing.events } else { @() }
        $events.npcs = if ($existing.npcs) { $existing.npcs } else { @{} }
        $events.quests = if ($existing.quests) { $existing.quests } else { @{} }
        $events.choices_log = if ($existing.choices_log) { $existing.choices_log } else { @() }
        $events.consequences = if ($existing.consequences) { $existing.consequences } else { @{} }
    } catch {
        # If file is corrupted, start fresh
    }
}

$newEvents = @()
$updatedQuests = @{}
$updatedNpcs = @{}

# Detect events from patches and state changes
foreach ($patch in $Patches) {
    $path = $patch.path
    $op = $patch.op
    $value = $patch.value
    
    # Detect encounter completion
    if ($path -match "^/encounters/") {
        $encounterName = $path -replace "^/encounters/", ""
        if ($op -eq "add" -and $value -and $state.encounters) {
            $encounter = $state.encounters | Where-Object { $_.name -eq $encounterName } | Select-Object -First 1
            if ($encounter -and $encounter.completed) {
                $eventId = "encounter_$encounterName"
                if (-not ($events.events | Where-Object { $_.id -eq $eventId })) {
                    $newEvents += @{
                        id = $eventId
                        timestamp = if ($encounter.timestamp) { $encounter.timestamp } else { (Get-Date).ToString("o") }
                        chapter = $state.scene.chapter
                        location = $state.scene.location
                        type = "encounter"
                        title = "Encounter: $encounterName"
                        description = if ($encounter.description) { $encounter.description } else { "Completed encounter: $encounterName" }
                        participants = if ($state.party.members) { $state.party.members } else { @() }
                        choices = @()
                        outcomes = @{
                            encounter_completed = $true
                            encounter_name = $encounterName
                        }
                    }
                }
            }
        }
    }
    
    # Detect quest item discovery (when discoveries are made)
    if ($path -match "^/discoveries/") {
        $discoveryName = $path -replace "^/discoveries/", ""
        if ($op -eq "add" -and $value) {
            # Check if this discovery relates to a quest item
            if ($discoveryName -match "necklace|item|treasure|quest") {
                # Try to match with existing quests
                foreach ($questId in $events.quests.Keys) {
                    $quest = $events.quests[$questId]
                    if ($quest.status -eq "active" -and $discoveryName -match $quest.objective) {
                        $updatedQuests[$questId] = @{
                            status = "completed"
                            completion_timestamp = (Get-Date).ToString("o")
                            completion_notes = "Quest item discovered: $discoveryName"
                        }
                    }
                }
            }
        }
    }
    
    # Detect scene changes that might indicate quest progress
    if ($path -match "^/scene/location$") {
        $newLocation = $value
        # Check if new location matches any active quest locations
        foreach ($questId in $events.quests.Keys) {
            $quest = $events.quests[$questId]
            if ($quest.status -eq "active" -and $quest.quest_location -and $newLocation -match $quest.quest_location) {
                # Party is at quest location - could be progress
                if (-not $quest.progress) {
                    $updatedQuests[$questId] = @{
                        progress = "at_location"
                        progress_timestamp = (Get-Date).ToString("o")
                    }
                }
            }
        }
    }
}

# Detect major encounters from state
if ($state.encounters) {
    foreach ($encounter in $state.encounters) {
        if ($encounter.completed) {
            $eventId = "encounter_$($encounter.name)"
            if (-not ($events.events | Where-Object { $_.id -eq $eventId })) {
                $newEvents += @{
                    id = $eventId
                    timestamp = if ($encounter.timestamp) { $encounter.timestamp } else { (Get-Date).ToString("o") }
                    chapter = $state.scene.chapter
                    location = $state.scene.location
                    type = "encounter"
                    title = "Encounter: $($encounter.name)"
                    description = if ($encounter.description) { $encounter.description } else { "Completed encounter: $($encounter.name)" }
                    participants = if ($state.party.members) { $state.party.members } else { @() }
                    choices = @()
                    outcomes = @{
                        encounter_completed = $true
                        encounter_name = $encounter.name
                    }
                }
            }
        }
    }
}

# Auto-detect quest completion from discoveries
if ($state.discoveries) {
    foreach ($discoveryName in $state.discoveries.PSObject.Properties.Name) {
        if ($state.discoveries[$discoveryName]) {
            # Check if discovery matches quest objectives
            foreach ($questId in $events.quests.Keys) {
                $quest = $events.quests[$questId]
                if ($quest.status -eq "active") {
                    $questItem = $quest.quest_item
                    $questLocation = $quest.quest_location
                    
                    # Check if discovery matches quest item or location
                    if ($questItem -and $discoveryName -match $questItem) {
                        if (-not $updatedQuests[$questId]) {
                            $updatedQuests[$questId] = @{}
                        }
                        $updatedQuests[$questId].status = "completed"
                        $updatedQuests[$questId].completion_timestamp = (Get-Date).ToString("o")
                        $updatedQuests[$questId].completion_notes = "Quest item discovered: $discoveryName"
                    }
                }
            }
        }
    }
}

# Apply updates
foreach ($event in $newEvents) {
    $events.events += $event
}

foreach ($questId in $updatedQuests.Keys) {
    $updates = $updatedQuests[$questId]
    foreach ($key in $updates.Keys) {
        $events.quests[$questId][$key] = $updates[$key]
    }
}

foreach ($npcName in $updatedNpcs.Keys) {
    $updates = $updatedNpcs[$npcName]
    if (-not $events.npcs[$npcName]) {
        $events.npcs[$npcName] = @{
            name = $npcName
            location = ""
            relationship = "neutral"
            status = "alive"
            interactions = @()
            notes = ""
        }
    }
    foreach ($key in $updates.Keys) {
        $events.npcs[$npcName][$key] = $updates[$key]
    }
}

# Update last_updated
$events.last_updated = (Get-Date).ToString("o")

# Save events file
try {
    $eventsDir = Split-Path $eventsFile -Parent
    if (-not (Test-Path $eventsDir)) {
        New-Item -ItemType Directory -Force -Path $eventsDir | Out-Null
    }
    ($events | ConvertTo-Json -Depth 10) | Set-Content -Path $eventsFile -Encoding UTF8
} catch {
    # Fail silently - event tracking is not critical
}

