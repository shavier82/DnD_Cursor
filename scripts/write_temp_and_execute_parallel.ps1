# Write Temp Files and Execute Parallel - All in Parallel
# This script accepts agent output JSON strings and writes temp files in parallel, then executes parallel write

param(
    [Parameter(Mandatory=$true)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$true)]
    [string]$RefereeJson,
    
    [Parameter(Mandatory=$true)]
    [string]$NarratorJson,
    
    [Parameter(Mandatory=$true)]
    [string]$StatePatcherJson,
    
    [Parameter(Mandatory=$true)]
    [string]$QAComplianceJson
)

$ErrorActionPreference = "Stop"
$CoordDir = "C:\DnD\.coord-$SessionId"
$TempDir = Join-Path $CoordDir "temp"

# Ensure directories exist
if (-not (Test-Path $CoordDir)) {
    New-Item -ItemType Directory -Force -Path $CoordDir | Out-Null
}
if (-not (Test-Path $TempDir)) {
    New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
}

Write-Host "`n=== Writing Temp Files in Parallel ===" -ForegroundColor Cyan

# Write all 4 temp files in parallel using Start-Job
$tempFiles = @{
    REFEREE = Join-Path $TempDir "agent_referee_$SessionId.json"
    NARRATOR = Join-Path $TempDir "agent_narrator_$SessionId.json"
    STATE_PATCHER = Join-Path $TempDir "agent_statepatcher_$SessionId.json"
    QA_COMPLIANCE = Join-Path $TempDir "agent_qacompliance_$SessionId.json"
}

$tempJobs = @{}
$tempJobs["REFEREE"] = Start-Job -ScriptBlock {
    param($file, $content)
    $content | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $tempFiles["REFEREE"], $RefereeJson

$tempJobs["NARRATOR"] = Start-Job -ScriptBlock {
    param($file, $content)
    $content | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $tempFiles["NARRATOR"], $NarratorJson

$tempJobs["STATE_PATCHER"] = Start-Job -ScriptBlock {
    param($file, $content)
    $content | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $tempFiles["STATE_PATCHER"], $StatePatcherJson

$tempJobs["QA_COMPLIANCE"] = Start-Job -ScriptBlock {
    param($file, $content)
    $content | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $tempFiles["QA_COMPLIANCE"], $QAComplianceJson

# Wait for all temp file writes to complete
Write-Host "Waiting for temp files to be written..." -ForegroundColor Yellow
$tempJobs.Values | Wait-Job | Out-Null

# Verify temp files exist
$allTempFilesExist = $true
foreach ($agent in @("REFEREE", "NARRATOR", "STATE_PATCHER", "QA_COMPLIANCE")) {
    $job = $tempJobs[$agent]
    Receive-Job -Job $job | Out-Null
    Remove-Job -Job $job
    
    if (Test-Path $tempFiles[$agent]) {
        Write-Host "  [OK] $agent temp file written" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $agent temp file missing" -ForegroundColor Red
        $allTempFilesExist = $false
    }
}

if (-not $allTempFilesExist) {
    Write-Error "Failed to write all temp files"
    exit 1
}

Write-Host "`n=== Executing Parallel Write ===" -ForegroundColor Cyan

# Now call the parallel execution script
$scriptPath = Join-Path $PSScriptRoot "create_agent_outputs_parallel.ps1"
& $scriptPath -SessionId $SessionId

Write-Host "`n=== Complete ===" -ForegroundColor Green


















