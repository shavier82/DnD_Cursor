# PACK Validation Script
# Validates all JSON pack files in the packs\ directory
# Returns exit code 0 if all valid, non-zero if any errors found

$ErrorActionPreference = "Stop"

# Load paths config
$configPath = Join-Path $PSScriptRoot "..\config\paths.json"
if (-not (Test-Path $configPath)) {
    Write-Host "ERROR: Config file not found: $configPath" -ForegroundColor Red
    exit 1
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json
$packDir = $config.packs_dir

$exitCode = 0
$errors = @()

Write-Host "Validating PACK files in: $packDir" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $packDir)) {
    Write-Host "ERROR: Packs directory not found: $packDir" -ForegroundColor Red
    exit 1
}

$requiredKeys = @("pack_type", "pack_version", "source", "chapter", "cards")
$validPackTypes = @("session_preload", "chapter_pack", "encounter_pack")

$packFiles = Get-ChildItem -Path $packDir -Filter "*.json" -File

if ($packFiles.Count -eq 0) {
    Write-Host "WARNING: No JSON files found in packs directory" -ForegroundColor Yellow
    exit 0
}

foreach ($file in $packFiles) {
    $filePath = $file.FullName
    Write-Host "Checking: $($file.Name)..." -ForegroundColor White -NoNewline
    
    try {
        # Try to parse as JSON
        $content = Get-Content $filePath -Raw | ConvertFrom-Json
        
        # Validate required top-level keys exist
        $missingKeys = @()
        foreach ($key in $requiredKeys) {
            if (-not (Get-Member -InputObject $content -Name $key -MemberType NoteProperty)) {
                $missingKeys += $key
            }
        }
        
        if ($missingKeys.Count -gt 0) {
            $errorMsg = "$($file.Name): Missing required keys: $($missingKeys -join ', ')"
            $errors += $errorMsg
            Write-Host " FAILED" -ForegroundColor Red
            Write-Host "  $errorMsg" -ForegroundColor Red
            $exitCode = 1
            continue
        }
        
        # Validate pack_type
        if ($validPackTypes -notcontains $content.pack_type) {
            $errorMsg = "$($file.Name): Invalid pack_type '$($content.pack_type)'. Must be one of: $($validPackTypes -join ', ')"
            $errors += $errorMsg
            Write-Host " FAILED" -ForegroundColor Red
            Write-Host "  $errorMsg" -ForegroundColor Red
            $exitCode = 1
            continue
        }
        
        # Validate chapter field
        if ($content.pack_type -eq "chapter_pack") {
            if ($null -eq $content.chapter -or ($content.chapter -isnot [int] -and $content.chapter -isnot [long])) {
                $errorMsg = "$($file.Name): chapter_pack must have chapter as a number, got: $($content.chapter)"
                $errors += $errorMsg
                Write-Host " FAILED" -ForegroundColor Red
                Write-Host "  $errorMsg" -ForegroundColor Red
                $exitCode = 1
                continue
            }
        } else {
            if ($null -ne $content.chapter) {
                $errorMsg = "$($file.Name): $($content.pack_type) must have chapter as null, got: $($content.chapter)"
                $errors += $errorMsg
                Write-Host " FAILED" -ForegroundColor Red
                Write-Host "  $errorMsg" -ForegroundColor Red
                $exitCode = 1
                continue
            }
        }
        
        # Validate cards is an array
        if ($content.cards -isnot [array]) {
            $errorMsg = "$($file.Name): cards must be an array"
            $errors += $errorMsg
            Write-Host " FAILED" -ForegroundColor Red
            Write-Host "  $errorMsg" -ForegroundColor Red
            $exitCode = 1
            continue
        }
        
        # Chapter pack specific validations
        if ($content.pack_type -eq "chapter_pack") {
            # Must have cards (PLAY-safe)
            if ($content.cards.Count -eq 0) {
                $errorMsg = "$($file.Name): chapter_pack must have at least one card"
                $errors += $errorMsg
                Write-Host " FAILED" -ForegroundColor Red
                Write-Host "  $errorMsg" -ForegroundColor Red
                $exitCode = 1
                continue
            }
            
            # Must NOT have raw_text (PLAY-safe)
            if (Get-Member -InputObject $content -Name "raw_text" -MemberType NoteProperty) {
                $errorMsg = "$($file.Name): chapter_pack must NOT contain raw_text (PLAY safety violation)"
                $errors += $errorMsg
                Write-Host " FAILED" -ForegroundColor Red
                Write-Host "  $errorMsg" -ForegroundColor Red
                $exitCode = 1
                continue
            }
        }
        
        Write-Host " OK" -ForegroundColor Green
        
    } catch {
        $errorMsg = "$($file.Name): Invalid JSON - $($_.Exception.Message)"
        $errors += $errorMsg
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "  $errorMsg" -ForegroundColor Red
        $exitCode = 1
    }
}

Write-Host ""

if ($exitCode -eq 0) {
    Write-Host "All pack files are valid!" -ForegroundColor Green
} else {
    Write-Host "Validation failed. Errors found:" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host ("  - " + $err) -ForegroundColor Red
    }
}

exit $exitCode




