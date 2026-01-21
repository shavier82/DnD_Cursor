# Parallel Agent Execution Workflow

## Overview

The parallel agent execution system uses PowerShell `Start-Job` to write all 4 agent output files simultaneously, ensuring true parallel execution.

## Workflow

### Step 1: Generate Agent Outputs
The AI assistant generates all 4 agent output objects in memory:
- REFEREE output
- NARRATOR output  
- STATE_PATCHER output
- QA_COMPLIANCE output

### Step 2: Write Temporary Files
The AI writes all 4 outputs to temporary JSON files (can be done in parallel):
- `%TEMP%\agent_referee_<session-id>.json`
- `%TEMP%\agent_narrator_<session-id>.json`
- `%TEMP%\agent_statepatcher_<session-id>.json`
- `%TEMP%\agent_qacompliance_<session-id>.json`

### Step 3: Execute Parallel Write Script
Call `write_agent_outputs_parallel.ps1` which:
1. Reads the 4 temporary JSON files
2. Spawns 4 PowerShell jobs using `Start-Job`
3. Each job writes its output file to the coordination directory **in parallel**
4. Waits for all jobs to complete
5. Verifies all files were created
6. Cleans up temporary files

## Scripts

### `write_agent_outputs_parallel.ps1`
Main entry point. Accepts JSON strings and writes temp files, then calls the parallel execution script.

### `create_agent_outputs_parallel.ps1`
Reads temp files and prepares agent outputs hashtable.

### `run_agents_parallel.ps1`
Core parallel execution script. Uses `Start-Job` to write all 4 output files simultaneously.

## Usage Example

```powershell
# From AI assistant workflow:
# 1. Generate agent outputs as JSON strings
$refereeJson = '{"agent_role":"REFEREE",...}'
$narratorJson = '{"agent_role":"NARRATOR",...}'
$stateJson = '{"agent_role":"STATE_PATCHER",...}'
$qaJson = '{"agent_role":"QA_COMPLIANCE",...}'

# 2. Write temp files (can be parallel)
$refereeJson | Out-File "$env:TEMP\agent_referee_$sessionId.json"
$narratorJson | Out-File "$env:TEMP\agent_narrator_$sessionId.json"
$stateJson | Out-File "$env:TEMP\agent_statepatcher_$sessionId.json"
$qaJson | Out-File "$env:TEMP\agent_qacompliance_$sessionId.json"

# 3. Execute parallel write
& "C:\DnD\DnD_Cursor\scripts\create_agent_outputs_parallel.ps1" -SessionId $sessionId
```

## Benefits

- **True Parallelism**: All 4 files are written simultaneously using PowerShell jobs
- **Faster Execution**: No sequential waiting between file writes
- **Verified Completion**: Script verifies all files were created successfully
- **Clean Cleanup**: Temporary files are automatically removed

## Integration with AI Workflow

The AI assistant will:
1. Generate all 4 agent outputs
2. Write them to temp files (using parallel write tool calls)
3. Execute the PowerShell script to write final outputs in parallel
4. Continue with merge/validation steps
































