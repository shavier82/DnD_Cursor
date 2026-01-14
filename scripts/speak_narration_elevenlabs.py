#!/usr/bin/env python3
"""
Speak narration using ElevenLabs AI TTS (Premium Quality, Free Tier)
More reliable audio playback than PowerShell version
"""

import json
import sys
import os
import tempfile
from pathlib import Path
import requests

def play_audio(file_path, background=False):
    """Play audio file using pygame (most reliable on Windows)
    
    Args:
        file_path: Path to audio file
        background: If True, play in background without waiting (default: False)
    """
    if background:
        # Play in background and return immediately
        try:
            import subprocess
            import sys
            # Use subprocess to play in background without blocking
            if sys.platform == "win32":
                subprocess.Popen(["powershell", "-Command", f"Start-Process '{file_path}'"], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen(["python", "-c", f"import pygame; pygame.mixer.init(); pygame.mixer.music.load('{file_path}'); pygame.mixer.music.play(); import time; time.sleep(30)"])
            return True
        except:
            # Fallback: just start the file
            try:
                os.startfile(file_path)
                return True
            except:
                return False
    else:
        # Original blocking behavior
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.quit()
            return True
        except ImportError:
            print("pygame not installed, trying alternative...")
            pass
        
        # Fallback: use Windows default player
        try:
            import subprocess
            subprocess.run(["powershell", "-Command", f"Start-Process '{file_path}' -Wait"], check=True)
            return True
        except:
            pass
        
        # Last resort: open with default app
        try:
            os.startfile(file_path)
            input("Press Enter when audio finishes playing...")
            return True
        except:
            return False

def speak_with_elevenlabs(text, api_key, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """Synthesize speech using ElevenLabs API"""
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2",  # Free tier compatible
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    # Only print if not in background mode (checking via call stack would be complex, so we'll keep it minimal)
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code != 200:
        error_msg = response.json().get('detail', {}).get('message', response.text)
        print(f"ERROR: {error_msg}")
        
        if 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
            print("\nYou've reached your free tier limit (10,000 characters/month)")
            print("Upgrade at https://elevenlabs.io or wait for monthly reset")
        
        return None
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_file.write(response.content)
    temp_file.close()
    
    return temp_file.name

def main():
    # Get API key
    api_key = os.environ.get('ELEVENLABS_API_KEY')
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY environment variable not set")
        print("\nSetup (FREE, no billing required):")
        print("1. Sign up at https://elevenlabs.io (free account)")
        print("2. Go to Profile -> API Key")
        print("3. Copy your API key")
        print("4. Set it with: $env:ELEVENLABS_API_KEY = 'your-key-here'")
        print("\nFree tier: 10,000 characters/month (no billing account needed!)")
        sys.exit(1)
    
    # Check for background flag
    background = "--background" in sys.argv or "-b" in sys.argv
    
    # Get session ID or file path
    args = [a for a in sys.argv[1:] if a not in ["--background", "-b"]]
    if len(args) < 1:
        print("Usage: python speak_narration_elevenlabs.py <session_id> [--background]")
        print("   or: python speak_narration_elevenlabs.py --file <path> [--background]")
        sys.exit(1)
    
    if args[0] == "--file":
        narrator_path = Path(args[1])
    else:
        session_id = args[0]
        narrator_path = Path(f"C:/DnD/.coord-{session_id}/dnd_out_NARRATOR.json")
    
    # Check if file exists
    if not narrator_path.exists():
        print(f"ERROR: Narrator file not found: {narrator_path}")
        sys.exit(1)
    
    # Read narration
    with open(narrator_path, 'r', encoding='utf-8-sig') as f:
        narrator_data = json.load(f)
    
    narration_text = narrator_data.get('narration', '')
    
    if not narration_text or narration_text == "(none)":
        print("No narration to speak")
        sys.exit(0)
    
    # Check character count
    char_count = len(narration_text)
    if char_count > 10000:
        if not background:
            print(f"WARNING: Narration is {char_count} characters (free tier limit: 10,000)")
            print("Truncating to first 10,000 characters...")
        narration_text = narration_text[:10000]
        char_count = 10000
    
    if not background:
        print("Speaking narration with ElevenLabs (Premium Quality)...")
        print(f"Characters: {char_count} / 10,000 (free tier)")
        print(f"\n{narration_text}\n")
    
    # Synthesize speech
    audio_file = speak_with_elevenlabs(narration_text, api_key)
    
    if not audio_file:
        sys.exit(1)
    
    # Play audio (background or blocking)
    if background:
        # Play in background and return immediately (non-blocking)
        play_audio(audio_file, background=True)
        # Don't delete file immediately - let background process handle it
        # File will be cleaned up automatically after playback
    else:
        # Original blocking behavior
        print("Playing audio...")
        success = play_audio(audio_file, background=False)
        
        # Cleanup
        try:
            os.remove(audio_file)
        except:
            pass
        
        if success:
            print("Done.")
        else:
            print("WARNING: Could not play audio automatically")
            print(f"Audio was saved to: {audio_file}")

if __name__ == "__main__":
    main()

