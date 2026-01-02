#!/usr/bin/env python3
"""
Build Chapter Pack
Compiles raw chapter .txt into PLAY-safe chapter_pack_<n>.json with cards
"""

import json
import sys
import os
import time
import argparse
import re
from pathlib import Path
from datetime import datetime

def extract_cards_from_text(text, chapter_num):
    """Extract structured cards from chapter text"""
    cards = []
    
    # Pattern for location headers (H1, H2, etc.)
    location_pattern = r'^H(\d+):\s+(.+?)$'
    # Pattern for boxed text (usually indented or in quotes)
    boxed_pattern = r'(?:^|\n)(?:When the characters|Read|You\'ve|This|The|A|An)\s+[^\.]+\.'
    
    lines = text.split('\n')
    current_location = None
    current_boxed = []
    
    for i, line in enumerate(lines):
        # Match location headers (H1: Cave Mouth, etc.)
        loc_match = re.match(location_pattern, line.strip())
        if loc_match:
            # Save previous location if exists
            if current_location:
                card = {
                    "id": f"ch{chapter_num}_h{current_location['num']}_{current_location['id']}",
                    "title": current_location['title'],
                    "type": "location",
                    "boxed_text": "\n".join(current_boxed).strip() if current_boxed else "",
                    "mechanics": current_location.get('mechanics', ""),
                    "references": f"Chapter {chapter_num}, {current_location['title']}"
                }
                cards.append(card)
            
            loc_num = loc_match.group(1)
            loc_title = loc_match.group(2)
            loc_id = re.sub(r'[^a-z0-9]+', '_', loc_title.lower()).strip('_')
            
            current_location = {
                "num": loc_num,
                "title": loc_title,
                "id": loc_id,
                "mechanics": ""
            }
            current_boxed = []
            continue
        
        # Collect boxed text (read-aloud sections)
        if current_location and line.strip().startswith(('You', 'The', 'This', 'A', 'An', 'When', 'Read')):
            if len(line.strip()) > 20 and len(line.strip()) < 500:
                current_boxed.append(line.strip())
        
        # Extract mechanics (DCs, checks, etc.)
        if current_location:
            dc_match = re.search(r'DC\s+(\d+)', line)
            check_match = re.search(r'(?:Wisdom|Dexterity|Strength|Constitution|Intelligence|Charisma)\s*\(([^)]+)\)', line)
            if dc_match or check_match:
                if not current_location.get('mechanics'):
                    current_location['mechanics'] = line.strip()
    
    # Save last location
    if current_location:
        card = {
            "id": f"ch{chapter_num}_h{current_location['num']}_{current_location['id']}",
            "title": current_location['title'],
            "type": "location",
            "boxed_text": "\n".join(current_boxed).strip() if current_boxed else "",
            "mechanics": current_location.get('mechanics', ""),
            "references": f"Chapter {chapter_num}, {current_location['title']}"
        }
        cards.append(card)
    
    # Extract scene/encounter cards
    scene_patterns = [
        (r'Goblin Ambush', 'scene', 'ch1_goblin_ambush'),
        (r'Snare', 'trap', 'ch1_snare'),
        (r'Pit Trap', 'trap', 'ch1_pit_trap'),
        (r'Cragmaw Hideout', 'location', 'ch1_cragmaw_hideout'),
    ]
    
    for pattern, card_type, card_id in scene_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            # Extract nearby boxed text
            pattern_pos = text.find(pattern)
            if pattern_pos > 0:
                context = text[max(0, pattern_pos-200):pattern_pos+500]
                boxed = re.search(r'([^\.]+\.\s*){1,3}', context)
                boxed_text = boxed.group(0).strip() if boxed else ""
                
                card = {
                    "id": card_id,
                    "title": pattern,
                    "type": card_type,
                    "boxed_text": boxed_text[:300],  # Limit length
                    "mechanics": "",
                    "references": f"Chapter {chapter_num}"
                }
                # Only add if not duplicate
                if not any(c['id'] == card_id for c in cards):
                    cards.append(card)
    
    return cards

