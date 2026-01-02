# Build Chapter Pack
# Compiles raw chapter .txt into chapter_pack_<n>.json

param(
    [Parameter(Mandatory=$true)]
    [int]$Chapter,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipRawText = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$sw = [Diagnostics.Stopwatch]::StartNew()
Write-Host "[build] Starting chapter pack build for Chapter $Chapter"

# Load paths config
$configPath = Join-Path $PSScriptRoot "..\config\paths.json"
if (-not (Test-Path $configPath)) {
    Write-Error "Config file not found: $configPath"
    exit 1
}

Write-Host "[build] Loading config..."
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$chaptersDir = $config.chapters_dir
$packsDir = $config.packs_dir
Write-Host ("[build] Config loaded in {0}ms" -f $sw.ElapsedMilliseconds)

# Ensure directories exist
if (-not (Test-Path $packsDir)) {
    New-Item -ItemType Directory -Force -Path $packsDir | Out-Null
}

# Find chapter file (case-insensitive, multiple patterns)
$patterns = @(
    "chapter_$($Chapter.ToString('00')).txt",
    "chapter_$Chapter.txt",
    "Chapter_$($Chapter.ToString('00')).txt",
    "Chapter_$Chapter.txt"
)

Write-Host "[build] Locating chapter file..."
$chapterFile = $null
foreach ($pattern in $patterns) {
    $testPath = Join-Path $chaptersDir $pattern
    if (Test-Path $testPath) {
        $chapterFile = $testPath
        break
    }
}

# Also try case-insensitive search
if (-not $chapterFile) {
    $allFiles = Get-ChildItem $chaptersDir -File -Filter "*.txt"
    $chapterFile = $allFiles | Where-Object { 
        $_.Name -match "^[Cc]hapter_0?$Chapter\.txt$" 
    } | Select-Object -First 1 -ExpandProperty FullName
}

if (-not $chapterFile) {
    Write-Error "Chapter file not found. Tried: $($patterns -join ', ')"
    exit 1
}

Write-Host ("[build] Using chapter file: $chapterFile")

# Read raw chapter text (only if not skipping)
$rawText = $null
$rawTextPath = $null

if (-not $SkipRawText) {
    Write-Host "[build] Reading raw text..."
    $rawText = Get-Content $chapterFile -Raw -Encoding UTF8
    Write-Host ("[build] Read {0} chars in {1}ms" -f $rawText.Length, $sw.ElapsedMilliseconds)
} else {
    $rawTextPath = $chapterFile
    Write-Host "[build] Skipping raw text embedding (using path reference)"
}

# Build chapter pack
Write-Host "[build] Building pack structure..."
$chapterPack = @{
    pack_type = "chapter_pack"
    pack_version = "1.0"
    source = "Mines of Phandelver and Below"
    chapter = $Chapter
    cards = @()
}

if ($SkipRawText) {
    $chapterPack.raw_text_path = $rawTextPath
} else {
    $chapterPack.raw_text = $rawText
}

Write-Host "[build] Serializing JSON..."
$chapterPackJson = $chapterPack | ConvertTo-Json -Depth 10
Write-Host ("[build] Serialized in {0}ms" -f $sw.ElapsedMilliseconds)

$outputPath = Join-Path $packsDir "chapter_pack_$Chapter.json"
Write-Host "[build] Writing output..."
Set-Content -Path $outputPath -Value $chapterPackJson -Encoding UTF8
Write-Host ("[build] DONE: $outputPath ({0}ms total)" -f $sw.ElapsedMilliseconds)
