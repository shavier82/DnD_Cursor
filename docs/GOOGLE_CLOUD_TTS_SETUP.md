# Google Cloud Text-to-Speech Setup Guide

This guide will help you set up Google Cloud TTS for natural-sounding narration.

## Why Google Cloud TTS?

- **Excellent Quality**: Neural2 voices sound very natural
- **Great Free Tier**: 0-4 million characters/month FREE
- **Many Voices**: 220+ voices in 40+ languages
- **Reliable**: Enterprise-grade service

## Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it (e.g., "DnD-TTS")
4. Click "Create"

### 2. Enable Text-to-Speech API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Cloud Text-to-Speech API"
3. Click on it and click "Enable"

### 3. Create Service Account

1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name it (e.g., "dnd-tts-service")
4. Click "Create and Continue"
5. Grant role: "Cloud Text-to-Speech API User"
6. Click "Continue" → "Done"

### 4. Create and Download Key

1. Click on your service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON" format
5. Download the JSON file
6. **Save it securely** (e.g., `C:\DnD\keys\google-tts-key.json`)

### 5. Set Environment Variable

```powershell
# Set for current session
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\DnD\keys\google-tts-key.json"

# Or set permanently (User level)
[System.Environment]::SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", "C:\DnD\keys\google-tts-key.json", "User")
```

### 6. Install Python SDK

```powershell
pip install google-cloud-texttospeech
```

## Usage

### Basic Usage

```powershell
python C:\DnD\DnD_Cursor\scripts\speak_narration_google.py 20260105234400
```

### With Custom Voice

```powershell
python C:\DnD\DnD_Cursor\scripts\speak_narration_google.py 20260105234400 --voice "en-US-Neural2-M"
```

### With Direct File Path

```powershell
python C:\DnD\DnD_Cursor\scripts\speak_narration_google.py --file "C:\DnD\.coord-20260105234400\dnd_out_NARRATOR.json"
```

## Recommended Voices for Narration

### Female Voices (Recommended)
- `en-US-Neural2-F` - Natural female voice (default)
- `en-US-Neural2-C` - Calm female voice
- `en-US-Neural2-D` - Warm female voice
- `en-US-Neural2-E` - Energetic female voice

### Male Voices
- `en-US-Neural2-M` - Natural male voice
- `en-US-Neural2-A` - Deep male voice
- `en-US-Neural2-B` - Warm male voice
- `en-US-Neural2-G` - Gentle male voice

### List All Available Voices

You can list all voices using the Google Cloud Console or API.

## Pricing

- **Free Tier**: 0-4 million characters/month
- **After Free Tier**: $4.00 per 1 million characters
- **Very affordable** for D&D narration (most sessions use < 10,000 characters)

## Troubleshooting

### "Credentials not found"
- Check that `GOOGLE_APPLICATION_CREDENTIALS` is set
- Verify the JSON file path is correct
- Ensure the JSON file is valid

### "API not enabled"
- Go to Google Cloud Console
- Enable "Cloud Text-to-Speech API"

### "Permission denied"
- Ensure service account has "Cloud Text-to-Speech API User" role
- Check that the JSON key file is from the correct service account

### "Module not found"
- Install: `pip install google-cloud-texttospeech`
- Ensure Python 3.7+ is being used

## Example Session

```powershell
# 1. Set credentials
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\DnD\keys\google-tts-key.json"

# 2. Test with a session
python C:\DnD\DnD_Cursor\scripts\speak_narration_google.py 20260105234400

# Output:
# Speaking narration with Google Cloud TTS...
# [narration text]
# Synthesizing speech...
# Playing audio...
# Done.
```

## Next Steps

Once set up, you can:
- Use it manually after each turn
- Integrate it into the merge script for automatic narration
- Try different voices to find your favorite

Enjoy natural-sounding narration!


















