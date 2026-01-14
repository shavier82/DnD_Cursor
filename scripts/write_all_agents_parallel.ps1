# Write All Agent Outputs in Parallel
# Reads a single JSON file containing all 4 agent outputs and writes them in parallel using Start-Job

param(
    [Parameter(Mandatory=$true)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$true)]
    [string]$AgentOutputsFile
)

$ErrorActionPreference = "Stop"
$CoordDir = "C:\DnD\.coord-$SessionId"

# Ensure coordination directory exists
if (-not (Test-Path $CoordDir)) {
    New-Item -ItemType Directory -Force -Path $CoordDir | Out-Null
}

# Read the agent outputs file
if (-not (Test-Path $AgentOutputsFile)) {
    Write-Error "Agent outputs file not found: $AgentOutputsFile"
    exit 1
}

$allOutputs = Get-Content -Path $AgentOutputsFile -Raw -Encoding UTF8 | ConvertFrom-Json

Write-Host "`n=== Writing All Agent Outputs in Parallel ===" -ForegroundColor Cyan
Write-Host "Session ID: $SessionId" -ForegroundColor White

# Define output files
$outputFiles = @{
    REFEREE = Join-Path $CoordDir "dnd_out_REFEREE.json"
    NARRATOR = Join-Path $CoordDir "dnd_out_NARRATOR.json"
    STATE_PATCHER = Join-Path $CoordDir "dnd_out_STATE_PATCHER.json"
    QA_COMPLIANCE = Join-Path $CoordDir "dnd_out_QA_COMPLIANCE.json"
}

# Convert each agent output to JSON string
$refereeJson = $allOutputs.REFEREE | ConvertTo-Json -Depth 10 -Compress
$narratorJson = $allOutputs.NARRATOR | ConvertTo-Json -Depth 10 -Compress
$statePatcherJson = $allOutputs.STATE_PATCHER | ConvertTo-Json -Depth 10 -Compress
$qaComplianceJson = $allOutputs.QA_COMPLIANCE | ConvertTo-Json -Depth 10 -Compress

# Start all 4 write jobs simultaneously
$startTime = Get-Date
$jobs = @{}

Write-Host "Spawning 4 parallel write jobs..." -ForegroundColor Yellow

$jobs["REFEREE"] = Start-Job -ScriptBlock {
    param($file, $json)
    $json | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $outputFiles["REFEREE"], $refereeJson

$jobs["NARRATOR"] = Start-Job -ScriptBlock {
    param($file, $json)
    $json | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $outputFiles["NARRATOR"], $narratorJson

$jobs["STATE_PATCHER"] = Start-Job -ScriptBlock {
    param($file, $json)
    $json | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $outputFiles["STATE_PATCHER"], $statePatcherJson

$jobs["QA_COMPLIANCE"] = Start-Job -ScriptBlock {
    param($file, $json)
    $json | Out-File -FilePath $file -Encoding UTF8 -NoNewline
} -ArgumentList $outputFiles["QA_COMPLIANCE"], $qaComplianceJson

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
