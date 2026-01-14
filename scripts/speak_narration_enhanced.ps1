#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Speaks narration with enhanced natural delivery using Azure Cognitive Services TTS

.DESCRIPTION
    Uses Azure Cognitive Services TTS for premium-quality, natural-sounding narration.
    Falls back to Windows SAPI with optimized settings if Azure is not configured.

.PARAMETER SessionId
    The session ID (e.g., "20260105234400")

.PARAMETER NarratorFile
    Optional: Direct path to narrator JSON file

.PARAMETER UseAzure
    Use Azure Cognitive Services TTS (requires configuration)

.EXAMPLE
    .\speak_narration_enhanced.ps1 -SessionId "20260105234400"
    
.EXAMPLE
    .\speak_narration_enhanced.ps1 -SessionId "20260105234400" -UseAzure
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [string]$NarratorFile,
    
    [Parameter(Mandatory=$false)]
    [switch]$UseAzure
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
    
    # Try Azure TTS first if requested
    if ($UseAzure) {
        $azureConfig = @{
            SubscriptionKey = $env:AZURE_SPEECH_KEY
            Region = $env:AZURE_SPEECH_REGION
        }
        
        if ($azureConfig.SubscriptionKey -and $azureConfig.Region) {
            Write-Host "Using Azure Cognitive Services TTS..." -ForegroundColor Green
            
            # Install module if needed
            if (-not (Get-Module -ListAvailable -Name Azure.CognitiveServices.Speech)) {
                Write-Host "Installing Azure Speech SDK..." -ForegroundColor Yellow
                Install-Module -Name Azure.CognitiveServices.Speech -Force -Scope CurrentUser
            }
            
            Import-Module Azure.CognitiveServices.Speech
            
            $speechConfig = [Microsoft.CognitiveServices.Speech.SpeechConfig]::FromSubscription(
                $azureConfig.SubscriptionKey,
                $azureConfig.Region
            )
            
            # Use a natural-sounding voice (e.g., Aria, Jenny, or Guy)
            $speechConfig.SpeechSynthesisVoiceName = "en-US-AriaNeural"
            
            $synthesizer = [Microsoft.CognitiveServices.Speech.SpeechSynthesizer]::new($speechConfig)
            
            # Add SSML for natural prosody
            $ssmlText = @"
<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
    <voice name='en-US-AriaNeural'>
        <prosody rate='medium' pitch='medium'>
            $narrationText
        </prosody>
    </voice>
</speak>
"@
            
            $result = $synthesizer.SpeakSsmlAsync($ssmlText).GetAwaiter().GetResult()
            
            if ($result.Reason -eq [Microsoft.CognitiveServices.Speech.ResultReason]::SynthesizingAudioCompleted) {
                Write-Host "Done." -ForegroundColor Green
                exit 0
            } else {
                Write-Host "Azure TTS failed, falling back to Windows TTS..." -ForegroundColor Yellow
            }
        } else {
            Write-Host "Azure not configured. Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables." -ForegroundColor Yellow
            Write-Host "Falling back to Windows TTS..." -ForegroundColor Yellow
        }
    }
    
    # Fall back to Windows SAPI with optimized settings
    Add-Type -AssemblyName System.Speech
    $speechSynthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
    
    # Get available voices
    $availableVoices = $speechSynthesizer.GetInstalledVoices()
    
    # Prefer neural voices
    $neuralVoices = $availableVoices | Where-Object { $_.VoiceInfo.Name -like "*Neural*" }
    
    if ($neuralVoices) {
        $femaleNeural = $neuralVoices | Where-Object { 
            $_.VoiceInfo.Name -like "*Aria*" -or 
            $_.VoiceInfo.Name -like "*Jenny*" -or
            $_.VoiceInfo.Name -like "*Ana*"
        } | Select-Object -First 1
        
        if ($femaleNeural) {
            $speechSynthesizer.SelectVoice($femaleNeural.VoiceInfo.Name)
            Write-Host "Using voice: $($femaleNeural.VoiceInfo.Name)" -ForegroundColor Gray
        } else {
            $speechSynthesizer.SelectVoice($neuralVoices[0].VoiceInfo.Name)
            Write-Host "Using voice: $($neuralVoices[0].VoiceInfo.Name)" -ForegroundColor Gray
        }
    }
    
    # Optimize for natural narration
    $speechSynthesizer.Rate = -2  # Slightly slower for clarity and natural pacing
    $speechSynthesizer.Volume = 100
    
    # Add pauses for natural flow (replace periods with longer pauses)
    $enhancedText = $narrationText -replace '\. ', '. ... '
    $enhancedText = $enhancedText -replace '\.\.\. \.\.\.', '...'  # Don't double up
    
    # Speak with enhanced text
    $speechSynthesizer.Speak($enhancedText)
    
    Write-Host "Done." -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: Failed to process narration: $_" -ForegroundColor Red
    exit 1
}


















