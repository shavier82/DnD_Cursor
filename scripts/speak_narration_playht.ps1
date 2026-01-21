#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Speaks narration using Play.ht AI TTS (Best Value)

.DESCRIPTION
    Uses Play.ht API for natural-sounding narration with good pricing.

.PARAMETER SessionId
    The session ID (e.g., "20260105234400")

.PARAMETER NarratorFile
    Optional: Direct path to narrator JSON file

.PARAMETER Voice
    Optional: Play.ht voice name (default: "Michael" - good for narration)

.EXAMPLE
    .\speak_narration_playht.ps1 -SessionId "20260105234400"
    
.NOTES
    Requires: $env:PLAYHT_API_KEY and $env:PLAYHT_USER_ID to be set
    Get credentials from: https://play.ht
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [string]$NarratorFile,
    
    [Parameter(Mandatory=$false)]
    [string]$Voice = "Michael"  # Good narration voice
)

# Check for API credentials
if (-not $env:PLAYHT_API_KEY -or -not $env:PLAYHT_USER_ID) {
    Write-Host "ERROR: PLAYHT_API_KEY and PLAYHT_USER_ID environment variables not set" -ForegroundColor Red
    Write-Host "Get your credentials from: https://play.ht" -ForegroundColor Yellow
    Write-Host "Set them with:" -ForegroundColor Yellow
    Write-Host "  `$env:PLAYHT_USER_ID = 'your-user-id'" -ForegroundColor Yellow
    Write-Host "  `$env:PLAYHT_API_KEY = 'your-api-key'" -ForegroundColor Yellow
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
    
    Write-Host "Speaking narration with Play.ht..." -ForegroundColor Green
    Write-Host "`n$narrationText`n" -ForegroundColor Cyan
    
    # Play.ht API endpoint
    $apiUrl = "https://api.play.ht/api/v2/tts"
    
    # Prepare request body
    $body = @{
        text = $narrationText
        voice = $Voice
        output_format = "mp3"
        sample_rate = 24000
    } | ConvertTo-Json
    
    # Make API request
    $headers = @{
        "AUTHORIZATION" = "Bearer $env:PLAYHT_API_KEY"
        "X-USER-ID" = $env:PLAYHT_USER_ID
        "Content-Type" = "application/json"
    }
    
    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $body -ContentType "application/json"
        
        # Get audio URL from response
        $audioUrl = $response.output_url
        
        if (-not $audioUrl) {
            Write-Host "ERROR: No audio URL in response" -ForegroundColor Red
            exit 1
        }
        
        # Download audio
        $tempAudio = [System.IO.Path]::GetTempFileName() + ".mp3"
        Invoke-WebRequest -Uri $audioUrl -OutFile $tempAudio
        
        # Play audio
        Add-Type -AssemblyName presentationCore
        $mediaPlayer = New-Object system.windows.media.mediaplayer
        $mediaPlayer.open([uri]$tempAudio)
        $mediaPlayer.Play()
        
        # Wait for playback to complete
        while ($mediaPlayer.Position -lt $mediaPlayer.NaturalDuration.TimeSpan) {
            Start-Sleep -Milliseconds 100
        }
        
        # Cleanup
        $mediaPlayer.Stop()
        Remove-Item $tempAudio -ErrorAction SilentlyContinue
        
        Write-Host "Done." -ForegroundColor Green
        
    } catch {
        $errorDetails = $_.ErrorDetails.Message
        if ($errorDetails) {
            Write-Host "ERROR: $errorDetails" -ForegroundColor Red
        } else {
            Write-Host "ERROR: API request failed: $_" -ForegroundColor Red
        }
        exit 1
    }
    
} catch {
    Write-Host "ERROR: Failed to process narration: $_" -ForegroundColor Red
    exit 1
}
































