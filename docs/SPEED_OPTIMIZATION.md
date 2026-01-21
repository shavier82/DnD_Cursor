# Speed Optimization Guide

## Overview

This guide documents the speed optimizations implemented to reduce response times from ~60 seconds to <10 seconds.

## Key Optimizations

### 1. Background TTS (CRITICAL - Saves 10-30+ seconds)

**Problem:** TTS playback blocks for 10-30+ seconds waiting for audio to finish.

**Solution:** Use `-Background` flag to run TTS in a background job.

**Usage:**
```powershell
.\scripts\speak_narration.ps1 -SessionId <id> -Background
```

**Time Saved:** 10-30+ seconds per narration response

### 2. Fast Mode for Validation

**Problem:** Validation runs extensive checks on every turn.

**Solution:** Use `-FastMode` flag to skip non-critical location checks.

**Usage:**
```powershell
.\scripts\validate_agent_outputs.ps1 -SessionId <id> -FastMode
```

**Time Saved:** 1-3 seconds per turn

### 3. Fast Mode for Merge

**Problem:** Auto-tracking and narrative combination block merge completion.

**Solution:** Use `-FastMode` flag to run these in background jobs.

**Usage:**
```powershell
.\scripts\merge_outputs.ps1 -SessionId <id> -FastMode
```

**Time Saved:** 2-5 seconds per turn

### 4. Batch File Reads

**Problem:** Reading files sequentially when they could be read in parallel.

**Solution:** The AI assistant batches file reads using parallel tool calls.

**Time Saved:** 2-5 seconds per turn

### 5. Parallel Agent Execution

**Problem:** Agent outputs written sequentially.

**Solution:** Already implemented - all 4 agents write in parallel using PowerShell jobs.

**Time Saved:** Already optimized

## Recommended Workflow

### For Maximum Speed (Fast Mode)

1. **Always use background TTS:**
   ```powershell
   .\scripts\speak_narration.ps1 -SessionId <id> -Background
   ```

2. **Use fast mode for validation:**
   ```powershell
   .\scripts\validate_agent_outputs.ps1 -SessionId <id> -FastMode -Quiet
   ```

3. **Use fast mode for merge:**
   ```powershell
   .\scripts\merge_outputs.ps1 -SessionId <id> -FastMode
   ```

### For Standard Mode (Full Validation)

Use without `-FastMode` flags for complete validation and tracking.

## Expected Performance

- **Before optimizations:** ~60 seconds per response
- **With optimizations:** <10 seconds per response
- **Improvement:** ~83% faster

## Implementation Notes

### TTS Background Mode
- Uses PowerShell `Start-Job` to run TTS in background
- Returns immediately without blocking
- Audio plays asynchronously
- Multiple TTS instances can run simultaneously

### Fast Mode Validation
- Skips location fence checks (path resolution)
- Still validates JSON structure and required fields
- Still checks agent_role matches
- Safe to use in production

### Fast Mode Merge
- Auto-tracking runs in background job
- Combat narrative combination runs in background job
- State saving still happens (required)
- Non-blocking operations

## Combat-Specific Optimizations

Combat turns benefit from all optimizations:
- Background TTS for turn narratives (only at encounter end)
- Fast mode validation
- Fast mode merge
- Batch file reads for character data

## Additional Tips

1. **Cache frequently accessed data** - Keep state and campaign events in memory during session
2. **Reduce Google Sheets queries** - Only query when values change, not every turn
3. **Batch state updates** - Apply all patches in one operation
4. **Skip non-critical validations** - Use fast mode during active play

## Troubleshooting

**TTS not playing in background:**
- Check that `-Background` flag is used
- Verify PowerShell jobs are enabled
- Check job status: `Get-Job`

**Fast mode too permissive:**
- Remove `-FastMode` flags for full validation
- Use fast mode only during active play
- Use standard mode for setup/validation
































