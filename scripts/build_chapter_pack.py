#!/usr/bin/env python3
"""
Build Chapter Pack
Compiles raw chapter .txt into chapter_pack_<n>.json
"""

import json
import sys
import os
import time
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Build chapter pack from raw .txt')
    parser.add_argument('--chapter', type=int, required=True, help='Chapter number')
    parser.add_argument('--skip-raw-text', action='store_true', help='Skip embedding raw text (use path reference)')
    args = parser.parse_args()
    
    start_time = time.time()
    print(f"[build] Starting chapter pack build for Chapter {args.chapter}")
    
    # Load paths config
    script_dir = Path(__file__).parent
    config_path = script_dir.parent / "config" / "paths.json"
    
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    print("[build] Loading config...")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    chapters_dir = Path(config['chapters_dir'])
    packs_dir = Path(config['packs_dir'])
    elapsed = (time.time() - start_time) * 1000
    print(f"[build] Config loaded in {elapsed:.0f}ms")
    
    # Ensure packs directory exists
    packs_dir.mkdir(parents=True, exist_ok=True)
    
    # Find chapter file (case-insensitive)
    print("[build] Locating chapter file...")
    patterns = [
        f"chapter_{args.chapter:02d}.txt",
        f"chapter_{args.chapter}.txt",
        f"Chapter_{args.chapter:02d}.txt",
        f"Chapter_{args.chapter}.txt"
    ]
    
    chapter_file = None
    for pattern in patterns:
        test_path = chapters_dir / pattern
        if test_path.exists():
            chapter_file = test_path
            break
    
    # Case-insensitive search if not found
    if not chapter_file:
        for txt_file in chapters_dir.glob("*.txt"):
            name_lower = txt_file.name.lower()
            if name_lower in [p.lower() for p in patterns]:
                chapter_file = txt_file
                break
    
    if not chapter_file:
        print(f"ERROR: Chapter file not found. Tried: {', '.join(patterns)}", file=sys.stderr)
        sys.exit(1)
    
    print(f"[build] Using chapter file: {chapter_file}")
    
    # Read raw chapter text
    raw_text = None
    raw_text_path = None
    
    if not args.skip_raw_text:
        print("[build] Reading raw text...")
        read_start = time.time()
        with open(chapter_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        read_elapsed = (time.time() - read_start) * 1000
        print(f"[build] Read {len(raw_text)} chars in {read_elapsed:.0f}ms")
    else:
        raw_text_path = str(chapter_file)
        print("[build] Skipping raw text embedding (using path reference)")
    
    # Build chapter pack
    print("[build] Building pack structure...")
    chapter_pack = {
        "pack_type": "chapter_pack",
        "pack_version": "1.0",
        "source": "Mines of Phandelver and Below",
        "chapter": args.chapter,
        "cards": []
    }
    
    if args.skip_raw_text:
        chapter_pack["raw_text_path"] = raw_text_path
    else:
        chapter_pack["raw_text"] = raw_text
    
    # Serialize JSON
    print("[build] Serializing JSON...")
    serialize_start = time.time()
    chapter_pack_json = json.dumps(chapter_pack, indent=2, ensure_ascii=False)
    serialize_elapsed = (time.time() - serialize_start) * 1000
    print(f"[build] Serialized in {serialize_elapsed:.0f}ms")
    
    # Write output
    output_path = packs_dir / f"chapter_pack_{args.chapter}.json"
    print("[build] Writing output...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(chapter_pack_json)
    
    total_elapsed = (time.time() - start_time) * 1000
    print(f"[build] DONE: {output_path} ({total_elapsed:.0f}ms total)")

if __name__ == "__main__":
    main()

