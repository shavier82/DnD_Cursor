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
from typing import List, Dict, Any

# Heading detection (broad - structure-first approach)
HEADING_PATTERNS = [
    # Keyed areas: H1: Cave Mouth / A3: Something / W12 - Whatever
    re.compile(r"^\s*([A-Z]{1,3}\d{1,3})\s*[:\-]\s*(.+?)\s*$"),
    # "Area H1: ..." / "Area H1 - ..."
    re.compile(r"^\s*Area\s+([A-Z]{1,3}\d{1,3})\s*[:\-]\s*(.+?)\s*$", re.IGNORECASE),
    # Chapter/part style headers: "Running This Chapter", "What's Next?", etc.
    re.compile(r"^\s*(Running This Chapter|The\s+Road\s+to\s+.+|What(?:'|')?s Next\??|General Features)\s*$", re.IGNORECASE),
    # Subsection headers often used everywhere: Development / Treasure / Roleplaying / etc.
    re.compile(r"^\s*(Development|Treasure|Roleplaying|Tactics|Creatures|Hazards|Visibility|Light|Sound|Ceilings|Doors|Endless Void|Briny Maze|Cardinal Directions|Movement|Illumination|Air)\s*\.?\s*$", re.IGNORECASE),
]

# "Looks like a title line" fallback:
TITLEISH = re.compile(r"^[A-Z][A-Za-z0-9'(),:\-\s]{2,90}$")

# DC/roll extraction patterns
DC_CHECK = re.compile(r"\bDC\s+(\d+)\s+([A-Za-z]+)\s*\(([^)]+)\)\s+check\b", re.IGNORECASE)
DC_SAVE = re.compile(r"\bDC\s+(\d+)\s+([A-Za-z]+)\s+saving throw\b", re.IGNORECASE)

def slugify(s: str) -> str:
    """Convert string to URL-safe slug"""
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s[:60] if s else "section"

def extract_gates(text: str) -> List[Dict[str, Any]]:
    """Extract DC checks and saves from text"""
    gates: List[Dict[str, Any]] = []
    for m in DC_CHECK.finditer(text):
        dc, ability, skill = int(m.group(1)), m.group(2), m.group(3)
        gates.append({
            "type": "check",
            "dc": dc,
            "ability": ability.title(),
            "skill": skill.strip(),
            "note": ""
        })
    for m in DC_SAVE.finditer(text):
        dc, ability = int(m.group(1)), m.group(2)
        gates.append({
            "type": "save",
            "dc": dc,
            "ability": ability.title(),
            "skill": "",
            "note": ""
        })
    return gates

def split_into_sections(raw: str) -> List[Dict[str, str]]:
    """Split chapter text into sections based on heading patterns (structure-first)"""
    lines = raw.replace("\r\n", "\n").split("\n")
    marks = []

    def add_mark(i: int, title: str):
        marks.append((i, title.strip()))

    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s:
            continue

        matched = False
        for pat in HEADING_PATTERNS:
            m = pat.match(ln)
            if m:
                if m.lastindex and m.lastindex >= 2:
                    add_mark(i, f"{m.group(1)}: {m.group(2)}")
                else:
                    add_mark(i, m.group(1))
                matched = True
                break
        if matched:
            continue

        # Title-ish fallback only if surrounded by blank lines (reduces false positives)
        if TITLEISH.match(s):
            prev_blank = (i == 0) or (not lines[i - 1].strip())
            next_blank = (i >= len(lines) - 1) or (not lines[i + 1].strip())
            if prev_blank and next_blank:
                add_mark(i, s)

    # If no headings detected, single section
    if not marks:
        return [{"title": "Chapter Overview", "body": raw.strip()}]

    # Dedup + sort
    marks = sorted(set(marks), key=lambda x: x[0])

    sections = []
    for idx, (start_i, title) in enumerate(marks):
        end_i = marks[idx + 1][0] if idx + 1 < len(marks) else len(lines)
        body = "\n".join(lines[start_i + 1:end_i]).strip()
        if body:
            sections.append({"title": title, "body": body})

    return sections or [{"title": "Chapter Overview", "body": raw.strip()}]

def build_cards(chapter_num: int, raw: str) -> List[Dict[str, Any]]:
    """Build cards from chapter text (structure-first, chapter-correct IDs)"""
    sections = split_into_sections(raw)
    cards: List[Dict[str, Any]] = []

    for idx, sec in enumerate(sections, start=1):
        title = sec["title"]
        body = sec["body"]
        gates = extract_gates(body)

        # Determine card type based on title pattern
        if re.match(r"^[A-Z]{1,3}\d{1,3}:", title):
            kind = "location"
        else:
            kind = "section"

        # CRITICAL: Use chapter_num parameter, never hardcode
        card_id = f"ch{chapter_num:02d}_{slugify(title)}_{idx:03d}"

        # Limit body text to prevent huge cards
        body_limited = body[:4000] if len(body) > 4000 else body

        cards.append({
            "id": card_id,
            "type": kind,
            "title": title,
            "boxed_text": body_limited,
            "mechanics": json.dumps(gates) if gates else "",
            "references": f"Chapter {chapter_num}, {title}"
        })

    # Hard guarantee: never return 0 cards
    if not cards:
        cards.append({
            "id": f"ch{chapter_num:02d}_overview_001",
            "type": "section",
            "title": "Chapter Overview",
            "boxed_text": raw.strip()[:4000],
            "mechanics": json.dumps(extract_gates(raw)),
            "references": f"Chapter {chapter_num}"
        })
    
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
    log(f"[build] Chapters dir: {chapters_dir}")
    log(f"[build] Packs dir: {packs_dir}")
    
    # Ensure packs directory and logs subdirectory exist
    packs_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = packs_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Find chapter file
    log("[build] Locating chapter file...")
    chapter_file = find_chapter_file(chapters_dir, args.chapter)
    
    if not chapter_file:
        log(f"ERROR: Chapter file not found for chapter {args.chapter}")
        log(f"[build] Searched in: {chapters_dir}")
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
    cards = build_cards(args.chapter, raw_text)
    extract_elapsed = (time.time() - extract_start) * 1000
    log(f"[build] Extracted {len(cards)} cards in {extract_elapsed:.0f}ms")
    
    # Report heading patterns detected
    heading_counts = {}
    for card in cards:
        card_type = card.get('type', 'unknown')
        heading_counts[card_type] = heading_counts.get(card_type, 0) + 1
    
    if heading_counts:
        log(f"[build] Heading patterns: {dict(heading_counts)}")
    
    if len(cards) == 0:
        log("ERROR: No cards extracted - validation will fail")
        sys.exit(1)
    
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
    log(f"[build] Cards: {len(cards)}, Log: {log_path}")

if __name__ == "__main__":
    main()
