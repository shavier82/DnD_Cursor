#!/usr/bin/env pwsh
# Verify Campaign Paths
# Quick script to verify all critical paths exist

Write-Host "=== Campaign Path Verification ===" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$warnings = @()

# Check root directory
Write-Host "Checking root directory..." -ForegroundColor Yellow
if (Test-Path "C:\DnD") {
    Write-Host "  [OK] C:\DnD exists" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] C:\DnD does not exist!" -ForegroundColor Red
    $errors += "C:\DnD"
}

# Check campaigns directory (NOTE: plural "Campaigns")
Write-Host "Checking campaigns directory..." -ForegroundColor Yellow
if (Test-Path "C:\DnD\Campaigns") {
    Write-Host "  [OK] C:\DnD\Campaigns exists" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] C:\DnD\Campaigns does not exist!" -ForegroundColor Red
    Write-Host "  [NOTE] Check spelling: 'Campaigns' (plural), not 'Campaign' (singular)" -ForegroundColor Yellow
    $errors += "C:\DnD\Campaigns"
}

# Check Phandelver campaign
Write-Host "Checking Phandelver campaign..." -ForegroundColor Yellow
if (Test-Path "C:\DnD\Campaigns\Phandelver") {
    Write-Host "  [OK] C:\DnD\Campaigns\Phandelver exists" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] C:\DnD\Campaigns\Phandelver does not exist!" -ForegroundColor Red
    $errors += "C:\DnD\Campaigns\Phandelver"
}

# Check critical subdirectories
Write-Host "Checking subdirectories..." -ForegroundColor Yellow
$subdirs = @(
    "C:\DnD\Campaigns\Phandelver\characters",
    "C:\DnD\Campaigns\Phandelver\packs",
    "C:\DnD\Campaigns\Phandelver\saves",
    "C:\DnD\Campaigns\Phandelver\chapters"
)

foreach ($dir in $subdirs) {
    if (Test-Path $dir) {
        Write-Host "  [OK] $dir exists" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] $dir does not exist" -ForegroundColor Yellow
        $warnings += $dir
    }
}

# Check config file
Write-Host "Checking config file..." -ForegroundColor Yellow
$configPath = "C:\DnD\DnD_Cursor\config\paths.json"
if (Test-Path $configPath) {
    Write-Host "  [OK] $configPath exists" -ForegroundColor Green
    try {
        $config = Get-Content $configPath | ConvertFrom-Json
        Write-Host "  [OK] Config file is valid JSON" -ForegroundColor Green
        Write-Host "  Default campaign: $($config.default_campaign)" -ForegroundColor Cyan
        Write-Host "  Campaign dir: $($config.default_campaign_dir)" -ForegroundColor Cyan
    } catch {
        Write-Host "  [ERROR] Config file is not valid JSON: $_" -ForegroundColor Red
        $errors += "Invalid JSON in paths.json"
    }
} else {
    Write-Host "  [WARN] $configPath does not exist" -ForegroundColor Yellow
    $warnings += $configPath
}

# Check character files
Write-Host "Checking character files..." -ForegroundColor Yellow
$charFiles = Get-ChildItem "C:\DnD\Campaigns\Phandelver\characters\*.json" -ErrorAction SilentlyContinue
if ($charFiles) {
    Write-Host "  [OK] Found $($charFiles.Count) character file(s):" -ForegroundColor Green
    foreach ($file in $charFiles) {
        Write-Host "    - $($file.Name)" -ForegroundColor Cyan
    }
} else {
    Write-Host "  [WARN] No character JSON files found" -ForegroundColor Yellow
    $warnings += "No character files"
}

# Check save state
Write-Host "Checking save state..." -ForegroundColor Yellow
$stateFile = "C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json"
if (Test-Path $stateFile) {
    Write-Host "  [OK] Save state file exists" -ForegroundColor Green
    try {
        $state = Get-Content $stateFile -Encoding UTF8 | ConvertFrom-Json
        Write-Host "  [OK] Save state is valid JSON" -ForegroundColor Green
        Write-Host "  Last saved: $($state.last_saved)" -ForegroundColor Cyan
        Write-Host "  Current scene: $($state.scene.area)" -ForegroundColor Cyan
    } catch {
        Write-Host "  [ERROR] Save state is not valid JSON: $_" -ForegroundColor Red
        $errors += "Invalid JSON in CURRENT_STATE.json"
    }
} else {
    Write-Host "  [WARN] Save state file does not exist" -ForegroundColor Yellow
    $warnings += "No save state"
}

# Summary
Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "[SUCCESS] All critical paths verified!" -ForegroundColor Green
    exit 0
} elseif ($errors.Count -eq 0) {
    Write-Host "[WARNING] Paths verified with $($warnings.Count) warning(s)" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "[ERROR] Found $($errors.Count) error(s) and $($warnings.Count) warning(s)" -ForegroundColor Red
    exit 1
}



