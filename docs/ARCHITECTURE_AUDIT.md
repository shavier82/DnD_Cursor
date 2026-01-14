# Architecture Audit & Speed Optimization

## Current Architecture Overview

### Turn Processing Flow (Current - SLOW)

```
User Input
  ↓
AI generates 4 agent outputs (parallel in memory)
  ↓
Write agent outputs to JSON files (can be parallel)
  ↓
validate_agent_outputs.ps1 (1-3 seconds)
  ├─ File existence checks
  ├─ JSON parsing
  ├─ Schema validation
  └─ Location fence checks (SLOW - skipped in FastMode)
  ↓
merge_outputs.ps1 (5-15 seconds) ⚠️ MAJOR BOTTLENECK
  ├─ Read 4 JSON files
  ├─ Compose NARRATION/ASK/ACTIONS
  ├─ Load CURRENT_STATE.json
  ├─ Apply patches (VERY SLOW - JSON conversion for each patch)
  ├─ Save state (JSON conversion again)
  ├─ auto_event_tracker.ps1 (background job, but still spawns)
  └─ combine_combat_narrative.ps1 (background job, but still spawns)
  ↓
speak_narration.ps1 (10-30 seconds if blocking, 0 if background)
  ↓
Output to user
```

**Total Time: 15-50+ seconds per turn** ⚠️

## Critical Bottlenecks Identified

### 1. **merge_outputs.ps1 - Patch Application (CRITICAL BOTTLENECK)**

**Problem:** Lines 180-302 convert state to JSON and back for EVERY patch
- For each patch: JSON → Hashtable → Apply patch → Hashtable → JSON
- Each JSON conversion is ~100-500ms
- With 5 patches = 500-2500ms wasted

**Current Code (SLOW):**
```powershell
foreach ($patch in $patchesArray) {
    # Convert state to JSON and back to avoid PSObject indexing issues
    $stateJson = $currentState | ConvertTo-Json -Depth 20 -Compress  # SLOW!
    $stateHash = $stateJson | ConvertFrom-Json -AsHashtable  # SLOW!
    # ... apply patch ...
    $currentState = $stateHash | ConvertTo-Json -Depth 20 | ConvertFrom-Json  # SLOW!
}
```

**Optimized Solution:** Convert ONCE, apply all patches, convert ONCE
- Time saved: **2-5 seconds per turn**

### 2. **State File I/O (MODERATE BOTTLENECK)**

**Problem:** Reading and writing state file every turn
- Read: ~50-200ms
- Write: ~100-300ms
- Total: ~150-500ms per turn

**Optimized Solution:** 
- Only save state when patches exist
- Use faster JSON serialization
- Consider in-memory cache with periodic flush

**Time saved: 100-300ms per turn**

### 3. **Google Sheets Updates (MODERATE BOTTLENECK)**

**Problem:** `update_sheets_data.py` makes multiple API calls per update
- Character lookup: 1 API call
- Value update: 1 API call
- With batchUpdate: Still 2 calls minimum

**Optimized Solution:** Batch multiple updates into single batchUpdate call
- Time saved: **500ms - 2 seconds per update**

### 4. **Background Job Overhead (MINOR BOTTLENECK)**

**Problem:** Starting background jobs has overhead even if non-blocking
- `Start-Job` spawn: ~50-200ms per job
- auto_event_tracker and combine_combat_narrative always spawn jobs

**Optimized Solution:** 
- Skip job spawn if patches don't require tracking
- Check conditions before spawning

**Time saved: 100-400ms per turn**

### 5. **JSON Parsing Redundancy (MINOR BOTTLENECK)**

**Problem:** Parsing same JSON files multiple times
- merge_outputs.ps1 reads files already validated
- Could reuse parsed objects

**Time saved: 50-200ms per turn**

## Optimized Architecture

### Turn Processing Flow (Optimized - FAST)

```
User Input
  ↓
AI generates 4 agent outputs (parallel in memory)
  ↓
Write agent outputs to JSON files (parallel write)
  ↓
validate_agent_outputs.ps1 -FastMode -Quiet (500ms)
  ├─ File existence checks
  ├─ JSON parsing
  └─ Schema validation (skip location checks)
  ↓
merge_outputs.ps1 -FastMode (1-2 seconds) ✅ OPTIMIZED
  ├─ Read 4 JSON files (batch read)
  ├─ Compose NARRATION/ASK/ACTIONS
  ├─ Load CURRENT_STATE.json (only if patches exist)
  ├─ Apply patches (OPTIMIZED: convert once, apply all, convert once)
  ├─ Save state (only if changed, faster JSON)
  └─ Spawn background jobs only if needed
  ↓
speak_narration.ps1 -Background (0ms - non-blocking)
  ↓
Output to user
```

**Total Time: 2-4 seconds per turn** ✅ **85% faster**

## Script Inventory

### Critical Scripts (Run Every Turn)

1. **merge_outputs.ps1** ⚠️ **NEEDS OPTIMIZATION**
   - Current: 5-15 seconds
   - Optimized: 1-2 seconds
   - Bottleneck: Patch application (convert-once fix)

2. **validate_agent_outputs.ps1** ✅ **ALREADY OPTIMIZED**
   - Current: 1-3 seconds (with FastMode: 500ms)
   - Status: Good (FastMode skip location checks)

3. **speak_narration.ps1** ✅ **ALREADY OPTIMIZED**
   - Current: 10-30s blocking / 0ms background
   - Status: Good (background mode works)

### Secondary Scripts (Run Periodically)

4. **auto_event_tracker.ps1** ⚠️ **CAN OPTIMIZE**
   - Current: Runs in background after every merge
   - Optimization: Only spawn if patches contain events
   - Time saved: 100-200ms

