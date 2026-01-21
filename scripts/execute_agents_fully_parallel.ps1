# Execute Agents Fully Parallel
# Accepts JSON strings and writes ALL files (temp + final) in parallel using Start-Job

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

# Ensure coordination directory exists
if (-not (Test-Path $CoordDir)) {
    New-Item -ItemType Directory -Force -Path $CoordDir | Out-Null
}

Write-Host "`n=== Fully Parallel Agent Execution ===" -ForegroundColor Cyan
Write-Host "Session ID: $SessionId" -ForegroundColor White
Write-Host "Writing all 4 output files simultaneously..." -ForegroundColor Yellow

# Define output files
$outputFiles = @{
    REFEREE = Join-Path $CoordDir "dnd_out_REFEREE.json"
    NARRATOR = Join-Path $CoordDir "dnd_out_NARRATOR.json"
    STATE_PATCHER = Join-Path $CoordDir "dnd_out_STATE_PATCHER.json"
    QA_COMPLIANCE = Join-Path $CoordDir "dnd_out_QA_COMPLIANCE.json"
}

# Start all 4 write jobs simultaneously
$startTime = Get-Date
$jobs = @{}

$jobs["REFEREE"] = Start-Job -ScriptBlock {
    param($file, $json)
    $json | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $outputFiles["REFEREE"], $RefereeJson

$jobs["NARRATOR"] = Start-Job -ScriptBlock {
    param($file, $json)
    $json | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $outputFiles["NARRATOR"], $NarratorJson

$jobs["STATE_PATCHER"] = Start-Job -ScriptBlock {
    param($file, $json)
    $json | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $outputFiles["STATE_PATCHER"], $StatePatcherJson

$jobs["QA_COMPLIANCE"] = Start-Job -ScriptBlock {
    param($file, $json)
    $json | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $outputFiles["QA_COMPLIANCE"], $QAComplianceJson

# Wait for all jobs to complete
Write-Host "Waiting for all writes to complete..." -ForegroundColor Yellow
$jobs.Values | Wait-Job | Out-Null

# Collect results
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host "`n=== Completion Status ===" -ForegroundColor Cyan
$successCount = 0
foreach ($agent in @("REFEREE", "NARRATOR", "STATE_PATCHER", "QA_COMPLIANCE")) {
    $job = $jobs[$agent]
    try {
        Receive-Job -Job $job | Out-Null
        Remove-Job -Job $job
        
        if (Test-Path $outputFiles[$agent]) {
            $fileInfo = Get-Item $outputFiles[$agent]
            Write-Host "  [OK] $agent : $($fileInfo.Name) ($([math]::Round($fileInfo.Length/1KB, 2)) KB)" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  [FAIL] $agent : Output file missing" -ForegroundColor Red
        }
    } catch {
        Write-Host "  [FAIL] $agent : $_" -ForegroundColor Red
    }
}

Write-Host "`nTotal time: $([math]::Round($duration, 2)) seconds" -ForegroundColor White
Write-Host "Successful: $successCount/4" -ForegroundColor $(if ($successCount -eq 4) { "Green" } else { "Yellow" })

if ($successCount -eq 4) {
    Write-Host "`n[SUCCESS] All agents completed in parallel!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n[FAILURE] Some agents failed" -ForegroundColor Red
    exit 1
}
































