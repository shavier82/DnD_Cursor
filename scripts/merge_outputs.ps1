param(
    [Parameter(Mandatory=$true)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [switch]$ShowPatch = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$FastMode = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Blocked([string]$Reason) {
    # Final merge must emit a single BLOCKED line (and stop)
    Write-Output ("BLOCKED: Pack missing required data: " + $Reason)
    exit 1
}

function Read-JsonFile([string]$Path) {
    if (-not (Test-Path $Path)) {
        Write-Blocked ("Missing agent output file " + (Split-Path $Path -Leaf))
    }
    try {
        $raw = Get-Content -Path $Path -Raw -Encoding UTF8
        return ($raw | ConvertFrom-Json)
    } catch {
        Write-Blocked ("Invalid JSON in " + (Split-Path $Path -Leaf) + " - " + $_.Exception.Message)
    }
}

# Coordination directory convention
$CoordDir = "C:\DnD\.coord-$SessionId"
if (-not (Test-Path $CoordDir)) {
    Write-Blocked ("Coordination directory not found: " + $CoordDir)
}

# Expected agent output files
$files = @{
    "REFEREE"       = Join-Path $CoordDir "dnd_out_REFEREE.json"
    "NARRATOR"      = Join-Path $CoordDir "dnd_out_NARRATOR.json"
    "STATE_PATCHER" = Join-Path $CoordDir "dnd_out_STATE_PATCHER.json"
    "QA_COMPLIANCE" = Join-Path $CoordDir "dnd_out_QA_COMPLIANCE.json"
}

# Load agent outputs
$referee = Read-JsonFile $files["REFEREE"]
$narrator = Read-JsonFile $files["NARRATOR"]
$patcher = Read-JsonFile $files["STATE_PATCHER"]
$qa = Read-JsonFile $files["QA_COMPLIANCE"]

# Hard block propagation
foreach ($a in @($referee, $narrator, $patcher, $qa)) {
    if ($null -ne $a.blocked -and $a.blocked -eq $true) {
        # If agent provides a reason, use it; else generic
        if ($a.reason) { Write-Blocked ($a.reason) }
        if ($a.block_reason) { Write-Blocked ($a.block_reason) }
        Write-Blocked ("Agent blocked: " + $a.agent_role)
    }
}

# QA gate
if ($qa.status -and $qa.status -ne "ok") {
    $issues = ""
    if ($qa.issues) { $issues = ($qa.issues -join "; ") }
    if ([string]::IsNullOrWhiteSpace($issues)) { $issues = "QA validation failed" }
    Write-Blocked ($issues)
}

# Compose final blocks
$narrationText = ""
if ($narrator.narration) { $narrationText = [string]$narrator.narration }
if ([string]::IsNullOrWhiteSpace($narrationText)) { $narrationText = "(none)" }

# ASK logic from referee roll_request
$askText = "(none)"
$rollPending = $false

if ($referee.roll_request -and $referee.roll_request.required -eq $true) {
    $rollPending = $true
    $skill = "skill check"
    if ($referee.roll_request.skill_or_check) { $skill = [string]$referee.roll_request.skill_or_check }

    $dc = 0
    if ($referee.roll_request.dc) { $dc = [int]$referee.roll_request.dc }

    $formula = "1d20"
    if ($referee.roll_request.formula) { $formula = [string]$referee.roll_request.formula }

    # Check if it's an attack roll (use AC instead of DC)
    if ($skill -match "attack|AC") {
        $askText = "PLAYER: Roll $skill. Reply with TOTAL. (Formula: $formula)"
    } elseif ($skill -match "initiative" -or $dc -eq 0 -and $skill -notmatch "check|save") {
        # Initiative or other non-DC rolls (dc=0 means no DC)
        $askText = "PLAYER: Roll $skill. Reply with TOTAL. (Formula: $formula)"
    } else {
        $askText = "PLAYER: Roll $skill vs DC $dc. Reply with TOTAL. (Formula: $formula)"
    }
}

# PATCH rules: must be [] if roll pending
$patchOut = @()
if (-not $rollPending) {
    if ($patcher.patches) {
        # Ensure array output
        if ($patcher.patches -is [System.Array]) {
            $patchOut = $patcher.patches
        } else {
            # Single object -> wrap
            $patchOut = @($patcher.patches)
        }
    } else {
        $patchOut = @()
    }
}

# Write MERGE JSON artifact (optional but useful)
$mergeJson = @{
    agent_role = "MERGE"
    blocked    = $false
    final      = @{
        NARRATION = $narrationText
        ASK       = $askText
        PATCH     = $patchOut
    }
} | ConvertTo-Json -Depth 20

$mergePath = Join-Path $CoordDir "dnd_out_MERGE.json"
Set-Content -Path $mergePath -Value $mergeJson -Encoding UTF8

# Save game state after merge (if patches indicate scene/encounter/gates completion)
# Ensure patches is an array before checking count
$patchesToCheck = if ($patcher.patches -is [System.Array]) { $patcher.patches } else { @($patcher.patches) }
$patchesCount = if ($patchesToCheck) { if ($patchesToCheck -is [System.Array]) { $patchesToCheck.Length } else { 1 } } else { 0 }
if ($patchesCount -gt 0) {
    # Convert patches to array to avoid PSObject indexing issues
    $patchesArray = @($patchesToCheck | ForEach-Object { $_ })
    
    # Check if patches indicate scene transition, encounter end, or gate/discovery updates
    $shouldSave = $false
    foreach ($patch in $patchesArray) {
        $pathStr = $patch.path
        if ($pathStr -match "/scene/|/encounter/|/combat/ended|/chapter/|/gates/|/discoveries/") {
            $shouldSave = $true
            break
        }
    }
    
    if ($shouldSave) {
        # Load paths config
        $configPath = Join-Path $PSScriptRoot "..\config\paths.json"
        if (Test-Path $configPath) {
            $config = Get-Content $configPath -Raw | ConvertFrom-Json
            $stateFile = $config.state_file
            
            # Load existing state
            $currentState = @{
                timestamp = (Get-Date).ToString("o")
                scene = @{}
                party = @{}
                combat = @{}
                encounters = @()
                gates = @{}
                discoveries = @()
            }
            
            if (Test-Path $stateFile) {
                try {
                    $existing = Get-Content $stateFile -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($existing) {
                        $currentState = $existing
                        $currentState.timestamp = (Get-Date).ToString("o")
                    }
                } catch {
                    # Use default state if load fails
                }
            }
            
            # Apply patches to state using JSON conversion to avoid PSObject issues
            # OPTIMIZATION: Convert state ONCE before loop, apply all patches, convert once after
            try {
                # Convert state to hashtable once before applying patches
                $stateJson = $currentState | ConvertTo-Json -Depth 20 -Compress
                $stateHash = $stateJson | ConvertFrom-Json -AsHashtable
                if (-not $stateHash) {
                    $stateHash = $stateJson | ConvertFrom-Json
                    # Convert PSObject to hashtable
                    $tempHash = @{}
                    $stateHash.PSObject.Properties | ForEach-Object {
                        $tempHash[$_.Name] = $_.Value
                    }
                    $stateHash = $tempHash
                }
                
                # Ensure required sections exist
                if (-not $stateHash.scene) { $stateHash.scene = @{} }
                if (-not $stateHash.combat) { $stateHash.combat = @{} }
                if (-not $stateHash.combat.combatants) { $stateHash.combat.combatants = @{} }
                if (-not $stateHash.combat.turn_narratives) { $stateHash.combat.turn_narratives = @() }
                if (-not $stateHash.encounters) { $stateHash.encounters = @() }
                if (-not $stateHash.gates) { $stateHash.gates = @{} }
                if (-not $stateHash.discoveries) { $stateHash.discoveries = @{} }
                
                # Apply all patches to hashtable
                foreach ($patch in $patchesArray) {
                    $path = $patch.path
                    $op = $patch.op
                    $value = $patch.value
                    
                    # Handle nested paths properly using hashtable
                    if ($path -match "^/scene/") {
                        $key = $path -replace "^/scene/", ""
                        if (-not $stateHash.scene) { $stateHash.scene = @{} }
                        if ($op -eq "add" -or $op -eq "replace") {
                            $stateHash.scene[$key] = $value
                        } elseif ($op -eq "remove") {
                            $stateHash.scene.Remove($key)
                        }
                    } elseif ($path -match "^/combat/") {
                        $key = $path -replace "^/combat/", ""
                        if (-not $stateHash.combat) { $stateHash.combat = @{} }
                        # Handle nested paths like /combat/combatants/Ogre Zombie 2/status
                        if ($key -match "^combatants/") {
                            $combatantPath = $key -replace "^combatants/", ""
                            $parts = @($combatantPath -split "/")
                            $combatantName = $parts[0]
                            if (-not $stateHash.combat.combatants) { 
                                $stateHash.combat.combatants = @{} 
                            }
                            if ($parts.Length -eq 1) {
                                # Direct combatant property
                                if ($op -eq "add" -or $op -eq "replace") {
                                    $stateHash.combat.combatants[$combatantName] = $value
                                } elseif ($op -eq "remove") {
                                    $stateHash.combat.combatants.Remove($combatantName)
                                }
                            } else {
                                # Nested property like /combat/combatants/Ogre Zombie 2/status
                                if (-not $stateHash.combat.combatants[$combatantName]) {
                                    $stateHash.combat.combatants[$combatantName] = @{}
                                }
                                $nestedKey = $parts[1]
                                if ($op -eq "add" -or $op -eq "replace") {
                                    $stateHash.combat.combatants[$combatantName][$nestedKey] = $value
                                } elseif ($op -eq "remove") {
                                    $stateHash.combat.combatants[$combatantName].Remove($nestedKey)
                                }
                            }
                        } elseif ($key -match "^turn_narratives/") {
                            # Handle array append with /- syntax
                            if (-not $stateHash.combat.turn_narratives) { $stateHash.combat.turn_narratives = @() }
                            # Ensure turn_narratives is an array
                            if ($stateHash.combat.turn_narratives -isnot [System.Array]) {
                                $stateHash.combat.turn_narratives = @($stateHash.combat.turn_narratives)
                            }
                            if ($op -eq "add" -and $key -match "/-$") {
                                $stateHash.combat.turn_narratives += $value
                            }
                        } else {
                            # Simple combat property
                            if ($op -eq "add" -or $op -eq "replace") {
                                $stateHash.combat[$key] = $value
                            } elseif ($op -eq "remove") {
                                $stateHash.combat.Remove($key)
                            }
                        }
                    } elseif ($path -match "^/encounter/") {
                        $key = $path -replace "^/encounter/", ""
                        if (-not $stateHash.encounters) { $stateHash.encounters = @() }
                        $encounterExists = $false
                        foreach ($enc in $stateHash.encounters) {
                            if ($enc.name -eq $key) {
                                $encounterExists = $true
                                $enc.completed = $true
                                $enc.timestamp = (Get-Date).ToString("o")
                                break
                            }
                        }
                        if (-not $encounterExists) {
                            $stateHash.encounters += @{
                                name = $key
                                completed = $true
                                timestamp = (Get-Date).ToString("o")
                            }
                        }
                    } elseif ($path -match "^/gates/") {
                        # CRITICAL: Gates tracking for mandatory information control system
                        $gateName = $path -replace "^/gates/", ""
                        if (-not $stateHash.gates) { $stateHash.gates = @{} }
                        if ($op -eq "add" -or $op -eq "replace") {
                            $stateHash.gates[$gateName] = $value
                        } elseif ($op -eq "remove") {
                            $stateHash.gates.Remove($gateName)
                        }
                    } elseif ($path -match "^/discoveries/") {
                        # CRITICAL: Discoveries tracking for mandatory information control system
                        $discoveryName = $path -replace "^/discoveries/", ""
                        if ($op -eq "add" -or $op -eq "replace") {
                            $stateHash.discoveries[$discoveryName] = $value
                        } elseif ($op -eq "remove") {
                            $stateHash.discoveries.Remove($discoveryName)
                        }
                    }
                }
                
                # Convert back to object once after all patches applied
                $currentState = $stateHash | ConvertTo-Json -Depth 20 | ConvertFrom-Json
            } catch {
                # If patch application fails, continue without updating state
                # Fail silently - patch application failures are not critical
            }
            
            # Save state
            # OPTIMIZATION: Use Compress for faster JSON serialization
            try {
                $stateDir = Split-Path $stateFile -Parent
                if (-not (Test-Path $stateDir)) {
                    New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
                }
                # Use -Compress for faster serialization (smaller file, faster write)
                ($currentState | ConvertTo-Json -Depth 10 -Compress) | Set-Content -Path $stateFile -Encoding UTF8 -NoNewline
            } catch {
                # Fail silently - state save is not critical
            }
            
            # Auto-track events and quests (skip in fast mode)
            # OPTIMIZATION: Only spawn job if patches contain event-related paths
            if (-not $FastMode) {
                try {
                    # Check if patches contain event-related paths (avoid unnecessary job spawn)
                    $hasEventPatches = $patchesArray | Where-Object { 
                        $_.path -match "^/encounter/|^/discoveries/|^/scene/location" 
                    } | Select-Object -First 1
                    
                    if ($hasEventPatches) {
                        $autoTrackerScript = Join-Path $PSScriptRoot "auto_event_tracker.ps1"
                        if (Test-Path $autoTrackerScript) {
                            $campaignName = if ($currentState.campaign) { $currentState.campaign } else { "Phandelver" }
                            $patchesForTracker = if ($patcher.patches -is [System.Array]) { $patcher.patches } else { @($patcher.patches) }
                            if ($patchesForTracker -and $patchesForTracker.Count -gt 0) {
                                # Run in background job to avoid blocking
                                Start-Job -ScriptBlock {
                                    param($script, $campaign, $stateFile, $patches)
                                    & $script -Campaign $campaign -StateFile $stateFile -Patches $patches
                                } -ArgumentList $autoTrackerScript, $campaignName, $stateFile, ($patchesForTracker | ConvertTo-Json -Depth 10) | Out-Null
                            }
                        }
                    }
                } catch {
                    # Fail silently - auto-tracking is not critical
                }
            }
            
            # Combine combat narratives when combat ends (skip in fast mode)
            # OPTIMIZATION: Only spawn job if combat actually ended (check patches for /combat/ended)
            if (-not $FastMode) {
                try {
                    # Check if combat ended patch exists (avoid unnecessary job spawn if combat already ended)
                    $combatEndedPatch = $patchesArray | Where-Object { 
                        $_.path -eq "/combat/ended" -and $_.value -eq $true 
                    } | Select-Object -First 1
                    
                    if ($combatEndedPatch -or ($currentState.combat -and $currentState.combat.ended -and $currentState.combat.turn_narratives)) {
                        $combineScript = Join-Path $PSScriptRoot "combine_combat_narrative.ps1"
                        if (Test-Path $combineScript) {
                            $campaignName = if ($currentState.campaign) { $currentState.campaign } else { "Phandelver" }
                            # Run in background job to avoid blocking
                            Start-Job -ScriptBlock {
                                param($script, $campaign, $stateFile)
                                & $script -Campaign $campaign -StateFile $stateFile
                            } -ArgumentList $combineScript, $campaignName, $stateFile | Out-Null
                        }
                    }
                } catch {
                    # Fail silently - narrative combination is not critical
                }
            }
        }
    }
}

# Suggested actions from NARRATOR (if provided)
$suggestedActions = @()
if ($narrator.suggested_actions) {
    if ($narrator.suggested_actions -is [System.Array]) {
        $suggestedActions = $narrator.suggested_actions
    } else {
        $suggestedActions = @($narrator.suggested_actions)
    }
}

# Emit final user-facing output (NARRATION, ASK, and ACTIONS - PATCH is applied but not displayed)
Write-Output "NARRATION:"
Write-Output $narrationText
Write-Output ""
Write-Output "ASK:"
Write-Output $askText
Write-Output ""
Write-Output "ACTIONS:"
if ($suggestedActions.Count -gt 0) {
    foreach ($action in $suggestedActions) {
        Write-Output "- $action"
    }
} else {
    Write-Output "(none)"
}
# PATCH is applied to state but not displayed to user (hidden from chat output)
