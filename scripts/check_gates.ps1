# Check Gates Helper Script
# Validates that gates are properly enforced

param(
    [Parameter(Mandatory=$true)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [string]$StateFile = "C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json"
)

$ErrorActionPreference = "Stop"

# Load state
if (-not (Test-Path $StateFile)) {
    Write-Output "WARNING: State file not found: $StateFile"
    Write-Output "All gates are considered NOT passed"
    exit 0
}

$state = Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json

# Load REFEREE output
$CoordDir = "C:\DnD\.coord-$SessionId"
$refereeFile = Join-Path $CoordDir "dnd_out_REFEREE.json"

if (-not (Test-Path $refereeFile)) {
    Write-Output "ERROR: REFEREE output not found: $refereeFile"
    exit 1
}

$referee = Get-Content $refereeFile -Raw -Encoding UTF8 | ConvertFrom-Json

# Check if gates exist in state
if (-not $state.gates) {
    Write-Output "INFO: No gates tracked in state"
} else {
    Write-Output "=== Gates Status ==="
    foreach ($gate in $state.gates.PSObject.Properties) {
        $status = if ($gate.Value) { "PASSED" } else { "NOT PASSED" }
        Write-Output "  $($gate.Name): $status"
    }
}

# Check if discoveries exist
if ($state.discoveries) {
    Write-Output "`n=== Discoveries ==="
    foreach ($discovery in $state.discoveries.PSObject.Properties) {
        $status = if ($discovery.Value) { "DISCOVERED" } else { "NOT DISCOVERED" }
        Write-Output "  $($discovery.Name): $status"
    }
}

# Check if REFEREE requested a roll
if ($referee.roll_request -and $referee.roll_request.required -eq $true) {
    Write-Output "`n=== Roll Requested ==="
    Write-Output "  Skill/Check: $($referee.roll_request.skill_or_check)"
    Write-Output "  DC: $($referee.roll_request.dc)"
    Write-Output "  Formula: $($referee.roll_request.formula)"
    Write-Output "  Reason: $($referee.roll_request.reason)"
}

Write-Output "`n=== Gate Enforcement Check ==="
Write-Output "State loaded: YES"
Write-Output "Gates tracked: $($state.gates.PSObject.Properties.Count)"
Write-Output "Discoveries tracked: $($state.discoveries.PSObject.Properties.Count)"



