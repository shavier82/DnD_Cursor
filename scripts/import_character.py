#!/usr/bin/env python3
"""
Import Character from PDF using OCR
Downloads PDFs from D&D Beyond URLs and extracts character data using OCR
"""

import json
import sys
import argparse
import re
import requests
from pathlib import Path
from datetime import datetime

try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

def download_pdf(url, output_path):
    """Download PDF from URL"""
    print(f"[download] Fetching {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"[download] Saved to {output_path}")
    return output_path

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF, trying text extraction first, then OCR if needed"""
    # Try PyMuPDF first (extracts text directly if PDF has text layer)
    if PDF_AVAILABLE:
        try:
            print(f"[extract] Attempting direct text extraction...")
            doc = fitz.open(pdf_path)
            text_parts = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                text_parts.append(text)
            doc.close()
            
            full_text = "\n".join(text_parts)
            if len(full_text.strip()) > 100:  # If we got substantial text
                print(f"[extract] Successfully extracted {len(full_text)} characters")
                return full_text
            else:
                print(f"[extract] Text layer too sparse, falling back to OCR...")
        except Exception as e:
            print(f"[extract] Direct extraction failed: {e}, trying OCR...")
    
    # Fall back to OCR if text extraction didn't work
    if OCR_AVAILABLE:
        try:
            print(f"[ocr] Converting PDF to images...")
            images = convert_from_path(pdf_path, dpi=300)
            
            all_text = []
            for i, image in enumerate(images):
                print(f"[ocr] Processing page {i+1}/{len(images)}...")
                text = pytesseract.image_to_string(image)
                all_text.append(text)
            
            return "\n".join(all_text)
        except Exception as e:
            raise RuntimeError(f"OCR failed: {e}. Install poppler for Windows or use PDFs with text layers.")
    else:
        raise RuntimeError("No PDF extraction method available. Install PyMuPDF or pdf2image/pytesseract.")

def parse_character_data(text):
    """Parse character data from extracted text"""
    char_data = {}
    lines = [line.strip() for line in text.split('\n')]
    
    # Find label positions
    label_positions = {}
    for i, line in enumerate(lines):
        line_upper = line.upper()
        if 'CHARACTER NAME' in line_upper and 'character_name' not in label_positions:
            label_positions['character_name'] = i
        elif ('CLASS' in line_upper and 'LEVEL' in line_upper) and 'class_level' not in label_positions:
            label_positions['class_level'] = i
        elif ('SPECIES' in line_upper or ('RACE' in line_upper and i < 20)) and 'race' not in label_positions:
            label_positions['race'] = i
        elif ('EXPERIENCE POINTS' in line_upper or 'EXPERIENCE' in line_upper) and 'xp' not in label_positions:
            label_positions['xp'] = i
    
    # Extract character name - look for value after CHARACTER NAME label
    # In D&D Beyond PDFs, the name appears much later in the columnar layout
    # The name is typically 60-70 lines after the label
    if 'character_name' in label_positions:
        label_line = label_positions['character_name']
        # Look in the range where character data typically appears (60-75 lines after label)
        # Also check earlier in case layout is different
        search_ranges = [(60, 80), (1, 100)]  # Try specific range first, then broader
        
        for start_offset, end_offset in search_ranges:
            for offset in range(start_offset, end_offset):
                if label_line + offset < len(lines):
                    candidate = lines[label_line + offset].strip()
                    # Name should be 2-3 words, Title Case, not a skill/class/field label
                    words = candidate.split()
                    if (len(words) >= 1 and len(words) <= 4 and
                        len(candidate) > 3 and len(candidate) < 50 and
                        candidate[0].isupper() and
                        all(w[0].isupper() for w in words if w) and
                        any(c.islower() for c in candidate) and
                        # Exclude known field labels, skills, classes
                        candidate.upper() not in ['CHARACTER NAME', 'CLASS', 'RACE', 'LEVEL', 'BACKGROUND',
                                                  'ALIGNMENT', 'EXPERIENCE POINTS', 'HIT POINTS', 'SPECIES',
                                                  'PLAYER NAME', 'STRENGTH', 'DEXTERITY', 'CONSTITUTION',
                                                  'INTELLIGENCE', 'WISDOM', 'CHARISMA', 'ACROBATICS',
                                                  'ANIMAL HANDLING', 'ARCANA', 'ATHLETICS', 'DECEPTION',
                                                  'HISTORY', 'INSIGHT', 'INTIMIDATION', 'INVESTIGATION',
                                                  'MEDICINE', 'NATURE', 'PERCEPTION', 'PERFORMANCE',
                                                  'PERSUASION', 'RELIGION', 'SLEIGHT OF HAND', 'STEALTH',
                                                  'SURVIVAL', 'GLADIATOR', 'BARBARIAN', 'WIZARD', 'ROGUE',
                                                  'CLERIC', 'FIGHTER', 'PALADIN', 'RANGER', 'SORCERER',
                                                  'WARLOCK', 'BARD', 'DRUID', 'MONK', 'SAVING THROW MODIFIERS',
                                                  'NOTES', 'ACTIONS', 'HEROIC INSPIRATION', 'PROFICIENCIES',
                                                  'DEFENSES', 'DEATH SAVES', 'HIT DICE', 'TOTAL', 'SUCCESSES',
                                                  'FAILURES', 'MAX HP', 'CURRENT HP', 'TEMP HP', 'SPEED',
                                                  'ARMOR', 'PROFICIENCY BONUS', 'ABILITY SAVE DC'] and
                        # Must not be all uppercase (field labels are)
                        not candidate.isupper() and
                        # Must have at least one lowercase letter
                        any(c.islower() for c in candidate)):
                        char_data['character_name'] = candidate
                        print(f"[parse] Found character name at line {label_line + offset}: {candidate}")
                        break
            if 'character_name' in char_data:
                break
    
    # Extract class and level (often together like "Barbarian 4")
    if 'class_level' in label_positions:
        label_line = label_positions['class_level']
        for offset in range(1, 70):
            if label_line + offset < len(lines):
                candidate = lines[label_line + offset].strip()
                # Look for pattern like "Barbarian 4" or "Wizard 3"
                class_level_match = re.match(r'([A-Z][a-z]+)\s+(\d+)', candidate)
                if class_level_match:
                    char_data['class'] = class_level_match.group(1)
                    char_data['level'] = int(class_level_match.group(2))
                    break
    
    # Extract race/species - look in same column as character name
    if 'race' in label_positions and 'character_name' in char_data:
        # Race appears near character name in columnar layout
        name_line = None
        for i, line in enumerate(lines):
            if line.strip() == char_data['character_name']:
                name_line = i
                break
        
        if name_line:
            # Race is typically 3 lines after character name (after class/level line and player name line)
            # Common races: Dwarf, Elf, Halfling, Human, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling
            # Can be compound: "Hill Dwarf", "Wood Elf", etc.
            common_races = ['Dwarf', 'Elf', 'Halfling', 'Human', 'Dragonborn', 'Gnome', 'Half-Elf', 
                           'Half-Orc', 'Tiefling', 'Goliath', 'Aasimar', 'Genasi', 'Firbolg',
                           'Goblin', 'Hobgoblin', 'Bugbear', 'Kobold', 'Orc', 'Yuan-Ti', 'Triton']
            
            # Skip player name line (usually has numbers/username pattern)
            for offset in [3, 2, 4, 1, 5]:
                if name_line + offset < len(lines):
                    candidate = lines[name_line + offset].strip()
                    # Skip if looks like player name (has numbers, all lowercase, or username pattern)
                    if re.match(r'^[a-z]+\d+', candidate) or candidate.islower() or len(candidate) < 3:
                        continue
                    
                    # Race can be single word or compound (Hill Dwarf, Wood Elf)
                    words = candidate.split()
                    # Check if it contains a known race word or looks like a race
                    is_race = False
                    for word in words:
                        if word in common_races or (word.endswith('Dwarf') or word.endswith('Elf') or 
                                                    word.endswith('Orc') or word.endswith('Genasi')):
                            is_race = True
                            break
                    
                    # Backgrounds to exclude
                    backgrounds = ['Soldier', 'Acolyte', 'Criminal', 'Folk Hero', 'Hermit',
                                  'Noble', 'Sage', 'Sailor', 'Urchin', 'Entertainer', 'Guild Artisan',
                                  'Guild Merchant', 'Outlander', 'Charlatan', 'Gladiator']
                    
                    if (is_race or 
                        (len(candidate) > 2 and len(candidate) < 30 and 
                         candidate[0].isupper() and 
                         candidate not in ['Species', 'Race', 'Class', 'Level', 'Gladiator', 'Player',
                                          'Background', 'Alignment', 'Character', 'Name'] + backgrounds and
                         not re.match(r'^[a-z]+\d+', candidate))):  # Not a username
                        char_data['race'] = candidate
                        print(f"[parse] Found race at line {name_line + offset}: {candidate}")
                        break
    
    # Fallback: use label position method
    if 'race' not in char_data and 'race' in label_positions:
        label_line = label_positions['race']
        for offset in range(60, 80):  # Race appears in same column range as name
            if label_line + offset < len(lines):
                candidate = lines[label_line + offset].strip()
                if (len(candidate) > 2 and len(candidate) < 30 and 
                    candidate[0].isupper() and candidate.isalpha() and
                    candidate not in ['Species', 'Race', 'Class', 'Level', 'Gladiator', 'Player',
                                     'Background', 'Alignment', 'Character', 'Name']):
                    char_data['race'] = candidate
                    break
    
    # Fallback regex patterns
    if 'level' not in char_data:
        level_match = re.search(r'\b(\d+)\s*(?:st|nd|rd|th)?\s*LEVEL\b', text, re.IGNORECASE)
        if not level_match:
            level_match = re.search(r'(?:CLASS|LEVEL)[:\s]+.*?(\d+)', text, re.IGNORECASE)
        if level_match:
            char_data['level'] = int(level_match.group(1))
    
    if 'class' not in char_data:
        class_match = re.search(r'(?:CLASS|CLASS\s+&?\s+LEVEL)[:\s]+([A-Z][a-z]+)', text, re.IGNORECASE)
        if class_match:
            char_data['class'] = class_match.group(1).strip()
    
    if 'race' not in char_data:
        race_match = re.search(r'(?:RACE|SPECIES)[:\s]+([A-Z][a-z]+)', text, re.IGNORECASE)
        if race_match:
            char_data['race'] = race_match.group(1).strip()
    
    # Extract ability scores
    abilities = ['STRENGTH', 'DEXTERITY', 'CONSTITUTION', 'INTELLIGENCE', 'WISDOM', 'CHARISMA']
    ability_map = {
        'STRENGTH': 'strength',
        'DEXTERITY': 'dexterity',
        'CONSTITUTION': 'constitution',
        'INTELLIGENCE': 'intelligence',
        'WISDOM': 'wisdom',
        'CHARISMA': 'charisma'
    }
    
    ability_scores = {}
    for ability in abilities:
        # Look for patterns like "STRENGTH 16" or "STR 16"
        patterns = [
            rf'{ability}[:\s]+(\d+)',
            rf'{ability[:3]}[:\s]+(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ability_scores[ability_map[ability]] = int(match.group(1))
                break
    
    if ability_scores:
        char_data['ability_scores'] = ability_scores
        # Calculate modifiers
        modifiers = {}
        for ability, score in ability_scores.items():
            modifiers[ability] = (score - 10) // 2
        char_data['ability_modifiers'] = modifiers
    
    # Extract XP (may have commas)
    if 'xp' in label_positions:
        label_line = label_positions['xp']
        for offset in range(1, 70):
            if label_line + offset < len(lines):
                candidate = lines[label_line + offset].strip()
                # Remove commas and extract number
                xp_match = re.search(r'(\d{1,3}(?:,\d{3})*)', candidate)
                if xp_match:
                    char_data['xp'] = int(xp_match.group(1).replace(',', ''))
                    break
    
    if 'xp' not in char_data:
        xp_match = re.search(r'EXPERIENCE[:\s]+(\d{1,3}(?:,\d{3})*)', text, re.IGNORECASE)
        if xp_match:
            char_data['xp'] = int(xp_match.group(1).replace(',', ''))
    
    # Extract hit points
    hp_patterns = [
        r'HIT\s+POINTS[:\s]+(\d+)\s*/\s*(\d+)',
        r'HP[:\s]+(\d+)\s*/\s*(\d+)',
        r'HIT\s+POINT\s+MAXIMUM[:\s]+(\d+)',
    ]
    for pattern in hp_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:
                char_data['hit_points'] = {
                    'current': int(match.group(1)),
                    'maximum': int(match.group(2)),
                    'temporary': 0
                }
            else:
                char_data['hit_points'] = {
                    'current': int(match.group(1)),
                    'maximum': int(match.group(1)),
                    'temporary': 0
                }
            break
    
    # Extract armor class
    ac_match = re.search(r'ARMOR\s+CLASS[:\s]+(\d+)', text, re.IGNORECASE)
    if ac_match:
        char_data['armor_class'] = int(ac_match.group(1))
    
    # Extract spell slots (look for patterns like "1st Level 2" or "Level 1: 2")
    spell_slots = {}
    for level in range(1, 10):
        patterns = [
            rf'{level}(?:st|nd|rd|th)?\s+LEVEL[:\s]+(\d+)',
            rf'LEVEL\s+{level}[:\s]+(\d+)',
            rf'SPELL\s+SLOTS\s+LEVEL\s+{level}[:\s]+(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                total = int(match.group(1))
                spell_slots[str(level)] = {'total': total, 'used': 0}
                break
    
    if spell_slots:
        char_data['spellcasting'] = {
            'spell_slots': spell_slots,
            'prepared_spells': [],
            'known_spells': [],
            'cantrips': []
        }
    
    return char_data

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

def merge_character_data(template, extracted):
    """Merge extracted data into template"""
    # Update template with extracted data
    for key, value in extracted.items():
        if key == 'ability_scores' and isinstance(value, dict):
            template['ability_scores'].update(value)
            # Recalculate modifiers
            for ability, score in value.items():
                template['ability_modifiers'][ability] = (score - 10) // 2
        elif key == 'hit_points' and isinstance(value, dict):
            template['hit_points'].update(value)
        elif key == 'spellcasting' and isinstance(value, dict):
            if 'spell_slots' in value:
                template['spellcasting']['spell_slots'].update(value['spell_slots'])
        else:
            template[key] = value
    
    # Calculate proficiency bonus from level
    if 'level' in template:
        template['proficiency_bonus'] = 2 + ((template['level'] - 1) // 4)
    
    # Calculate XP to next level
    if 'xp' in template and 'level' in template:
        xp_thresholds = [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 
                         85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]
        level = template['level']
        if level < 20:
            template['xp_to_next'] = xp_thresholds[level] - template['xp']
        else:
            template['xp_to_next'] = 0
    
    return template

def main():
    parser = argparse.ArgumentParser(description='Import character from PDF URL using OCR')
    parser.add_argument('--url', type=str, help='D&D Beyond PDF URL')
    parser.add_argument('--name', type=str, help='Character name (overrides OCR extraction)')
    parser.add_argument('--update-xp', type=int, help='Add XP to character')
    parser.add_argument('--reset-spell-slots', action='store_true', help='Reset spell slots to full')
    args = parser.parse_args()
    
    if not PDF_AVAILABLE and not OCR_AVAILABLE:
        print("ERROR: PDF extraction libraries not installed. Run: pip install PyMuPDF", file=sys.stderr)
        print("  For OCR (if PDFs are image-based): pip install pytesseract pdf2image pillow", file=sys.stderr)
        sys.exit(1)
    
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
    
    # Download PDF if URL provided
    pdf_path = None
    if args.url:
        pdf_filename = args.url.split('/')[-1]
        pdf_path = players_dir / pdf_filename
        
        if not pdf_path.exists():
            download_pdf(args.url, pdf_path)
        else:
            print(f"[import] Using existing PDF: {pdf_path}")
    
    # Extract text from PDF
    character_name = args.name
    extracted_data = {}
    
    if pdf_path and pdf_path.exists():
        print(f"[extract] Extracting text from PDF...")
        text = extract_text_from_pdf(str(pdf_path))
        
        # Save extracted text for debugging
        text_path = players_dir / f"{pdf_path.stem}_extracted.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"[extract] Extracted text saved to: {text_path}")
        
        # Parse character data
        print(f"[parse] Parsing character data...")
        extracted_data = parse_character_data(text)
        
        # Use extracted name if not provided
        if not character_name and 'character_name' in extracted_data:
            character_name = extracted_data['character_name']
            print(f"[parse] Extracted character name: {character_name}")
    
    if not character_name:
        print("ERROR: Character name not found. Provide --name or ensure PDF contains character name.", file=sys.stderr)
        sys.exit(1)
    
    # Character JSON file path
    char_filename = f"{character_name.lower().replace(' ', '_')}.json"
    char_path = players_dir / char_filename
    
    # Load existing character or create new
    if char_path.exists():
        print(f"[import] Loading existing character: {char_path}")
        with open(char_path, 'r', encoding='utf-8') as f:
            character = json.load(f)
    else:
        print(f"[import] Creating new character: {character_name}")
        pdf_name = pdf_path.name if pdf_path else "unknown.pdf"
        character = create_character_template(character_name, pdf_name)
    
    # Merge extracted data
    if extracted_data:
        character = merge_character_data(character, extracted_data)
        print(f"[import] Merged extracted data")
    
    # Update XP if specified
    if args.update_xp:
        old_xp = character['xp']
        character['xp'] += args.update_xp
        print(f"[import] XP updated: {old_xp} -> {character['xp']}")
        
        # Calculate level
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
    
    # Update timestamp
    character['last_updated'] = datetime.now().isoformat()
    
    # Save character JSON
    with open(char_path, 'w', encoding='utf-8') as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
    
    print(f"[import] Character saved: {char_path}")
    print(f"[import] Level: {character['level']}, XP: {character['xp']}/{character['xp_to_next']} to next")
    if 'class' in character and character['class']:
        print(f"[import] Class: {character['class']}, Race: {character.get('race', 'Unknown')}")

if __name__ == "__main__":
    main()