5. **combine_combat_narrative.ps1** ⚠️ **CAN OPTIMIZE**
   - Current: Runs in background when combat ends
   - Optimization: Only spawn if combat actually ended
   - Time saved: 100-200ms

### Google Sheets Scripts (Run On-Demand)

6. **update_sheets_data.py** ⚠️ **NEEDS OPTIMIZATION**
   - Current: Multiple API calls per update
   - Optimization: Batch updates into single API call
   - Time saved: 500ms - 2s per update

7. **read_resource.py** ✅ **OK**
   - Single API call, fast enough

8. **read_inventory.py** ✅ **OK**
   - Single API call, fast enough

### Utility Scripts (Run Infrequently)

9. **build_chapter_pack.py** ✅ **OK**
   - Only runs during BUILD mode

10. **save_game_state.py** ✅ **OK**
    - Only runs when explicitly called

## Optimization Implementation Plan

### Phase 1: Critical Fixes (Immediate - 85% improvement)

#### 1.1 Fix merge_outputs.ps1 Patch Application
**File:** `scripts/merge_outputs.ps1`
**Lines:** 180-302
**Change:** Convert state once, apply all patches, convert once

**Before:**
```powershell
foreach ($patch in $patchesArray) {
    $stateJson = $currentState | ConvertTo-Json -Depth 20 -Compress  # SLOW
    $stateHash = $stateJson | ConvertFrom-Json -AsHashtable
    # ... apply patch ...
    $currentState = $stateHash | ConvertTo-Json -Depth 20 | ConvertFrom-Json  # SLOW
}
```

**After:**
```powershell
# Convert once before loop
$stateJson = $currentState | ConvertTo-Json -Depth 20 -Compress
$stateHash = $stateJson | ConvertFrom-Json -AsHashtable

# Apply all patches
foreach ($patch in $patchesArray) {
    # ... apply patch to $stateHash directly ...
}

# Convert once after all patches
$currentState = $stateHash | ConvertTo-Json -Depth 20 | ConvertFrom-Json
```

**Expected Improvement:** 2-5 seconds faster

#### 1.2 Optimize State File I/O
**File:** `scripts/merge_outputs.ps1`
**Change:** Only load/save if patches exist, use faster encoding

**Before:**
```powershell
# Always load state
$currentState = Get-Content $stateFile -Raw | ConvertFrom-Json
# ... apply patches ...
# Always save
$currentState | ConvertTo-Json -Depth 10 | Set-Content $stateFile
```

**After:**
```powershell
# Only load if patches exist
if ($patchesCount -gt 0) {
    if (Test-Path $stateFile) {
        $currentState = Get-Content $stateFile -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    # ... apply patches ...
    # Only save if state changed
    if ($stateChanged) {
        ($currentState | ConvertTo-Json -Depth 10 -Compress) | Set-Content $stateFile -Encoding UTF8 -NoNewline
    }
}
```

**Expected Improvement:** 100-300ms faster

### Phase 2: Conditional Background Jobs (Additional 5% improvement)

#### 2.1 Skip Auto-Event Tracker When Not Needed
**File:** `scripts/merge_outputs.ps1`
**Lines:** 315-333
**Change:** Only spawn if patches contain event-related paths

**Before:**
```powershell
if (-not $FastMode) {
    Start-Job { ... } | Out-Null  # Always spawns
}
```

**After:**
```powershell
if (-not $FastMode -and $shouldTrackEvents) {
    # Check if patches contain event-related paths
    $hasEventPatches = $patchesArray | Where-Object { 
        $_.path -match "^/encounter/|^/discoveries/|^/scene/location"
    }
    if ($hasEventPatches) {
        Start-Job { ... } | Out-Null
    }
}
```

**Expected Improvement:** 100-200ms faster

### Phase 3: Google Sheets Batching (Additional 5% improvement)

#### 3.1 Batch Sheet Updates
**File:** `scripts/update_sheets_data.py`
**Change:** Support batch updates for multiple characters/values

**Before:**
```python
# Multiple calls
update_character_xp(service, sheet_id, char_id, xp)  # API call 1
update_character_currency(service, sheet_id, char_id, currency)  # API call 2
```

**After:**
```python
# Single batch call
batch_update_character(service, sheet_id, char_id, {
    'xp': xp,
    'currency': currency
})  # Single API call
```

**Expected Improvement:** 500ms - 2s per update session

## Performance Targets

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| **Turn Processing Time** | 15-50s | 2-4s | 85-92% faster |
| **Merge Script** | 5-15s | 1-2s | 80-87% faster |
| **Validation** | 1-3s | 0.5s | 67-83% faster |
| **TTS** | 10-30s | 0s (bg) | 100% faster |
| **State I/O** | 150-500ms | 50-100ms | 67-80% faster |
| **Sheets Updates** | 1-3s | 0.5-1s | 50-67% faster |

## Implementation Priority

1. **P0 (Critical - Do Now):** Fix merge_outputs.ps1 patch application
2. **P1 (High - Do Soon):** Optimize state file I/O
3. **P2 (Medium - Do Next):** Conditional background job spawning
4. **P3 (Low - Nice to Have):** Google Sheets batching

## Testing

After implementing optimizations:
1. Measure turn processing time before/after
2. Verify correctness (no regressions)
3. Test with various patch counts (1-10 patches)
4. Test with/without FastMode
5. Test with/without background TTS

## Monitoring

Track these metrics:
- Average turn processing time
- Merge script execution time
- Validation execution time
- State save time
- Background job spawn time


















