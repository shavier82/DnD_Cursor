# Bootstrap Parallel Agents
# Creates coordination directory and validates setup

param(
    [Parameter(Mandatory=$false)]
    [string]$SessionId
)

$ErrorActionPreference = "Stop"

# Generate session ID if not provided
if (-not $SessionId) {
    $SessionId = "dnd-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "Generated session ID: $SessionId" -ForegroundColor Cyan
} else {
    Write-Host "Using provided session ID: $SessionId" -ForegroundColor Cyan
}

# Validate session ID format
if ($SessionId -notmatch '^[a-zA-Z0-9_-]+$') {
    Write-Error "Invalid session ID format. Use alphanumeric, dash, or underscore only."
    exit 1
}

# Define paths
$CoordDir = "C:\DnD\.coord-$SessionId"
$CampaignPath = "C:\DnD\Campaigns\Phandelver"
$RepoPath = "C:\DnD\DnD_Cursor"

# Safety checks
Write-Host "`nRunning safety checks..." -ForegroundColor Yellow

# Check campaign is NOT a git repo
if (Test-Path "$CampaignPath\.git") {
    Write-Error "CRITICAL: Campaign folder is a Git repo! This violates safety rules."
    exit 1
}
Write-Host "  ✓ Campaign folder is safe (not a Git repo)" -ForegroundColor Green

# Verify coordination dir is NOT in campaign
if ($CoordDir -like "$CampaignPath\*") {
    Write-Error "CRITICAL: Coordination directory cannot be inside campaign folder!"
    exit 1
}

# Verify coordination dir is NOT in repo
if ($CoordDir -like "$RepoPath\*") {
    Write-Error "CRITICAL: Coordination directory cannot be inside repo folder!"
    exit 1
}

# Create coordination directory
if (Test-Path $CoordDir) {
    Write-Host "  ⚠ Coordination directory already exists: $CoordDir" -ForegroundColor Yellow
    $response = Read-Host "Continue? (y/n)"
    if ($response -ne 'y') {
        exit 0
    }
} else {
    New-Item -ItemType Directory -Force -Path $CoordDir | Out-Null
    Write-Host "  ✓ Created coordination directory: $CoordDir" -ForegroundColor Green
}

# Verify required files exist
Write-Host "`nVerifying required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "$RepoPath\campaign_path.txt",
    "$RepoPath\packs\session_preload.json"
)

$allExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file MISSING" -ForegroundColor Red
        $allExist = $false
    }
}

if (-not $allExist) {
    Write-Error "Required files missing. Cannot proceed."
    exit 1
}

# Output session info
Write-Host "`n=== Bootstrap Complete ===" -ForegroundColor Cyan
Write-Host "Session ID: $SessionId" -ForegroundColor White
Write-Host "Coordination Directory: $CoordDir" -ForegroundColor White
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Run /dnd_turn_parallel $SessionId" -ForegroundColor Cyan
Write-Host "2. Wait for all agents to complete" -ForegroundColor Cyan
Write-Host "3. Run /dnd_turn_merge $SessionId" -ForegroundColor Cyan

# Save session ID to file for reference
$sessionFile = Join-Path $CoordDir ".session-id"
Set-Content -Path $sessionFile -Value $SessionId
Write-Host "`nSession ID saved to: $sessionFile" -ForegroundColor Gray




