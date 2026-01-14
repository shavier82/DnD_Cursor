#!/usr/bin/env pwsh
# Lists all available Windows TTS voices

Add-Type -AssemblyName System.Speech
$speechSynthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer

$voices = $speechSynthesizer.GetInstalledVoices()

Write-Host ""
Write-Host "Available TTS Voices:" -ForegroundColor Cyan
Write-Host ""
$separator = "=" * 60
Write-Host $separator

foreach ($voice in $voices) {
    $voiceInfo = $voice.VoiceInfo
    $isNeural = $voiceInfo.Name -like "*Neural*"
    
    if ($isNeural) {
        Write-Host "Neural: " -ForegroundColor Green -NoNewline
        Write-Host $voiceInfo.Name -ForegroundColor Green
    } else {
        Write-Host "Standard: " -ForegroundColor Gray -NoNewline
        Write-Host $voiceInfo.Name -ForegroundColor Gray
    }
    
    Write-Host "  Culture: $($voiceInfo.Culture)" -ForegroundColor DarkGray
    Write-Host "  Gender: $($voiceInfo.Gender)" -ForegroundColor DarkGray
    Write-Host ""
}

Write-Host $separator
Write-Host ""
Write-Host "Tip: Neural voices (Windows 11) sound much more natural!" -ForegroundColor Yellow
Write-Host "Use -Voice parameter to specify a voice name." -ForegroundColor Yellow
Write-Host ""
