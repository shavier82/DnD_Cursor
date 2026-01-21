# scripts/map_clip.ps1
# Get script directory and change to project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

# Run map guard from project root
$out = & python scripts\map_guard.py 2>&1
$exitCode = $LASTEXITCODE

# Preserve newlines faithfully (join array with newlines)
$outText = ($out -join "`n").TrimEnd()

# Copy receipt (or error output) to clipboard
$outText | Set-Clipboard

# Echo to terminal (preserve formatting)
[Console]::WriteLine($outText)

exit $exitCode
