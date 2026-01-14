# Test Parallel Execution
$sessionId = "20260105223000"

# Create test agent outputs
$referee = @{
    agent_role = "REFEREE"
    blocked = $false
    roll_request = @{
        required = $false
        skill_or_check = $null
        dc = $null
        formula = $null
        reason = $null
    }
    mechanics_notes = @("Test parallel execution")
} | ConvertTo-Json -Depth 10 -Compress

$narrator = @{
    agent_role = "NARRATOR"
    blocked = $false
    narration = "Test parallel execution"
} | ConvertTo-Json -Depth 10 -Compress

$state = @{
    agent_role = "STATE_PATCHER"
    blocked = $false
    patches = @()
} | ConvertTo-Json -Depth 10 -Compress

$qa = @{
    agent_role = "QA_COMPLIANCE"
    blocked = $false
    status = "ok"
    issues = @()
} | ConvertTo-Json -Depth 10 -Compress

# Write temp files
$referee | Out-File "$env:TEMP\agent_referee_$sessionId.json" -Encoding UTF8 -NoNewline
$narrator | Out-File "$env:TEMP\agent_narrator_$sessionId.json" -Encoding UTF8 -NoNewline
$state | Out-File "$env:TEMP\agent_statepatcher_$sessionId.json" -Encoding UTF8 -NoNewline
$qa | Out-File "$env:TEMP\agent_qacompliance_$sessionId.json" -Encoding UTF8 -NoNewline

# Execute parallel write
& "$PSScriptRoot\create_agent_outputs_parallel.ps1" -SessionId $sessionId


















