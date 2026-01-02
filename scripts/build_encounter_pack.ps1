# Build Encounter Pack
# Compiles encounter/scene data into encounter_pack.json

param(
    [Parameter(Mandatory=$false)]
    [string]$SceneId,
    
    [Parameter(Mandatory=$false)]
    [string]$Keyword
)

$ErrorActionPreference = "Stop"

# Load paths config
$configPath = Join-Path $PSScriptRoot "..\config\paths.json"
if (-not (Test-Path $configPath)) {
    Write-Error "Config file not found: $configPath"
    exit 1
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json
$chaptersDir = $config.chapters_dir
$packsDir = $config.packs_dir

# Ensure packs directory exists
if (-not (Test-Path $packsDir)) {
    New-Item -ItemType Directory -Force -Path $packsDir | Out-Null
}

# Build minimal encounter pack
$encounterPack = @{
    pack_type = "encounter_pack"
    pack_version = "1.0"
    source = "Mines of Phandelver and Below"
    chapter = $null
    scene_id = $SceneId
    keyword = $Keyword
    cards = @()
} | ConvertTo-Json -Depth 10

$outputPath = Join-Path $packsDir "encounter_pack.json"
Set-Content -Path $outputPath -Value $encounterPack -Encoding UTF8

Write-Host "Built: $outputPath"

