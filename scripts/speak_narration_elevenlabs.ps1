#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Speaks narration using ElevenLabs AI TTS (Premium Quality, Free Tier Available)

.DESCRIPTION
    Uses ElevenLabs API for extremely natural-sounding narration.
    Free tier: 10,000 characters/month (no billing required!)

.PARAMETER SessionId
    The session ID (e.g., "20260105234400")

.PARAMETER NarratorFile
    Optional: Direct path to narrator JSON file

.PARAMETER VoiceId
    Optional: ElevenLabs voice ID (default: "21m00Tcm4TlvDq8ikWAM" - Rachel)

.EXAMPLE
    .\speak_narration_elevenlabs.ps1 -SessionId "20260105234400"
    
.NOTES
    Requires: $env:ELEVENLABS_API_KEY to be set
    Get free API key from: https://elevenlabs.io (free account, no billing!)
    Free tier: 10,000 characters/month
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [string]$NarratorFile,
    
    [Parameter(Mandatory=$false)]
    [string]$VoiceId = "21m00Tcm4TlvDq8ikWAM"  # Rachel - excellent for narration
)

# Check for API key
if (-not $env:ELEVENLABS_API_KEY) {
    Write-Host "ERROR: ELEVENLABS_API_KEY environment variable not set" -ForegroundColor Red
    Write-Host ""
    Write-Host "Setup (FREE, no billing required):" -ForegroundColor Yellow
    Write-Host "1. Sign up at https://elevenlabs.io (free account)" -ForegroundColor Yellow
    Write-Host "2. Go to Profile → API Key" -ForegroundColor Yellow
    Write-Host "3. Copy your API key" -ForegroundColor Yellow
    Write-Host "4. Set it with: `$env:ELEVENLABS_API_KEY = 'your-key-here'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Free tier: 10,000 characters/month (no billing account needed!)" -ForegroundColor Green
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
    
    # Check character count (free tier limit)
    $charCount = $narrationText.Length
    if ($charCount -gt 10000) {
        Write-Host "WARNING: Narration is $charCount characters (free tier limit: 10,000)" -ForegroundColor Yellow
        Write-Host "Truncating to first 10,000 characters..." -ForegroundColor Yellow
        $narrationText = $narrationText.Substring(0, 10000)
    }
    
    Write-Host "Speaking narration with ElevenLabs (Premium Quality)..." -ForegroundColor Green
    Write-Host "Characters: $charCount / 10,000 (free tier)" -ForegroundColor Gray
    Write-Host "`n$narrationText`n" -ForegroundColor Cyan
    
    # ElevenLabs API endpoint
    $apiUrl = "https://api.elevenlabs.io/v1/text-to-speech/$VoiceId"
    
    # Prepare request body
    $body = @{
        text = $narrationText
        model_id = "eleven_turbo_v2"  # Free tier compatible model
        voice_settings = @{
            stability = 0.5
            similarity_boost = 0.75
        }
    } | ConvertTo-Json -Depth 10
    
    # Make API request
    $headers = @{
        "Accept" = "audio/mpeg"
        "Content-Type" = "application/json"
        "xi-api-key" = $env:ELEVENLABS_API_KEY
    }
    
    try {
        Write-Host "Synthesizing speech..." -ForegroundColor Gray
        $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $body -ContentType "application/json"
        
        # Save audio to temp file
        $tempAudio = [System.IO.Path]::GetTempFileName() + ".mp3"
        [System.IO.File]::WriteAllBytes($tempAudio, $response)
        
        Write-Host "Playing audio..." -ForegroundColor Gray
        
        # Try multiple playback methods
        $played = $false
        
        # Method 1: Windows Media Player COM object
        try {
            $wmp = New-Object -ComObject WMPlayer.OCX
            $wmp.URL = $tempAudio
            $wmp.controls.play()
            
            # Wait for playback to complete
            while ($wmp.playState -ne 1) {  # 1 = stopped
                Start-Sleep -Milliseconds 500
            }
            
            $played = $true
        } catch {
            Write-Host "Method 1 failed, trying alternative..." -ForegroundColor DarkGray
        }
        
        # Method 2: Start default media player
        if (-not $played) {
            try {
                Start-Process $tempAudio -Wait
                $played = $true
            } catch {
                Write-Host "Method 2 failed" -ForegroundColor DarkGray
            }
        }
        
        # Cleanup
        Start-Sleep -Seconds 1
        Remove-Item $tempAudio -ErrorAction SilentlyContinue
        
        if (-not $played) {
            Write-Host "WARNING: Could not play audio automatically" -ForegroundColor Yellow
            Write-Host "Audio was saved but playback failed" -ForegroundColor Yellow
        }
        
        Write-Host "Done." -ForegroundColor Green
        
    } catch {
        $errorDetails = $_.ErrorDetails.Message
        if ($errorDetails) {
            try {
                $errorJson = $errorDetails | ConvertFrom-Json
                $errorMsg = $errorJson.detail.message
                Write-Host "ERROR: $errorMsg" -ForegroundColor Red
                
                if ($errorMsg -like "*quota*" -or $errorMsg -like "*limit*") {
                    Write-Host ""
                    Write-Host "You've reached your free tier limit (10,000 characters/month)" -ForegroundColor Yellow
                    Write-Host "Upgrade at https://elevenlabs.io or wait for monthly reset" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "ERROR: $errorDetails" -ForegroundColor Red
            }
        } else {
            Write-Host "ERROR: API request failed: $_" -ForegroundColor Red
        }
        exit 1
    }
    
} catch {
    Write-Host "ERROR: Failed to process narration: $_" -ForegroundColor Red
    exit 1
}
