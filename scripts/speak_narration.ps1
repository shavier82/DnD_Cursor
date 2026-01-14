#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Speaks the narration from a NARRATOR agent output file using Windows TTS with natural voices

.DESCRIPTION
    Reads the narration text from dnd_out_NARRATOR.json and uses Windows SAPI
    to speak it aloud with natural-sounding neural voices (Windows 11) or best available voice.

.PARAMETER SessionId
    The session ID (e.g., "20260105234400")

.PARAMETER NarratorFile
    Optional: Direct path to narrator JSON file. If not provided, uses SessionId to construct path.

.PARAMETER Voice
    Optional: Specific voice name to use. If not provided, uses best available neural voice.

.EXAMPLE
    .\speak_narration.ps1 -SessionId "20260105234400"
    
.EXAMPLE
    .\speak_narration.ps1 -NarratorFile "C:\DnD\.coord-20260105234400\dnd_out_NARRATOR.json" -Voice "Microsoft Aria Neural"
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [string]$NarratorFile,
    
    [Parameter(Mandatory=$false)]
    [string]$Voice,
    
    [Parameter(Mandatory=$false)]
    [switch]$Background = $false
)

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
    
    Write-Host "Speaking narration..." -ForegroundColor Green
    Write-Host "`n$narrationText`n" -ForegroundColor Cyan
    
    # Use Windows SAPI (Speech API) to speak the text
    Add-Type -AssemblyName System.Speech
    $speechSynthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
    
    # Get available voices
    $availableVoices = $speechSynthesizer.GetInstalledVoices()
    
    # Try to find a neural voice (Windows 11) or best available
    $selectedVoice = $null
    
    if ($Voice) {
        # Use specified voice
        $selectedVoice = $availableVoices | Where-Object { $_.VoiceInfo.Name -like "*$Voice*" } | Select-Object -First 1
    } else {
        # Prefer neural voices (Windows 11) - these sound much more natural
        $neuralVoices = $availableVoices | Where-Object { $_.VoiceInfo.Name -like "*Neural*" }
        
        if ($neuralVoices) {
            # Prefer female neural voices for narration (often sound better for storytelling)
            $femaleNeural = $neuralVoices | Where-Object { 
                $_.VoiceInfo.Name -like "*Aria*" -or 
                $_.VoiceInfo.Name -like "*Jenny*" -or
                $_.VoiceInfo.Name -like "*Ana*"
            } | Select-Object -First 1
            
            if ($femaleNeural) {
                $selectedVoice = $femaleNeural
            } else {
                $selectedVoice = $neuralVoices | Select-Object -First 1
            }
        } else {
            # Fall back to best available non-neural voice
            # Prefer female voices for narration
            $femaleVoices = $availableVoices | Where-Object { 
                $_.VoiceInfo.Name -like "*Zira*" -or 
                $_.VoiceInfo.Name -like "*Hazel*" -or
                $_.VoiceInfo.Gender -eq "Female"
            } | Select-Object -First 1
            
            if ($femaleVoices) {
                $selectedVoice = $femaleVoices
            } else {
                $selectedVoice = $availableVoices | Select-Object -First 1
            }
        }
    }
    
    if ($selectedVoice) {
        $speechSynthesizer.SelectVoice($selectedVoice.VoiceInfo.Name)
        Write-Host "Using voice: $($selectedVoice.VoiceInfo.Name)" -ForegroundColor Gray
    } else {
        Write-Host "WARNING: Could not find preferred voice, using default" -ForegroundColor Yellow
    }
    
    # Optimize speech settings for natural narration
    $speechSynthesizer.Rate = -2  # Slower for natural pacing and clarity (-10 to 10)
    $speechSynthesizer.Volume = 100  # Full volume (0 to 100)
    
    # Add natural pauses for better flow
    # Replace sentence endings with pauses for more natural rhythm
    $enhancedText = $narrationText
    
    # Add brief pauses after periods (except at end)
    $enhancedText = $enhancedText -replace '\.([^\s])', '. $1'
    
    # Add longer pauses after paragraph breaks or significant punctuation
    $enhancedText = $enhancedText -replace '\.\s+([A-Z])', '. ... $1'
    
    # Clean up any double spaces
    $enhancedText = $enhancedText -replace '\s{2,}', ' '
    
    # Speak the enhanced narration
    if ($Background) {
        # Run TTS in separate process (not job) to prevent blocking while maintaining audio access
        Write-Host "Starting TTS in background process..." -ForegroundColor Gray
        
        # Create a temporary script file with the TTS code
        $tempScript = [System.IO.Path]::GetTempFileName() + ".ps1"
        $scriptContent = @"
Add-Type -AssemblyName System.Speech
`$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    `$synth.SelectVoice('$($selectedVoice.VoiceInfo.Name)')
} catch {}
`$synth.Rate = $($speechSynthesizer.Rate)
`$synth.Volume = $($speechSynthesizer.Volume)
`$synth.Speak(@'
$($enhancedText -replace "'", "''")
'@)
`$synth.Dispose()
"@
        Set-Content -Path $tempScript -Value $scriptContent -Encoding UTF8
        
        # Launch in separate process with hidden window (has audio access)
        $process = Start-Process -FilePath "powershell.exe" -ArgumentList @(
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-WindowStyle", "Hidden",
            "-File", $tempScript
        ) -PassThru
        
        # Clean up local synthesizer (separate process has its own)
        $speechSynthesizer.Dispose()
        
        # Schedule temp script cleanup after process completes (non-blocking)
        Register-ObjectEvent -InputObject $process -EventName Exited -Action {
            Start-Sleep -Seconds 2
            Remove-Item $tempScript -ErrorAction SilentlyContinue
        } | Out-Null
        
        Write-Host "TTS running in background process (non-blocking)" -ForegroundColor Green
        return
    } else {
        # Blocking mode (original behavior)
        $speechSynthesizer.Speak($enhancedText)
        $speechSynthesizer.Dispose()
        Write-Host "Done." -ForegroundColor Green
    }
    
} catch {
    Write-Host "ERROR: Failed to process narration: $_" -ForegroundColor Red
    exit 1
}
