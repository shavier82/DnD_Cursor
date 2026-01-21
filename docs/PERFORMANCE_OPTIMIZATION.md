# Performance Optimization Guide

## Response Time Optimization

This guide outlines optimizations to reduce response time from ~60 seconds to <10 seconds.

## Current Bottlenecks

1. **TTS Audio Playback (MAJOR - 10-30+ seconds)** - Audio plays and blocks until finished
2. **Sequential File Reads** - Reading multiple files one at a time
3. **Google Sheets API Calls** - Network latency for inventory checks
4. **PowerShell Script Execution** - Overhead from spawning processes
5. **Multiple Tool Calls** - Making many sequential tool calls instead of batching

## Optimizations Implemented

### 1. Non-Blocking TTS (CRITICAL)

**Problem:** TTS playback blocks for 10-30+ seconds waiting for audio to finish.

**Solution:** Run TTS in background mode so it doesn't block response.

**Usage:**
```powershell
# Non-blocking (returns immediately, plays audio in background)
python C:\DnD\DnD_Cursor\scripts\speak_narration_elevenlabs.py <session-id> --background
```

**Time Saved:** 10-30+ seconds per narration response

### 2. Batch File Reads

**Problem:** Reading files sequentially when they could be read in parallel.

**Solution:** Batch read operations using parallel tool calls.

**Before:**
- Read file 1 → wait → Read file 2 → wait → Read file 3

**After:**
- Read files 1, 2, 3 simultaneously in one batch

**Time Saved:** 2-5 seconds per turn

### 3. Reduce Unnecessary State Updates

**Problem:** Updating state multiple times in sequence when it could be done once.

**Solution:** Batch all state patches into a single update.

**Time Saved:** 1-2 seconds per turn

### 4. Skip Non-Critical Validations

**Problem:** Running validations that don't block execution.

**Solution:** Only validate when explicitly needed, defer non-critical checks.

**Time Saved:** 1-3 seconds per turn

## Recommended Workflow

1. **Use `--background` flag for TTS** - Always use background mode unless you specifically want to wait for audio
2. **Batch file reads** - Read all needed files in parallel
3. **Batch state updates** - Apply all patches in one operation
4. **Cache frequently accessed data** - Keep state and campaign events in memory during session

## Expected Performance

- **Before:** ~60 seconds per response
- **After:** <10 seconds per response
- **Improvement:** ~83% faster

## Additional Optimizations (Future)

1. **Async Google Sheets queries** - Query sheets in background, cache results
2. **Pre-load common data** - Load campaign events and state at session start, keep in memory
3. **Lazy validation** - Only validate when needed, not on every turn
4. **Parallel agent processing** - Already implemented, but can optimize further
































