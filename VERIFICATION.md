# Verification Checklist

Quick smoke tests to verify the system is working correctly.

## Build Scripts

### Build Chapter 1

```powershell
cd C:\DnD\DnD_Cursor
python scripts\build_chapter_pack.py --chapter 1
```

**Verify:**
- `chapter_pack_1.json` exists in `C:\DnD\Campaigns\Phandelver\packs\`
- File is valid JSON (no parse errors)
- Contains `pack_type: "chapter_pack"` and `chapter: 1`

### Build Session Preload

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\build_session_preload.ps1
```

**Verify:**
- `session_preload.json` exists in packs directory
- Valid JSON structure

### Build Encounter Pack

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\build_encounter_pack.ps1
```

**Verify:**
- `encounter_pack.json` exists in packs directory
- Valid JSON structure

## Parallel Agents

### Full Turn Test

1. Run `/dnd_turn_parallel demo-001` in Cursor Chat
2. Run `/dnd_turn_merge demo-001` in Cursor Chat

**Verify:**
- All 4 agent outputs created
- Validation passes
- Merge produces 3-block output (NARRATION, ASK, ACTIONS)
- If roll requested → STATE_PATCHER.patches is `[]`
- Suggested actions displayed when entering locations (if NARRATOR provides them)
- PATCH is applied to state but not displayed in output
