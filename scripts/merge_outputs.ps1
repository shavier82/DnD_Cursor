param(
    [Parameter(Mandatory=$true)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [switch]$ShowPatch = $false
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
if ($patcher.patches -and $patcher.patches.Count -gt 0) {
    # Check if patches indicate scene transition, encounter end, or gate/discovery updates
    $shouldSave = $false
    foreach ($patch in $patcher.patches) {
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
            
            # Apply patches to state
            foreach ($patch in $patcher.patches) {
                $path = $patch.path
                $op = $patch.op
                $value = $patch.value
                
                # Simple patch application (basic paths only)
                if ($path -match "^/scene/") {
                    $key = $path -replace "^/scene/", ""
                    if ($op -eq "add" -or $op -eq "replace") {
                        $currentState.scene[$key] = $value
                    } elseif ($op -eq "remove") {
                        $currentState.scene.Remove($key)
                    }
                } elseif ($path -match "^/combat/") {
                    $key = $path -replace "^/combat/", ""
                    if ($op -eq "add" -or $op -eq "replace") {
                        $currentState.combat[$key] = $value
                    } elseif ($op -eq "remove") {
                        $currentState.combat.Remove($key)
                    }
                } elseif ($path -match "^/encounter/") {
                    $key = $path -replace "^/encounter/", ""
                    if ($op -eq "add" -or $op -eq "replace") {
                        if (-not $currentState.encounters) { $currentState.encounters = @() }
                        $encounterExists = $false
                        foreach ($enc in $currentState.encounters) {
                            if ($enc.name -eq $key) {
                                $encounterExists = $true
                                $enc.completed = $true
                                $enc.timestamp = (Get-Date).ToString("o")
                                break
                            }
                        }
                        if (-not $encounterExists) {
                            $currentState.encounters += @{
                                name = $key
                                completed = $true
                                timestamp = (Get-Date).ToString("o")
                            }
                        }
                    }
                } elseif ($path -match "^/gates/") {
                    # CRITICAL: Gates tracking for mandatory information control system
                    $gateName = $path -replace "^/gates/", ""
                    if (-not $currentState.gates) { $currentState.gates = @{} }
                    if ($op -eq "add" -or $op -eq "replace") {
                        $currentState.gates[$gateName] = $value
                    } elseif ($op -eq "remove") {
                        $currentState.gates.Remove($gateName)
                    }
                } elseif ($path -match "^/discoveries/") {
                    # CRITICAL: Discoveries tracking for mandatory information control system
                    $discoveryName = $path -replace "^/discoveries/", ""
                    if (-not $currentState.discoveries) { $currentState.discoveries = @{} }
                    if ($op -eq "add" -or $op -eq "replace") {
                        $currentState.discoveries[$discoveryName] = $value
                    } elseif ($op -eq "remove") {
                        $currentState.discoveries.Remove($discoveryName)
                    }
                }
            }
            
            # Save state
            try {
                $stateDir = Split-Path $stateFile -Parent
                if (-not (Test-Path $stateDir)) {
                    New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
                }
                ($currentState | ConvertTo-Json -Depth 10) | Set-Content -Path $stateFile -Encoding UTF8
            } catch {
                # Fail silently - state save is not critical
            }
            
            # Auto-track events and quests
            try {
                $autoTrackerScript = Join-Path $PSScriptRoot "auto_event_tracker.ps1"
                if (Test-Path $autoTrackerScript) {
                    $campaignName = if ($currentState.campaign) { $currentState.campaign } else { "Phandelver" }
                    if ($patcher.patches -and $patcher.patches.Count -gt 0) {
                        & $autoTrackerScript -Campaign $campaignName -StateFile $stateFile -Patches $patcher.patches
                    }
                }
            } catch {
                # Fail silently - auto-tracking is not critical
            }
        }
    }
}

# Emit final user-facing output (EXACTLY three blocks per .cursorrules contract)
Write-Output "NARRATION:"
Write-Output $narrationText
Write-Output ""
Write-Output "ASK:"
Write-Output $askText
Write-Output ""
Write-Output "PATCH:"
# Print JSON for PATCH on one line to be deterministic
# Always output PATCH block (empty array [] if no patches, per contract requirement)
if ($patchOut.Count -eq 0) {
    Write-Output "[]"
} else {
    Write-Output ($patchOut | ConvertTo-Json -Depth 20 -Compress)
}
