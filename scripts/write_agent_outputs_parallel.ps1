# Write Agent Outputs in Parallel - Main Entry Point
# This script accepts agent output JSON content and writes them in parallel

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
$TempDir = $env:TEMP

# Write temporary JSON files
$tempFiles = @{
    REFEREE = Join-Path $TempDir "agent_referee_$SessionId.json"
    NARRATOR = Join-Path $TempDir "agent_narrator_$SessionId.json"
    STATE_PATCHER = Join-Path $TempDir "agent_statepatcher_$SessionId.json"
    QA_COMPLIANCE = Join-Path $TempDir "agent_qacompliance_$SessionId.json"
}

$RefereeJson | Out-File -FilePath $tempFiles.REFEREE -Encoding UTF8 -NoNewline
$NarratorJson | Out-File -FilePath $tempFiles.NARRATOR -Encoding UTF8 -NoNewline
$StatePatcherJson | Out-File -FilePath $tempFiles.STATE_PATCHER -Encoding UTF8 -NoNewline
$QAComplianceJson | Out-File -FilePath $tempFiles.QA_COMPLIANCE -Encoding UTF8 -NoNewline

# Call the parallel execution script
$scriptPath = Join-Path $PSScriptRoot "create_agent_outputs_parallel.ps1"
& $scriptPath -SessionId $SessionId -TempDir $TempDir


















