# Run Parallel Agents - True Parallel Execution
# Spawns 4 separate PowerShell jobs to write agent outputs simultaneously using Start-Job
# This ensures all 4 agent output files are written in parallel, not sequentially

param(
    [Parameter(Mandatory=$true)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$AgentOutputs = @{}
)

$ErrorActionPreference = "Stop"
$CoordDir = "C:\DnD\.coord-$SessionId"

# Verify coordination directory exists
if (-not (Test-Path $CoordDir)) {
    Write-Error "Coordination directory does not exist: $CoordDir"
    exit 1
}

# Agent roles
$agents = @("REFEREE", "NARRATOR", "STATE_PATCHER", "QA_COMPLIANCE")

Write-Host "`n=== Starting Parallel Agent Execution ===" -ForegroundColor Cyan
Write-Host "Session ID: $SessionId" -ForegroundColor White
Write-Host "Coordination Directory: $CoordDir" -ForegroundColor White
Write-Host "`nSpawning $($agents.Count) agent jobs..." -ForegroundColor Yellow

# Function to write agent output file in parallel
function Write-AgentOutput {
    param(
        [string]$AgentRole,
        [string]$SessionId,
        [object]$OutputData
    )
    
    $outputFile = "C:\DnD\.coord-$SessionId\dnd_out_$AgentRole.json"
    
    # Ensure output directory exists
    $outputDir = Split-Path $outputFile -Parent
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    }
    
    # Write the JSON output
    $OutputData | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputFile -Encoding UTF8
    
    return @{
        agent = $AgentRole
        success = $true
        outputFile = $outputFile
    }
}

# Check if agent outputs were provided
if ($AgentOutputs.Count -eq 0) {
    Write-Warning "No agent outputs provided. This script requires pre-generated agent outputs."
    Write-Host "Usage: .\run_agents_parallel.ps1 -SessionId <id> -AgentOutputs @{REFEREE=<obj>; NARRATOR=<obj>; ...}" -ForegroundColor Yellow
    exit 1
}

# Verify all required agent outputs are provided
$missing = @()
foreach ($agent in $agents) {
    if (-not $AgentOutputs.ContainsKey($agent)) {
        $missing += $agent
    }
}

if ($missing.Count -gt 0) {
    Write-Error "Missing agent outputs: $($missing -join ', ')"
    exit 1
}

# Start all agents as background jobs to write files in parallel
$jobs = @{}
$startTime = Get-Date

foreach ($agent in $agents) {
    Write-Host "  Starting $agent write job..." -ForegroundColor Cyan
    
    # Serialize the output data to pass to the job
    $outputJson = $AgentOutputs[$agent] | ConvertTo-Json -Depth 10 -Compress
    
    $jobs[$agent] = Start-Job -ScriptBlock {
        param($agentRole, $sessionId, $outputJson)
        
        $outputFile = "C:\DnD\.coord-$sessionId\dnd_out_$agentRole.json"
        
        # Ensure output directory exists
        $outputDir = Split-Path $outputFile -Parent
        if (-not (Test-Path $outputDir)) {
            New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
        }
        
        # Deserialize and write the JSON output
        $outputData = $outputJson | ConvertFrom-Json
        $outputData | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputFile -Encoding UTF8
        
        return @{
            agent = $agentRole
            success = $true
            outputFile = $outputFile
        }
    } -ArgumentList $agent, $SessionId, $outputJson
}

Write-Host "`nAll $($agents.Count) jobs started. Waiting for completion..." -ForegroundColor Yellow

# Wait for all jobs to complete with timeout
$timeout = 30 # seconds
$elapsed = 0
$allComplete = $false

while (-not $allComplete -and $elapsed -lt $timeout) {
    $running = ($jobs.Values | Where-Object { $_.State -eq "Running" }).Count
    if ($running -eq 0) {
        $allComplete = $true
        break
    }
    Start-Sleep -Milliseconds 100
    $elapsed += 0.1
}

if (-not $allComplete) {
    Write-Warning "Timeout waiting for agents to complete. Some jobs may still be running."
}

# Collect results
Write-Host "`n=== Agent Completion Status ===" -ForegroundColor Cyan
$results = @{}
$successCount = 0
$failCount = 0

foreach ($agent in $agents) {
    $job = $jobs[$agent]
    
    if ($job.State -eq "Completed") {
        try {
            $result = Receive-Job -Job $job
            Remove-Job -Job $job
            
            $outputFile = "C:\DnD\.coord-$SessionId\dnd_out_$agent.json"
            if (Test-Path $outputFile) {
                Write-Host "  [OK] $agent completed successfully" -ForegroundColor Green
                $results[$agent] = $result
                $successCount++
            } else {
                Write-Host "  [FAIL] $agent completed but output file missing" -ForegroundColor Red
                $failCount++
            }
        } catch {
            Write-Host "  [FAIL] $agent failed: $_" -ForegroundColor Red
            $failCount++
        }
    } elseif ($job.State -eq "Failed") {
        Write-Host "  [FAIL] $agent job failed" -ForegroundColor Red
        $error = Receive-Job -Job $job -ErrorAction SilentlyContinue
        if ($error) {
            Write-Host "    Error: $error" -ForegroundColor Red
        }
        Remove-Job -Job $job
        $failCount++
    } else {
        Write-Host "  [WARN] $agent still running (State: $($job.State))" -ForegroundColor Yellow
        Stop-Job -Job $job
        Remove-Job -Job $job
        $failCount++
    }
}

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host "`n=== Execution Summary ===" -ForegroundColor Cyan
Write-Host "Total time: $([math]::Round($duration, 2)) seconds" -ForegroundColor White
Write-Host "Successful: $successCount/$($agents.Count)" -ForegroundColor $(if ($successCount -eq $agents.Count) { "Green" } else { "Yellow" })
Write-Host "Failed: $failCount/$($agents.Count)" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Red" })

# Verify all output files exist
Write-Host "`n=== Output File Verification ===" -ForegroundColor Cyan
$allFilesExist = $true
foreach ($agent in $agents) {
    $outputFile = "C:\DnD\.coord-$SessionId\dnd_out_$agent.json"
    if (Test-Path $outputFile) {
        $fileInfo = Get-Item $outputFile
        Write-Host "  [OK] $agent : $($fileInfo.Name) ($([math]::Round($fileInfo.Length/1KB, 2)) KB)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $agent : Output file missing" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if ($allFilesExist -and $successCount -eq $agents.Count) {
    Write-Host "`n[SUCCESS] All agents completed successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n[FAILURE] Some agents failed or outputs are missing" -ForegroundColor Red
    exit 1
}
