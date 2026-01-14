#!/usr/bin/env python3
"""
Speak narration using Google Cloud Text-to-Speech (High Quality, Good Free Tier)

Requires: pip install google-cloud-texttospeech
Setup: https://cloud.google.com/text-to-speech/docs/quickstart
Free tier: 0-4 million characters/month
"""

import json
import sys
import argparse
import os
from pathlib import Path

try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False
    print("ERROR: google-cloud-texttospeech not installed")
    print("Install with: pip install google-cloud-texttospeech")
    sys.exit(1)

def speak_with_google_tts(text, voice_name="en-US-Neural2-F", output_file=None):
    """Use Google Cloud TTS to synthesize speech"""
    
    # Initialize client
    client = texttospeech.TextToSpeechClient()
    
    # Configure synthesis input
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    # Configure voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    
    # Configure audio
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,  # Normal speed
        pitch=0.0,  # Normal pitch
        volume_gain_db=0.0  # Normal volume
    )
    
    # Perform synthesis
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    # Save to file
    if not output_file:
        import tempfile
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
    
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
    
    return output_file

def play_audio_windows(file_path):
    """Play audio file on Windows"""
    try:
        import subprocess
        # Use PowerShell to play audio
        ps_command = f"""
        Add-Type -AssemblyName presentationCore
        `$mediaPlayer = New-Object system.windows.media.mediaplayer
        `$mediaPlayer.open([uri]'{file_path}')
        `$mediaPlayer.Play()
        while (`$mediaPlayer.Position -lt `$mediaPlayer.NaturalDuration.TimeSpan) {{
            Start-Sleep -Milliseconds 100
        }}
        `$mediaPlayer.Stop()
        """
        subprocess.run(["powershell", "-Command", ps_command], check=True)
    except Exception as e:
        print(f"Warning: Could not play audio automatically: {e}")
        print(f"Audio saved to: {file_path}")
        print("Please play it manually.")

def main():
    parser = argparse.ArgumentParser(description="Speak narration using Google Cloud TTS")
    parser.add_argument("session_id", nargs="?", help="Session ID")
    parser.add_argument("--file", help="Direct path to narrator JSON file")
    parser.add_argument("--voice", default="en-US-Neural2-F", help="Voice name (default: en-US-Neural2-F)")
    
    args = parser.parse_args()
    
    # Determine file path
    if args.file:
        narrator_path = Path(args.file)
    elif args.session_id:
        narrator_path = Path(f"C:/DnD/.coord-{args.session_id}/dnd_out_NARRATOR.json")
    else:
        print("ERROR: Must provide either session_id or --file")
        sys.exit(1)
    
    # Check if file exists
    if not narrator_path.exists():
        print(f"ERROR: Narrator file not found: {narrator_path}")
        sys.exit(1)
    
    # Read and parse JSON
    try:
        with open(narrator_path, 'r', encoding='utf-8') as f:
            narrator_data = json.load(f)
        
        narration_text = narrator_data.get('narration', '')
        
        if not narration_text or narration_text == "(none)":
            print("No narration to speak")
            sys.exit(0)
        
        print("Speaking narration with Google Cloud TTS...")
        print(f"\n{narration_text}\n")
        
        # Synthesize speech
        print("Synthesizing speech...")
        audio_file = speak_with_google_tts(narration_text, args.voice)
        
        # Play audio
        print("Playing audio...")
        play_audio_windows(audio_file)
        
        # Cleanup
        try:
            os.remove(audio_file)
        except:
            pass
        
        print("Done.")
        
    except Exception as e:
        print(f"ERROR: Failed to process narration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
