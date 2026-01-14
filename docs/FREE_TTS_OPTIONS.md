# Free TTS Options (No Billing Required)

If you don't want to set up a billing account, here are free alternatives:

## 1. **ElevenLabs** ⭐ Best Free Option
- **Free Tier**: 10,000 characters/month (no billing required)
- **Quality**: ⭐⭐⭐⭐⭐ (Best quality)
- **Setup**: Just need API key (free account)
- **Script**: `speak_narration_elevenlabs.ps1`

**Setup:**
1. Sign up at https://elevenlabs.io (free)
2. Get API key from dashboard
3. Set: `$env:ELEVENLABS_API_KEY = "your-key"`
4. Use: `.\scripts\speak_narration_elevenlabs.ps1 -SessionId "20260105234400"`

## 2. **Play.ht** 
- **Free Tier**: 2,500 words/month (no billing required)
- **Quality**: ⭐⭐⭐⭐ (Very good)
- **Setup**: Free account + API key
- **Script**: `speak_narration_playht.ps1`

**Setup:**
1. Sign up at https://play.ht (free)
2. Get User ID and API key
3. Set environment variables
4. Use the script

## 3. **Windows Neural Voices** (Already Installed)
- **Free**: Unlimited (Windows 11)
- **Quality**: ⭐⭐⭐ (Good with neural voices)
- **No Setup**: Already available
- **Script**: `speak_narration.ps1` (updated version)

**Usage:**
```powershell
.\scripts\speak_narration.ps1 -SessionId "20260105234400"
```

## Recommendation

**For best free quality without billing:**
- **ElevenLabs** - 10K chars/month, excellent quality, no billing needed

**For unlimited free (lower quality):**
- **Windows Neural Voices** - Already installed, works well with neural voices

## Google Cloud TTS (If You Want to Set Up Billing)

**Note**: Billing account is required BUT:
- Free tier: 0-4 million characters/month
- You won't be charged until you exceed free tier
- You can set billing alerts
- Very safe - Google won't charge you for free tier usage

If you want to proceed with Google Cloud:
1. Add billing account (credit card required, but won't be charged for free tier)
2. Set up billing alerts to $0.01 (so you get notified if you exceed free tier)
3. You'll get 4M characters/month free


















