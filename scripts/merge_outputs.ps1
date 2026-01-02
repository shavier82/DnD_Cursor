param(
    [Parameter(Mandatory=$true)]
    [string]$SessionId
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
$askText = "What would you like to do next?"
$rollPending = $false

if ($referee.roll_request -and $referee.roll_request.required -eq $true) {
    $rollPending = $true
    $skill = "skill check"
    if ($referee.roll_request.skill_or_check) { $skill = [string]$referee.roll_request.skill_or_check }

    $dc = 0
    if ($referee.roll_request.dc) { $dc = [int]$referee.roll_request.dc }

    $formula = "1d20"
    if ($referee.roll_request.formula) { $formula = [string]$referee.roll_request.formula }

    $askText = "PLAYER: Roll $skill vs DC $dc. Reply with TOTAL. (Formula: $formula)"
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

# Emit final user-facing output (strict 3 blocks)
Write-Output "NARRATION:"
Write-Output $narrationText
Write-Output ""
Write-Output "ASK:"
Write-Output $askText
Write-Output ""
Write-Output "PATCH:"
# Print JSON for PATCH on one line to be deterministic
Write-Output ($patchOut | ConvertTo-Json -Depth 20 -Compress)
