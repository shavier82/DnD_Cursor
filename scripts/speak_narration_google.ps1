#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Speaks narration using Google Cloud Text-to-Speech (High Quality, Good Free Tier)

.DESCRIPTION
    Uses Google Cloud TTS API with Neural2 voices for natural-sounding narration.

.PARAMETER SessionId
    The session ID (e.g., "20260105234400")

.PARAMETER NarratorFile
    Optional: Direct path to narrator JSON file

.PARAMETER Voice
    Optional: Google Cloud voice name (default: "en-US-Neural2-F" - female neural)

.EXAMPLE
    .\speak_narration_google.ps1 -SessionId "20260105234400"
    
.NOTES
    Requires: Google Cloud credentials JSON file
    Setup: https://cloud.google.com/text-to-speech/docs/quickstart
    Free tier: 0-4 million characters/month
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [string]$NarratorFile,
    
    [Parameter(Mandatory=$false)]
    [string]$Voice = "en-US-Neural2-F"  # Female neural voice, very natural
)

# Check for Google Cloud credentials
$googleCreds = $env:GOOGLE_APPLICATION_CREDENTIALS
if (-not $googleCreds -or -not (Test-Path $googleCreds)) {
    Write-Host "ERROR: GOOGLE_APPLICATION_CREDENTIALS environment variable not set or file not found" -ForegroundColor Red
    Write-Host "Setup instructions:" -ForegroundColor Yellow
    Write-Host "1. Create a Google Cloud project" -ForegroundColor Yellow
    Write-Host "2. Enable Text-to-Speech API" -ForegroundColor Yellow
    Write-Host "3. Create a service account and download JSON key" -ForegroundColor Yellow
    Write-Host "4. Set: `$env:GOOGLE_APPLICATION_CREDENTIALS = 'path/to/credentials.json'" -ForegroundColor Yellow
    Write-Host "See: https://cloud.google.com/text-to-speech/docs/quickstart" -ForegroundColor Yellow
    exit 1
}

# Determine narrator file path
if ($NarratorFile) {
    $narratorPath = $NarratorFile
} elseif ($SessionId) {
    $narratorPath = "C:\DnD\.coord-$SessionId\dnd_out_NARRATOR.json"
} else {
    Write-Host "ERROR: Must provide either -SessionId or -NarratorFile" -ForegroundColor Red
    exit 1
}

# Check if file exists
if (-not (Test-Path $narratorPath)) {
    Write-Host "ERROR: Narrator file not found: $narratorPath" -ForegroundColor Red
    exit 1
}

# Read and parse JSON
try {
    $narratorData = Get-Content $narratorPath -Raw | ConvertFrom-Json
    
    if (-not $narratorData.narration) {
        Write-Host "WARNING: No narration found in file" -ForegroundColor Yellow
        exit 0
    }
    
    $narrationText = $narratorData.narration
    
    if ([string]::IsNullOrWhiteSpace($narrationText) -or $narrationText -eq "(none)") {
        Write-Host "No narration to speak" -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "Speaking narration with Google Cloud TTS..." -ForegroundColor Green
    Write-Host "`n$narrationText`n" -ForegroundColor Cyan
    
    # Check if gcloud CLI is available (for authentication)
    # Alternative: Use Python with google-cloud-texttospeech
    
    Write-Host "Note: Google Cloud TTS requires Python SDK or gcloud CLI" -ForegroundColor Yellow
    Write-Host "For best integration, use the Python version:" -ForegroundColor Yellow
    Write-Host "  python scripts\speak_narration_google.py -SessionId $SessionId" -ForegroundColor Yellow
    
    # Try using Python if available
    $pythonScript = Join-Path $PSScriptRoot "speak_narration_google.py"
    if (Test-Path $pythonScript) {
        python $pythonScript --session-id $SessionId --voice $Voice
    } else {
        Write-Host "Python script not found. Install google-cloud-texttospeech:" -ForegroundColor Yellow
        Write-Host "  pip install google-cloud-texttospeech" -ForegroundColor Yellow
        Write-Host "Then use the Python script for full functionality." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "ERROR: Failed to process narration: $_" -ForegroundColor Red
    exit 1
}


















