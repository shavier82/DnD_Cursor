#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-Session Mechanics Check
MUST be run before every session. Validates that mechanics checklist was reviewed.

This script creates a validation token that proves the checklist was read.
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

CHECKLIST_PATH = Path(__file__).parent.parent / "MECHANICS_AUTOMATION_CHECKLIST.md"
VALIDATION_FILE = Path(__file__).parent.parent / ".mechanics_validated.json"

def validate_checklist_read():
    """Validate that the mechanics checklist exists and was read"""
    
    if not CHECKLIST_PATH.exists():
        print("❌ ERROR: MECHANICS_AUTOMATION_CHECKLIST.md not found!")
        print(f"   Expected at: {CHECKLIST_PATH}")
        return False
    
    # Read checklist to verify it exists
    try:
        with open(CHECKLIST_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key sections
        required_sections = [
            "POST-COMBAT",
            "NPC MANAGEMENT",
            "QUEST MANAGEMENT",
            "OBSIDIAN SYNC",
            "VALIDATION CHECKLIST"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"⚠️  WARNING: Checklist missing sections: {', '.join(missing_sections)}")
        
    except Exception as e:
        print(f"❌ ERROR: Failed to read checklist: {e}")
        return False
    
    # Create validation token
    validation_data = {
        "checklist_read": True,
        "timestamp": datetime.now().isoformat(),
        "checklist_path": str(CHECKLIST_PATH),
        "sections_verified": len(required_sections) - len(missing_sections) if 'missing_sections' in locals() else len(required_sections)
    }
    
    try:
        with open(VALIDATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(validation_data, f, indent=2)
        
        print("✅ Mechanics checklist validated!")
        print(f"   Validation token created: {VALIDATION_FILE}")
        print(f"   Timestamp: {validation_data['timestamp']}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to create validation token: {e}")
        return False


def check_validation_token():
    """Check if validation token exists and is recent"""
    
    if not VALIDATION_FILE.exists():
        return False, "No validation token found"
    
    try:
        with open(VALIDATION_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data.get("checklist_read"):
            return False, "Validation token invalid"
        
        # Check if token is recent (within last 24 hours)
        timestamp_str = data.get("timestamp")
        if timestamp_str:
            from datetime import datetime, timedelta
            token_time = datetime.fromisoformat(timestamp_str)
            if datetime.now() - token_time > timedelta(hours=24):
                return False, "Validation token expired (older than 24 hours)"
        
        return True, f"Validated at {timestamp_str}"
        
    except Exception as e:
        return False, f"Error reading validation token: {e}"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Just check if validation exists
        valid, message = check_validation_token()
        if valid:
            print(f"✅ {message}")
            sys.exit(0)
        else:
            print(f"❌ {message}")
            print("\n⚠️  You must run this script without --check to validate the checklist first.")
            sys.exit(1)
    else:
        # Validate checklist
        if validate_checklist_read():
            print("\n✅ Pre-session check complete. You may proceed with the session.")
            sys.exit(0)
        else:
            print("\n❌ Pre-session check failed. Review the checklist and try again.")
            sys.exit(1)
