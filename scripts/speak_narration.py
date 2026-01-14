#!/usr/bin/env python3
"""
Speak narration from NARRATOR agent output using Windows TTS or pyttsx3

Usage:
    python speak_narration.py <session_id>
    python speak_narration.py --file "C:\DnD\.coord-20260105234400\dnd_out_NARRATOR.json"
"""

import json
import sys
import argparse
from pathlib import Path

def speak_with_pyttsx3(text):
    """Use pyttsx3 library for cross-platform TTS"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Optional: Set voice properties
        # voices = engine.getProperty('voices')
        # engine.setProperty('voice', voices[0].id)  # Use first available voice
        # engine.setProperty('rate', 150)  # Speed (words per minute)
        # engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        engine.say(text)
        engine.runAndWait()
        return True
    except ImportError:
        print("ERROR: pyttsx3 not installed. Install with: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"ERROR: TTS failed: {e}")
        return False

def speak_with_windows_sapi(text):
    """Use Windows SAPI directly (Windows only)"""
    try:
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(text)
        return True
    except ImportError:
        print("ERROR: pywin32 not installed. Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"ERROR: Windows SAPI failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Speak narration from NARRATOR output")
    parser.add_argument("session_id", nargs="?", help="Session ID (e.g., 20260105234400)")
    parser.add_argument("--file", help="Direct path to narrator JSON file")
    
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
        
        print("Speaking narration...")
        print(f"\n{narration_text}\n")
        
        # Try different TTS methods
        success = False
        
        # Try Windows SAPI first (if on Windows)
        if sys.platform == "win32":
            success = speak_with_windows_sapi(narration_text)
        
        # Fall back to pyttsx3 if SAPI failed or not on Windows
        if not success:
            success = speak_with_pyttsx3(narration_text)
        
        if success:
            print("Done.")
        else:
            print("ERROR: Could not speak narration. Install pyttsx3: pip install pyttsx3")
            sys.exit(1)
            
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to process narration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


















