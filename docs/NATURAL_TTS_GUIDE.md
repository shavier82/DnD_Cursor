# Natural-Sounding TTS Guide

This guide explains how to get the most natural-sounding text-to-speech for D&D narration.

## Quick Solutions

### Option 1: Enhanced Windows TTS (Free, Better)

Use the enhanced script with optimized settings:

```powershell
.\scripts\speak_narration_enhanced.ps1 -SessionId "20260105234400"
```

**Improvements:**
- Automatically uses neural voices
- Optimized speech rate (-2 for natural pacing)
- Adds pauses for better flow
- Better voice selection

### Option 2: Azure Cognitive Services TTS (Premium Quality, Free Tier Available)

Azure TTS has very natural voices. Free tier: 500,000 characters/month.

**Setup:**

1. **Get Azure Speech Service:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Create a "Speech Services" resource
   - Copy the **Key** and **Region** (e.g., "eastus")

2. **Set Environment Variables:**
   ```powershell
   $env:AZURE_SPEECH_KEY = "your-key-here"
   $env:AZURE_SPEECH_REGION = "eastus"
   ```

   Or set permanently:
   ```powershell
   [System.Environment]::SetEnvironmentVariable("AZURE_SPEECH_KEY", "your-key", "User")
   [System.Environment]::SetEnvironmentVariable("AZURE_SPEECH_REGION", "eastus", "User")
   ```

3. **Install Azure Speech SDK:**
   ```powershell
   Install-Module -Name Azure.CognitiveServices.Speech -Force -Scope CurrentUser
   ```

4. **Use Azure TTS:**
   ```powershell
   .\scripts\speak_narration_enhanced.ps1 -SessionId "20260105234400" -UseAzure
   ```

**Best Azure Voices for Narration:**
- `en-US-AriaNeural` (female, very natural)
- `en-US-JennyNeural` (female, natural)
- `en-US-GuyNeural` (male, natural)
- `en-US-DavisNeural` (male, deep)

### Option 3: ElevenLabs (Premium, Extremely Natural)

ElevenLabs has the most natural voices but requires a paid subscription ($5/month+).

**Setup:**
1. Sign up at [ElevenLabs](https://elevenlabs.io)
2. Get API key
3. Use their API or web interface

## Voice Quality Comparison

| Service | Quality | Cost | Naturalness |
|---------|---------|------|-------------|
| Windows Standard | Low | Free | Robotic |
| Windows Neural | Medium | Free | Good |
| Azure Neural | High | Free tier | Very Natural |
| ElevenLabs | Highest | $5+/month | Extremely Natural |

## Tips for More Natural Sound

### 1. Use Neural Voices
Always prefer neural voices over standard voices - they use AI and sound much more human.

### 2. Adjust Speech Rate
- Too fast: Sounds rushed
- Too slow: Sounds robotic
- Optimal: -2 to 0 (slightly slower than default)

### 3. Add Pauses
Natural speech has pauses. The enhanced script adds pauses after sentences.

### 4. Choose the Right Voice
- **Female voices** (Aria, Jenny) often work better for narration
- **Male voices** (Guy, Davis) can work for dramatic moments
- Test different voices to find your preference

### 5. Use SSML (Azure/Cloud TTS)
SSML allows fine control over prosody, pauses, and emphasis:

```xml
<speak>
    <prosody rate="medium" pitch="medium">
        Your narration text here.
    </prosody>
</speak>
```

## Recommended Setup

**For Best Free Quality:**
1. Install Windows 11 neural voices
2. Use `speak_narration_enhanced.ps1`
3. Consider Azure TTS (free tier) for even better quality

**For Premium Quality:**
1. Set up Azure Cognitive Services TTS
2. Use `speak_narration_enhanced.ps1 -UseAzure`
3. Or use ElevenLabs for the absolute best quality

## Troubleshooting

### Still Sounds Robotic
- Ensure you're using neural voices (check with `list_voices.ps1`)
- Try Azure TTS for better quality
- Adjust speech rate (try -2 to -1)

### Azure TTS Not Working
- Check environment variables are set
- Verify Azure Speech Service is created
- Check key and region are correct

### Voice Too Fast/Slow
- Adjust `Rate` parameter in script
- Range: -10 (slowest) to 10 (fastest)
- Recommended: -2 to 0 for narration
































