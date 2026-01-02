#!/usr/bin/env python3
"""
Import Character from PDF
Extracts character data from D&D Beyond PDF and creates/updates character JSON
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

def create_character_template(character_name, pdf_filename):
    """Create a character JSON template"""
    return {
        "character_name": character_name,
        "source_pdf": pdf_filename,
        "last_updated": datetime.now().isoformat(),
        "level": 1,
        "class": "",
        "race": "",
        "background": "",
        "alignment": "",
        "xp": 0,
        "xp_to_next": 300,
        "ability_scores": {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        },
        "ability_modifiers": {
            "strength": 0,
            "dexterity": 0,
            "constitution": 0,
            "intelligence": 0,
            "wisdom": 0,
            "charisma": 0
        },
        "proficiency_bonus": 2,
        "saving_throws": {
            "strength": False,
            "dexterity": False,
            "constitution": False,
            "intelligence": False,
            "wisdom": False,
            "charisma": False
        },
        "skills": {},
        "hit_points": {
            "current": 0,
            "maximum": 0,
            "temporary": 0
        },
        "armor_class": 10,
        "initiative": 0,
        "speed": 30,
        "spellcasting": {
            "ability": "",
            "spell_save_dc": 0,
            "spell_attack_bonus": 0,
            "spell_slots": {
                "1": {"total": 0, "used": 0},
                "2": {"total": 0, "used": 0},
                "3": {"total": 0, "used": 0},
                "4": {"total": 0, "used": 0},
                "5": {"total": 0, "used": 0},
                "6": {"total": 0, "used": 0},
                "7": {"total": 0, "used": 0},
                "8": {"total": 0, "used": 0},
                "9": {"total": 0, "used": 0}
            },
            "prepared_spells": [],
            "known_spells": [],
            "cantrips": []
        },
        "features": [],
        "equipment": [],
        "resources": {},
        "notes": ""
    }

def extract_from_pdf(pdf_path):
    """
    Extract character data from PDF.
    Note: This is a placeholder - actual PDF parsing requires libraries like PyPDF2 or pdfplumber.
    For now, returns None to indicate manual entry needed.
    """
    # TODO: Implement PDF parsing
    # Options:
    # 1. Use PyPDF2 to extract text and parse
    # 2. Use pdfplumber for better text extraction
    # 3. Use OCR if PDF is image-based
    return None

def main():
    parser = argparse.ArgumentParser(description='Import character from PDF or create template')
    parser.add_argument('--pdf', type=str, help='Path to character sheet PDF')
    parser.add_argument('--name', type=str, required=True, help='Character name')
    parser.add_argument('--update-xp', type=int, help='Add XP to character')
    parser.add_argument('--reset-spell-slots', action='store_true', help='Reset spell slots to full')
    args = parser.parse_args()
    
    # Load paths config
    script_dir = Path(__file__).parent
    config_path = script_dir.parent / "config" / "paths.json"
    
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    campaign_dir = Path(config['default_campaign_dir'])
    players_dir = campaign_dir / "players"
    players_dir.mkdir(parents=True, exist_ok=True)
    
    # Character JSON file path
    char_filename = f"{args.name.lower().replace(' ', '_')}.json"
    char_path = players_dir / char_filename
    
    # Load existing character or create new
    if char_path.exists():
        print(f"[import] Loading existing character: {char_path}")
        with open(char_path, 'r', encoding='utf-8') as f:
            character = json.load(f)
    else:
        print(f"[import] Creating new character: {args.name}")
        pdf_name = Path(args.pdf).name if args.pdf else "unknown.pdf"
        character = create_character_template(args.name, pdf_name)
    
    # Update XP if specified
    if args.update_xp:
        old_xp = character['xp']
        character['xp'] += args.update_xp
        print(f"[import] XP updated: {old_xp} -> {character['xp']}")
        
        # Calculate level (simplified - adjust thresholds as needed)
        xp_thresholds = [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 
                         85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]
        new_level = 1
        for i, threshold in enumerate(xp_thresholds, 1):
            if character['xp'] >= threshold:
                new_level = i
            else:
                break
        
        if new_level > character['level']:
            print(f"[import] Level up! {character['level']} -> {new_level}")
            character['level'] = new_level
            character['proficiency_bonus'] = 2 + ((new_level - 1) // 4)
        
        if new_level < 20:
            character['xp_to_next'] = xp_thresholds[new_level] - character['xp']
        else:
            character['xp_to_next'] = 0
    
    # Reset spell slots if requested
    if args.reset_spell_slots:
        for slot_level in character['spellcasting']['spell_slots']:
            character['spellcasting']['spell_slots'][slot_level]['used'] = 0
        print("[import] Spell slots reset to full")
    
    # Try to extract from PDF if provided
    if args.pdf:
        pdf_path = Path(args.pdf)
        if pdf_path.exists():
            print(f"[import] Attempting to extract from PDF: {pdf_path}")
            extracted = extract_from_pdf(pdf_path)
            if extracted:
                # Merge extracted data
                character.update(extracted)
                print("[import] Data extracted from PDF")
            else:
                print("[import] PDF parsing not yet implemented - using template")
                print("[import] Please manually update the character JSON file")
        else:
            print(f"[import] WARNING: PDF file not found: {pdf_path}")
    
    # Update timestamp
    character['last_updated'] = datetime.now().isoformat()
    
    # Save character JSON
    with open(char_path, 'w', encoding='utf-8') as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
    
    print(f"[import] Character saved: {char_path}")
    print(f"[import] Level: {character['level']}, XP: {character['xp']}/{character['xp_to_next']} to next")

if __name__ == "__main__":
    main()

