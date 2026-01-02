# Setup Verification Checklist

Run these commands in PowerShell to verify the setup:

## 1. Verify campaign_path.txt

```powershell
Test-Path "C:\DnD\DnD_Cursor\campaign_path.txt"
Get-Content "C:\DnD\DnD_Cursor\campaign_path.txt"
# Should output: C:\DnD\Campaigns\Phandelver
```

## 2. List Chapter Placeholder Files

```powershell
Get-ChildItem "C:\DnD\Campaigns\Phandelver\chapters\*.txt" | Select-Object Name
# Should list: chapter_1.txt, chapter_2.txt, Chapter_3.txt, chapter_4.txt, Chapter_5.txt, Chapter_6.txt, Chapter_7.txt, Chapter_8.txt
```

## 3. List Pack JSON Files

```powershell
Get-ChildItem "C:\DnD\DnD_Cursor\packs\*.json" | Select-Object Name
# Should list all 10 pack files: session_preload.json, chapter_pack_1-8.json, encounter_pack.json
```

## 4. Run Pack Validation Script

```powershell
cd C:\DnD\DnD_Cursor
.\scripts\validate_packs.ps1
# Should output: ✓ All pack files are valid!
# Exit code should be 0
```

## 5. Verify Campaign Folder is NOT a Git Repo

```powershell
Test-Path "C:\DnD\Campaigns\Phandelver\.git"
# Should return: False
```

## 6. Verify Parallel Agent Files Exist

```powershell
@(
    "C:\DnD\DnD_Cursor\.cursor\commands\dnd_turn_parallel.md",
    "C:\DnD\DnD_Cursor\.cursor\commands\dnd_turn_merge.md",
    "C:\DnD\DnD_Cursor\.cursor\worktrees.json"
) | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "✓ $_" -ForegroundColor Green
    } else {
        Write-Host "✗ $_ MISSING" -ForegroundColor Red
    }
}
```

## 7. Full Verification Script

Run this single command to verify everything:

```powershell
Write-Host "`n=== D&D Campaign Setup Verification ===" -ForegroundColor Cyan
Write-Host ""

# 1. campaign_path.txt
Write-Host "1. Checking campaign_path.txt..." -ForegroundColor Yellow
if (Test-Path "C:\DnD\DnD_Cursor\campaign_path.txt") {
    $content = Get-Content "C:\DnD\DnD_Cursor\campaign_path.txt"
    Write-Host "  ✓ Exists: $content" -ForegroundColor Green
} else {
    Write-Host "  ✗ MISSING" -ForegroundColor Red
}

# 2. Chapter files
Write-Host "`n2. Checking chapter placeholders..." -ForegroundColor Yellow
$chapters = Get-ChildItem "C:\DnD\Campaigns\Phandelver\chapters\*.txt" -ErrorAction SilentlyContinue
if ($chapters) {
    Write-Host "  ✓ Found $($chapters.Count) chapter files" -ForegroundColor Green
    $chapters | ForEach-Object { Write-Host "    - $($_.Name)" -ForegroundColor Cyan }
} else {
    Write-Host "  ✗ No chapter files found" -ForegroundColor Red
}

# 3. Pack files
Write-Host "`n3. Checking pack JSON files..." -ForegroundColor Yellow
$packs = Get-ChildItem "C:\DnD\DnD_Cursor\packs\*.json" -ErrorAction SilentlyContinue
if ($packs) {
    Write-Host "  ✓ Found $($packs.Count) pack files" -ForegroundColor Green
} else {
    Write-Host "  ✗ No pack files found" -ForegroundColor Red
}

# 4. Run validation
Write-Host "`n4. Running pack validation..." -ForegroundColor Yellow
cd C:\DnD\DnD_Cursor
& ".\scripts\validate_packs.ps1"
$validationExit = $LASTEXITCODE

# 5. Campaign safety
Write-Host "`n5. Checking campaign folder safety..." -ForegroundColor Yellow
if (Test-Path "C:\DnD\Campaigns\Phandelver\.git") {
    Write-Host "  ✗ CRITICAL: Campaign is a Git repo!" -ForegroundColor Red
} else {
    Write-Host "  ✓ Campaign folder is safe (not a Git repo)" -ForegroundColor Green
}

# 6. Parallel agent files
Write-Host "`n6. Checking parallel agent files..." -ForegroundColor Yellow
@(
    ".cursor\commands\dnd_turn_parallel.md",
    ".cursor\commands\dnd_turn_merge.md",
    ".cursor\worktrees.json"
) | ForEach-Object {
    $path = Join-Path "C:\DnD\DnD_Cursor" $_
    if (Test-Path $path) {
        Write-Host "  ✓ $_" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $_ MISSING" -ForegroundColor Red
    }
}

Write-Host "`n=== Verification Complete ===" -ForegroundColor Cyan
if ($validationExit -eq 0) {
    Write-Host "All checks passed!" -ForegroundColor Green
} else {
    Write-Host "Some checks failed. Review output above." -ForegroundColor Yellow
}
```




