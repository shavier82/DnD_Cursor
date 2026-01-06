param(
    [Parameter(Mandatory = $true)]
    [string]$SessionId,
    
    [Parameter(Mandatory = $false)]
    [switch]$Quiet = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Fail([string]$msg) {
    Write-Output $msg
    exit 1
}

$CoordDir = Join-Path "C:\DnD" (".coord-" + $SessionId)
if (-not (Test-Path $CoordDir)) {
    Fail ("Coordination directory missing: " + $CoordDir)
}

# Hard fences
$RepoRoot     = "C:\DnD\DnD_Cursor"
$CampaignRoot = "C:\DnD\Campaigns"

$schemas = @{
    "REFEREE" = @{
        file = "dnd_out_REFEREE.json"
        requiredTop = @("agent_role","blocked","roll_request","mechanics_notes")
        requiredRoll = @("required")
    }
    "NARRATOR" = @{
        file = "dnd_out_NARRATOR.json"
        requiredTop = @("agent_role","blocked","narration")
    }
    "STATE_PATCHER" = @{
        file = "dnd_out_STATE_PATCHER.json"
        requiredTop = @("agent_role","blocked","patches")
    }
    "QA_COMPLIANCE" = @{
        file = "dnd_out_QA_COMPLIANCE.json"
        requiredTop = @("agent_role","blocked","status","issues")
    }
}

$errors = @()

if (-not $Quiet) {
Write-Output ("Validating agent outputs for session: " + $SessionId)
Write-Output ("Coord dir: " + $CoordDir)
}

foreach ($agent in $schemas.Keys) {
    $file = $schemas[$agent].file
    $path = Join-Path $CoordDir $file

    # Existence
    if (-not (Test-Path $path)) {
        $errors += ("{0}: missing file {1}" -f $agent, $file)
        continue
    }

    # Location fences (resolved path must start with CoordDir)
    $resolved = (Resolve-Path $path).Path
    if ($resolved -notlike ($CoordDir + "\*")) {
        $errors += ("{0}: wrong location {1}" -f $agent, $resolved)
        continue
    }
    if ($resolved -like ($RepoRoot + "\*")) {
        $errors += ("{0}: output inside repo (forbidden) {1}" -f $agent, $resolved)
        continue
    }
    if ($resolved -like ($CampaignRoot + "\*")) {
        $errors += ("{0}: output inside campaigns (forbidden) {1}" -f $agent, $resolved)
        continue
    }

    # JSON parse
    try {
        $raw = Get-Content -Path $path -Raw -Encoding UTF8
        $obj = $raw | ConvertFrom-Json
    } catch {
        $errors += ("{0}: invalid JSON in {1} - {2}" -f $agent, $file, $_.Exception.Message)
        continue
    }

    # Required top-level keys
    $missingTop = @()
    foreach ($k in $schemas[$agent].requiredTop) {
        if (-not (Get-Member -InputObject $obj -Name $k -MemberType NoteProperty -ErrorAction SilentlyContinue)) {
            $missingTop += $k
        }
    }
    if ($missingTop.Count -gt 0) {
        $errors += ("{0}: missing fields [{1}]" -f $agent, ($missingTop -join ", "))
        continue
    }

    # Role match
    if ($obj.agent_role -ne $agent) {
        $errors += ("{0}: agent_role mismatch (got '{1}')" -f $agent, $obj.agent_role)
        continue
    }

    # Type checks per agent
    if ($agent -eq "REFEREE") {
        foreach ($rk in $schemas[$agent].requiredRoll) {
            if (-not (Get-Member -InputObject $obj.roll_request -Name $rk -MemberType NoteProperty -ErrorAction SilentlyContinue)) {
                $errors += ("REFEREE: roll_request.{0} missing" -f $rk)
            }
        }
    }

    if ($agent -eq "STATE_PATCHER") {
        if (-not ($obj.patches -is [System.Collections.IEnumerable])) {
            $errors += "STATE_PATCHER: patches must be an array"
        }
    }

    if ($agent -eq "QA_COMPLIANCE") {
        if (-not ($obj.issues -is [System.Collections.IEnumerable])) {
            $errors += "QA_COMPLIANCE: issues must be an array"
        }
    }

    if (-not $Quiet) {
    Write-Output ("OK: " + $agent)
    }
}

if ($errors.Count -gt 0) {
    Write-Output "VALIDATION FAILED"
    foreach ($e in $errors) { Write-Output ("- " + $e) }
    exit 1
}

if (-not $Quiet) {
Write-Output "VALIDATION OK"
}
exit 0
