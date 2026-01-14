# Text-to-Speech Integration

This document describes how to use text-to-speech (TTS) to speak the narration from the D&D campaign system with natural-sounding voices.

## Quick Start

### PowerShell Script (Windows - Recommended)

The easiest way on Windows is to use the PowerShell script:

```powershell
# After a turn is processed, speak the narration
.\scripts\speak_narration.ps1 -SessionId "20260105234400"

# Or with direct file path
.\scripts\speak_narration.ps1 -NarratorFile "C:\DnD\.coord-20260105234400\dnd_out_NARRATOR.json"
```

**Requirements:** None - uses built-in Windows SAPI (Speech API)

**Note:** The script automatically prefers **Neural voices** (Windows 11) which sound much more natural than standard voices.

## Getting Better Voices

### Windows 11 Neural Voices (Best Quality - Free)

Windows 11 includes neural voices that sound much more natural. To install them:

1. **Settings → Time & Language → Speech**
2. Click **"Manage voices"**
3. Install neural voices (e.g., "Microsoft Aria Neural", "Microsoft Jenny Neural")

Or install via PowerShell (Admin):

```powershell
# Install English (US) neural voices
Add-WindowsCapability -Online -Name Language.Speech.en-US-Neural
```

### List Available Voices

To see what voices you have installed:

```powershell
.\scripts\list_voices.ps1
```

This will show all available voices and highlight neural voices (recommended).

### Use a Specific Voice

To use a specific voice:

```powershell
.\scripts\speak_narration.ps1 -SessionId "20260105234400" -Voice "Microsoft Aria Neural"
```

## Voice Quality Comparison

### Standard Voices (Robotic)
- Microsoft Zira Desktop
- Microsoft David Desktop
- Sound more mechanical and less natural

### Neural Voices (Natural - Recommended)
- Microsoft Aria Neural (female, very natural)
- Microsoft Jenny Neural (female, natural)
- Microsoft Ana Neural (female, natural)
- Microsoft Guy Neural (male, natural)
- Sound much more human-like and expressive

## Integration Options

### Option 1: Manual (After Each Turn)

After each turn, manually run the TTS script:

```powershell
# After turn processing
.\scripts\speak_narration.ps1 -SessionId "20260105234400"
```

### Option 2: Auto-Integration (Modify Merge Script)

You can modify `scripts\merge_outputs.ps1` to automatically speak narration after merging. Add this at the end of the merge script:

```powershell
# After writing merge output, speak narration
if ($narrationText -and $narrationText -ne "(none)") {
    Write-Host "Speaking narration..." -ForegroundColor Green
    & "C:\DnD\DnD_Cursor\scripts\speak_narration.ps1" -NarratorFile $narratorPath
}
```

## Advanced: Cloud TTS (Premium Quality)

For even better quality, you can use cloud-based TTS services:

### Azure Cognitive Services TTS

Very high quality, many voice options:

```powershell
# Requires: pip install azure-cognitiveservices-speech
# Requires: Azure subscription and API key
```

### ElevenLabs (Premium)

Extremely natural voices, but requires paid subscription.

## Troubleshooting

### Still Sounds Robotic

1. **Check if you have neural voices installed:**
   ```powershell
   .\scripts\list_voices.ps1
   ```

2. **Install Windows 11 neural voices** (see above)

3. **Use a specific neural voice:**
   ```powershell
   .\scripts\speak_narration.ps1 -SessionId "20260105234400" -Voice "Microsoft Aria Neural"
   ```

### No Neural Voices Available

- Ensure you're on Windows 11 (neural voices require Windows 11)
- Install neural voices via Settings or PowerShell (see above)
- On Windows 10, you'll only have standard voices (more robotic)

### Voice Not Found

- List available voices: `.\scripts\list_voices.ps1`
- Use partial name matching (e.g., `-Voice "Aria"` will match "Microsoft Aria Neural")

### No Sound Output

- Check system volume
- Verify audio device is connected
- Test with a simple TTS command:
  ```powershell
  Add-Type -AssemblyName System.Speech
  $speech = New-Object System.Speech.Synthesis.SpeechSynthesizer
  $speech.SelectVoice("Microsoft Aria Neural")
  $speech.Speak("Test")
  ```

## Notes

- Neural voices (Windows 11) sound much more natural than standard voices
- The script automatically prefers neural voices if available
- TTS runs synchronously - the script will wait for speech to complete
- For very long narrations, consider adding pauses or breaks