def find_chapter_file(chapters_dir, chapter_num):
    """Find chapter file with case-insensitive matching"""
    patterns = [
        f"chapter_{chapter_num:02d}.txt",
        f"chapter_{chapter_num}.txt",
        f"Chapter_{chapter_num:02d}.txt",
        f"Chapter_{chapter_num}.txt",
        f"CHAPTER_{chapter_num:02d}.txt",
        f"CHAPTER_{chapter_num}.txt",
    ]
    
    # Try exact matches first
    for pattern in patterns:
        test_path = chapters_dir / pattern
        if test_path.exists():
            return test_path
    
    # Case-insensitive search
    for txt_file in chapters_dir.glob("*.txt"):
        name_lower = txt_file.name.lower()
        # Match chapter_<num>.txt or chapter_<num>_<anything>.txt
        match = re.match(r'^chapter_0?(\d+)', name_lower)
        if match and int(match.group(1)) == chapter_num:
            return txt_file
    
    return None

def main():
    parser = argparse.ArgumentParser(description='Build chapter pack from raw .txt')
    parser.add_argument('--chapter', type=int, required=True, help='Chapter number')
    args = parser.parse_args()
    
    start_time = time.time()
    log_lines = []
    
    def log(msg):
        log_lines.append(msg)
        print(msg)
    
    log(f"[build] Starting chapter pack build for Chapter {args.chapter}")
    
    # Load paths config
    script_dir = Path(__file__).parent
    config_path = script_dir.parent / "config" / "paths.json"
    
    if not config_path.exists():
        log(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)
    
    log("[build] Loading config...")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    chapters_dir = Path(config['chapters_dir'])
    packs_dir = Path(config['packs_dir'])
    elapsed = (time.time() - start_time) * 1000
    log(f"[build] Config loaded in {elapsed:.0f}ms")
    
    # Ensure packs directory and logs subdirectory exist
    packs_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = packs_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Find chapter file
    log("[build] Locating chapter file...")
    chapter_file = find_chapter_file(chapters_dir, args.chapter)
    
    if not chapter_file:
        log(f"ERROR: Chapter file not found for chapter {args.chapter}")
        sys.exit(1)
    
    log(f"[build] Using chapter file: {chapter_file}")
    
    # Read raw chapter text
    log("[build] Reading raw text...")
    read_start = time.time()
    with open(chapter_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    read_elapsed = (time.time() - read_start) * 1000
    log(f"[build] Read {len(raw_text)} chars in {read_elapsed:.0f}ms")
    
    # Extract cards
    log("[build] Extracting cards...")
    extract_start = time.time()
    cards = extract_cards_from_text(raw_text, args.chapter)
    extract_elapsed = (time.time() - extract_start) * 1000
    log(f"[build] Extracted {len(cards)} cards in {extract_elapsed:.0f}ms")
    
    # Build chapter pack (PLAY-safe: NO raw_text)
    log("[build] Building pack structure...")
    chapter_pack = {
        "pack_type": "chapter_pack",
        "pack_version": "1.0",
        "source": "Mines of Phandelver and Below",
        "chapter": args.chapter,
        "cards": cards
    }
    
    # Serialize JSON
    log("[build] Serializing JSON...")
    serialize_start = time.time()
    chapter_pack_json = json.dumps(chapter_pack, indent=2, ensure_ascii=False)
    serialize_elapsed = (time.time() - serialize_start) * 1000
    pack_size_kb = len(chapter_pack_json.encode('utf-8')) / 1024
    log(f"[build] Serialized {pack_size_kb:.1f}KB in {serialize_elapsed:.0f}ms")
    
    # Write output
    output_path = packs_dir / f"chapter_pack_{args.chapter}.json"
    log("[build] Writing output...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(chapter_pack_json)
    
    # Write verbose log
    log_path = logs_dir / f"build_chapter_pack_ch{args.chapter}.log"
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Build log for Chapter {args.chapter}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Source file: {chapter_file}\n")
        f.write(f"Output file: {output_path}\n")
        f.write(f"Cards extracted: {len(cards)}\n")
        f.write(f"Pack size: {pack_size_kb:.1f}KB\n")
        f.write(f"\n--- Build Steps ---\n")
        f.write("\n".join(log_lines))
        f.write(f"\n\n--- Extracted Cards ---\n")
        for card in cards:
            f.write(f"\n{card['id']}: {card['title']} ({card['type']})\n")
    
    total_elapsed = (time.time() - start_time) * 1000
    log(f"[build] DONE: {output_path} ({total_elapsed:.0f}ms total, {pack_size_kb:.1f}KB)")
    log(f"[build] Log: {log_path}")

if __name__ == "__main__":
    main()
