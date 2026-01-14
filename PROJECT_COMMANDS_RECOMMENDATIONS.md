# Project Commands Recommendations

## Current Commands ✅
- `dnd_session_init` - Manual Session Initialization (HARDENED)
- `dnd_turn_merge` - Merge Agent Outputs
- `dnd_turn_parallel` - Parallel Agents Dispatch (HARDENED v2)

---

## Recommended Additional Commands

### 1. Quick State Check
**Command:** `dnd_state_check`
**Script:** 
```powershell
# Quick state verification
$campaign = "Phandelver"
Write-Host "`n=== CURRENT STATE ===" -ForegroundColor Cyan
Get-Content "C:\DnD\Campaigns\$campaign\saves\CURRENT_STATE.json" | Select-Object -First 30
Write-Host "`n=== RECENT EVENTS ===" -ForegroundColor Cyan
Get-Content "C:\DnD\Campaigns\$campaign\saves\CAMPAIGN_EVENTS.json" | Select-Object -Last 20
```
**Usage:** Quick overview of campaign state before DMing

---

### 2. Lookup Monster (MCP Wrapper)
**Command:** `dnd_monster`
**Purpose:** Quick monster lookup from command palette
**Script:**
```powershell
param([Parameter(Mandatory=$true)][string]$MonsterName)
Write-Host "Looking up: $MonsterName" -ForegroundColor Yellow
# This would trigger MCP lookup_monster
# For now, just a reminder to use MCP in chat
Write-Host "Use in chat: lookup_monster('$MonsterName')" -ForegroundColor Green
```
**Usage:** `dnd_monster Goblin` → Reminds to use MCP

---

### 3. Lookup Spell
**Command:** `dnd_spell`
**Purpose:** Quick spell lookup
**Script:**
```powershell
param([Parameter(Mandatory=$true)][string]$SpellName)
Write-Host "Looking up: $SpellName" -ForegroundColor Yellow
Write-Host "Use in chat: lookup_spell('$SpellName')" -ForegroundColor Green
```
**Usage:** `dnd_spell Fireball` → Reminds to use MCP

---

### 4. Read Chapter Pack
**Command:** `dnd_chapter`
**Script:**
```powershell
param([Parameter(Mandatory=$true)][int]$ChapterNum)
$packPath = "C:\DnD\DnD_Cursor\packs\chapter_pack_$ChapterNum.json"
if (Test-Path $packPath) {
    Get-Content $packPath | ConvertFrom-Json | ConvertTo-Json -Depth 10
} else {
    Write-Host "Chapter pack $ChapterNum not found" -ForegroundColor Red
}
```
**Usage:** `dnd_chapter 3` → Loads chapter 3 content

---

### 5. Roll Dice (MCP Wrapper)
**Command:** `dnd_roll`
**Purpose:** Quick dice roll
**Script:**
```powershell
param([Parameter(Mandatory=$true)][string]$DiceExpression)
Write-Host "Rolling: $DiceExpression" -ForegroundColor Yellow
Write-Host "Use in chat: roll_dice('$DiceExpression', 'Quick roll')" -ForegroundColor Green
```
**Usage:** `dnd_roll 2d6+3` → Reminds to use MCP dice roller

---

### 6. Combat Start
**Command:** `dnd_combat_start`
**Purpose:** Initialize combat tracking
**Script:**
```powershell
param(
    [Parameter(Mandatory=$true)][string]$Encounter,
    [Parameter(Mandatory=$true)][string]$Campaign
)
Write-Host "`n=== COMBAT STARTING ===" -ForegroundColor Red
Write-Host "Encounter: $Encounter" -ForegroundColor Yellow
Write-Host "Campaign: $Campaign" -ForegroundColor Yellow
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Roll initiative for all combatants" -ForegroundColor White
Write-Host "2. Use dnd_turn_parallel for each turn" -ForegroundColor White
Write-Host "3. Use dnd_turn_merge to apply changes" -ForegroundColor White
```
**Usage:** `dnd_combat_start "Goblin Ambush" "Phandelver"`

---

### 7. Sheet Sync
**Command:** `dnd_sheet_sync`
**Purpose:** Sync character data from Google Sheets
**Script:**
```powershell
param([Parameter(Mandatory=$true)][string]$Campaign)
Write-Host "Syncing sheets for: $Campaign" -ForegroundColor Cyan
python "C:\DnD\DnD_Cursor\scripts\read_sheets.py" --campaign $Campaign
```
**Usage:** `dnd_sheet_sync Phandelver` → Pulls latest character data

---

### 8. Validate State
**Command:** `dnd_validate`
**Purpose:** Check state file integrity
**Script:**
```powershell
param([Parameter(Mandatory=$true)][string]$Campaign)
$statePath = "C:\DnD\Campaigns\$Campaign\saves\CURRENT_STATE.json"
try {
    Get-Content $statePath | ConvertFrom-Json | Out-Null
    Write-Host "✅ CURRENT_STATE.json is valid" -ForegroundColor Green
} catch {
    Write-Host "❌ CURRENT_STATE.json has errors: $_" -ForegroundColor Red
}
```
**Usage:** `dnd_validate Phandelver` → Checks JSON validity

---

### 9. Quick Save Backup
**Command:** `dnd_backup`
**Purpose:** Backup current campaign state
**Script:**
```powershell
param([Parameter(Mandatory=$true)][string]$Campaign)
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$savesDir = "C:\DnD\Campaigns\$Campaign\saves"
$backupDir = "C:\DnD\Campaigns\$Campaign\backups"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Copy-Item "$savesDir\CURRENT_STATE.json" "$backupDir\CURRENT_STATE_$timestamp.json"
Copy-Item "$savesDir\CAMPAIGN_EVENTS.json" "$backupDir\CAMPAIGN_EVENTS_$timestamp.json"
Write-Host "✅ Backup created: $timestamp" -ForegroundColor Green
```
**Usage:** `dnd_backup Phandelver` → Creates timestamped backup

---

### 10. MCP Test
**Command:** `dnd_mcp_test`
**Purpose:** Verify all MCP servers are working
**Script:**
```powershell
Write-Host "`n=== MCP SERVER TEST ===" -ForegroundColor Cyan
Write-Host "Testing dice-roller..." -ForegroundColor Yellow
Write-Host "Testing rules-database..." -ForegroundColor Yellow
Write-Host "Testing sourcebooks..." -ForegroundColor Yellow
Write-Host "`nRun these in chat to test:" -ForegroundColor White
Write-Host "1. roll_dice('2d6+3', 'Test roll')" -ForegroundColor Gray
Write-Host "2. lookup_monster('Goblin')" -ForegroundColor Gray
Write-Host "3. lookup_spell('Fireball')" -ForegroundColor Gray
Write-Host "4. lookup_condition('Grappled')" -ForegroundColor Gray
Write-Host "5. lookup_rule('Advantage')" -ForegroundColor Gray
Write-Host "6. search_sourcebooks('grappling', 'phb')" -ForegroundColor Gray
```
**Usage:** `dnd_mcp_test` → Shows test commands

---

## How to Add These Commands

### Option 1: Via Cursor UI
1. Go to Settings → Features → Project Commands
2. Click **"+ Add Command"**
3. Fill in:
   - **Name:** `dnd_state_check`
   - **Command:** `<paste script here>`
4. Save

### Option 2: Via Workspace Settings
Edit `.vscode/settings.json`:
```json
{
  "cursor.commands": [
    {
      "name": "dnd_state_check",
      "command": "powershell -Command \"$campaign = 'Phandelver'; Write-Host '=== STATE ===' -ForegroundColor Cyan; Get-Content 'C:\\DnD\\Campaigns\\$campaign\\saves\\CURRENT_STATE.json' | Select-Object -First 30\""
    }
  ]
}
```

---

## Priority Commands to Add First

1. ✅ **`dnd_state_check`** - Most useful for quick state overview
2. ✅ **`dnd_backup`** - Critical for safety
3. ✅ **`dnd_validate`** - Prevents state corruption
4. ✅ **`dnd_mcp_test`** - Verify tools are working
5. ✅ **`dnd_chapter`** - Quick chapter content access

---

## Benefits of More Commands

- **Speed:** One-click access to common operations
- **Safety:** Automated backups and validation
- **Consistency:** Standardized workflows
- **Visibility:** Quick state checks without digging through files
- **Integration:** MCP wrapper commands for frequently-used lookups










