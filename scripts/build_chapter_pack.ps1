# Build Chapter Pack
# Compiles raw chapter .txt into chapter_pack_<n>.json

param(
    [Parameter(Mandatory=$true)]
    [int]$Chapter
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

# Ensure directories exist
if (-not (Test-Path $packsDir)) {
    New-Item -ItemType Directory -Force -Path $packsDir | Out-Null
}

# Find chapter file
$chapterFile = Join-Path $chaptersDir "chapter_$($Chapter.ToString('00')).txt"
if (-not (Test-Path $chapterFile)) {
    # Try alternate naming
    $chapterFile = Join-Path $chaptersDir "chapter_$Chapter.txt"
}

if (-not (Test-Path $chapterFile)) {
    Write-Error "Chapter file not found: $chapterFile"
    exit 1
}

# Read raw chapter text
$rawText = Get-Content $chapterFile -Raw -Encoding UTF8

# Build chapter pack (minimal structure - can be expanded)
$chapterPack = @{
    pack_type = "chapter_pack"
    pack_version = "1.0"
    source = "Mines of Phandelver and Below"
    chapter = $Chapter
    raw_text = $rawText
    cards = @()
} | ConvertTo-Json -Depth 10

$outputPath = Join-Path $packsDir "chapter_pack_$Chapter.json"
Set-Content -Path $outputPath -Value $chapterPack -Encoding UTF8

Write-Host "Built: $outputPath"

