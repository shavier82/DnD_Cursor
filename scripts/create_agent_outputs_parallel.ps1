# Create Agent Outputs in Parallel
# Helper script that reads agent output JSON files and writes them in parallel

param(
    [Parameter(Mandatory=$true)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [string]$TempDir = ""
)

$ErrorActionPreference = "Stop"
$CoordDir = "C:\DnD\.coord-$SessionId"

# Ensure coordination directory exists
if (-not (Test-Path $CoordDir)) {
    New-Item -ItemType Directory -Force -Path $CoordDir | Out-Null
}

# Use coordination directory's temp subfolder if TempDir not specified
if ([string]::IsNullOrEmpty($TempDir)) {
    $TempDir = Join-Path $CoordDir "temp"
    if (-not (Test-Path $TempDir)) {
        New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
    }
}

# Look for temporary agent output files
$tempFiles = @{
    REFEREE = Join-Path $TempDir "agent_referee_$SessionId.json"
    NARRATOR = Join-Path $TempDir "agent_narrator_$SessionId.json"
    STATE_PATCHER = Join-Path $TempDir "agent_statepatcher_$SessionId.json"
    QA_COMPLIANCE = Join-Path $TempDir "agent_qacompliance_$SessionId.json"
}

# Read and convert JSON files to objects
$agentOutputs = @{}
foreach ($agent in @("REFEREE", "NARRATOR", "STATE_PATCHER", "QA_COMPLIANCE")) {
    $tempFile = $tempFiles[$agent]
    if (Test-Path $tempFile) {
        try {
            $content = Get-Content -Path $tempFile -Raw -Encoding UTF8
            $agentOutputs[$agent] = $content | ConvertFrom-Json
        } catch {
            Write-Error "Failed to read $agent output from $tempFile : $_"
            exit 1
        }
    } else {
        Write-Error "Missing temporary file for $agent : $tempFile"
        exit 1
    }
}

# Call the parallel execution script
$scriptPath = Join-Path $PSScriptRoot "run_agents_parallel.ps1"
& $scriptPath -SessionId $SessionId -AgentOutputs $agentOutputs

# Clean up temporary files
foreach ($tempFile in $tempFiles.Values) {
    if (Test-Path $tempFile) {
        Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue
    }
}

