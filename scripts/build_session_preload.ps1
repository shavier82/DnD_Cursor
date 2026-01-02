# Build Session Preload Pack
# Compiles always-on session data into session_preload.json

param()

$ErrorActionPreference = "Stop"

# Load paths config
$configPath = Join-Path $PSScriptRoot "..\config\paths.json"
if (-not (Test-Path $configPath)) {
    Write-Error "Config file not found: $configPath"
    exit 1
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json
$packsDir = $config.packs_dir

# Ensure packs directory exists
if (-not (Test-Path $packsDir)) {
    New-Item -ItemType Directory -Force -Path $packsDir | Out-Null
}

# Build minimal session preload
$preload = @{
    pack_type = "session_preload"
    pack_version = "1.0"
    source = "Mines of Phandelver and Below"
    chapter = $null
    cards = @()
} | ConvertTo-Json -Depth 10

$outputPath = Join-Path $packsDir "session_preload.json"
Set-Content -Path $outputPath -Value $preload -Encoding UTF8

Write-Host "Built: $outputPath"

