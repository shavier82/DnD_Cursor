#!/usr/bin/env python3
"""Test script to run viewer and capture errors"""
import sys
import traceback

try:
    from view_battlemap import BattlemapViewer
    import json
    from pathlib import Path
    
    positions_file = Path("combat_positions_t18.json")
    if not positions_file.exists():
        print(f"ERROR: File not found: {positions_file}")
        sys.exit(1)
    
    print(f"Starting viewer with file: {positions_file}")
    viewer = BattlemapViewer(str(positions_file), update_interval=1.0)
    print("Viewer created, starting main loop...")
    viewer.run()
    
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)
