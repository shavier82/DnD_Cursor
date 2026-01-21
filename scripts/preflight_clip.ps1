# scripts/preflight_clip.ps1
# Get script directory and change to project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Force working directory to repo root (prevents CWD drift)
Push-Location $projectRoot
try {
    # Run preflight gate from project root
    $out = & python scripts\preflight_gate.py 2>&1
    $exitCode = $LASTEXITCODE
    
    # Preserve newlines faithfully (join array with newlines)
    $outText = ($out -join "`n").TrimEnd()
    
    # Copy receipt (or error output) to clipboard
    $outText | Set-Clipboard
    
    # Echo to terminal (preserve formatting)
    [Console]::WriteLine($outText)
    
    exit $exitCode
}
finally {
    Pop-Location
}
