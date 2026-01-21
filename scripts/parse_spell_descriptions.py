#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse full spell descriptions from PHB 2024 and update spells.json database.
Extracts: casting_time, range, components, duration, description, at_higher_levels
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Optional

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

PHB_FILE = Path(r"C:\DnD\Sourcebooks\PlayersHandbook2024.txt")
SPELLS_DB = Path(r"C:\DnD\DnD_Cursor\rules_database\spells.json")

def load_spells_db():
    """Load existing spells database"""
    with open(SPELLS_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_spells_db(spells):
    """Save updated spells database"""
    with open(SPELLS_DB, 'w', encoding='utf-8') as f:
        json.dump(spells, f, indent=2, ensure_ascii=False)

def get_spell_id(spell_name: str) -> str:
    """Convert spell name to spell_id format"""
    return spell_name.lower().replace(' ', '_').replace("'", "").replace("/", "_")

def parse_spell_description(content: str, spell_name: str) -> Optional[Dict]:
    """Parse full spell description from PHB content"""
    # Find spell entry - spell name on its own line (may have leading/trailing whitespace)
    # Pattern: spell name, then newline, then "Level X" or "School Cantrip"
    pattern = f"^{re.escape(spell_name)}\\n(Level \\d+|Cantrip|[A-Za-z]+ Cantrip)"
    match = re.search(pattern, content, re.MULTILINE)
    
    if not match:
        return None
    
    start_pos = match.start()
    
    # Find the next spell - look for pattern: newline, spell name, newline, "Level X" or "School Cantrip"
    # But skip if it's part of the current spell's description
    search_start = start_pos + len(spell_name) + 50  # Skip a bit to avoid matching current spell
    next_spell_pattern = r"\n\n([A-Z][A-Za-z\s'/-]+)\n(Level \d+|[A-Za-z]+ Cantrip)"
    next_match = re.search(next_spell_pattern, content[search_start:], re.MULTILINE)
    
    if next_match:
        end_pos = search_start + next_match.start()
    else:
        # Find end of spells section
        end_pos = content.find("\n\nSpells (", start_pos)
        if end_pos == -1:
            end_pos = len(content)
    
    spell_text = content[start_pos:end_pos]
    
    # Parse spell details
    result = {}
    
    # Extract level and school from second line
    level_match = re.search(r"Level (\d+) ([A-Za-z]+) \(([^)]+)\)", spell_text)
    cantrip_match = re.search(r"([A-Za-z]+) Cantrip \(([^)]+)\)", spell_text)
    
    if level_match:
        result['level'] = int(level_match.group(1))
        result['school'] = level_match.group(2)
    elif cantrip_match:
        result['level'] = 0
        result['school'] = cantrip_match.group(1)
    else:
        return None
    
    # Extract Casting Time
    casting_match = re.search(r"Casting Time:\s*(.+?)(?=\n\n|$)", spell_text, re.DOTALL)
    if casting_match:
        result['casting_time'] = casting_match.group(1).strip()
    
    # Extract Range
    range_match = re.search(r"Range:\s*(.+?)(?=\n\n|$)", spell_text, re.DOTALL)
    if range_match:
        result['range'] = range_match.group(1).strip()
    
    # Extract Components
    components_match = re.search(r"Components:\s*(.+?)(?=\n\n|$)", spell_text, re.DOTALL)
    if components_match:
        result['components'] = components_match.group(1).strip()
    
    # Extract Duration
    duration_match = re.search(r"Duration:\s*(.+?)(?=\n\n|$)", spell_text, re.DOTALL)
    if duration_match:
        result['duration'] = duration_match.group(1).strip()
    
    # Extract Description (everything after Duration until "Using a Higher-Level" or next spell)
    desc_start = spell_text.find("Duration:")
    if desc_start != -1:
        desc_start = spell_text.find("\n", desc_start) + 1
        higher_level_match = re.search(r"\n\nUsing a Higher-Level", spell_text[desc_start:])
        if higher_level_match:
            desc_end = desc_start + higher_level_match.start()
            result['description'] = spell_text[desc_start:desc_end].strip()
            
            # Extract "At Higher Levels" section - stop at next spell or end
            higher_level_start = desc_start + higher_level_match.start() + 2
            higher_level_text = spell_text[higher_level_start:].strip()
            
            # Stop at next spell pattern (spell name on its own line followed by "Level X" or "School Cantrip")
            next_spell_match = re.search(r"\n\n([A-Z][A-Za-z\s'/-]+)\n(Level \d+|[A-Za-z]+ Cantrip)", higher_level_text)
            if next_spell_match:
                higher_level_text = higher_level_text[:next_spell_match.start()].strip()
            
            result['at_higher_levels'] = higher_level_text
        else:
            # Description goes to end (or next spell)
            result['description'] = spell_text[desc_start:].strip()
            # Remove any trailing spell name patterns
            next_spell_match = re.search(r"\n\n([A-Z][A-Za-z\s'/-]+)\n(Level \d+|[A-Za-z]+ Cantrip)", result['description'])
            if next_spell_match:
                result['description'] = result['description'][:next_spell_match.start()].strip()
            result['at_higher_levels'] = None
    
    return result

def main():
    print("Loading PHB content...")
    with open(PHB_FILE, 'r', encoding='utf-8') as f:
        phb_content = f.read()
    
    print("Loading spells database...")
    spells = load_spells_db()
    
    print(f"Found {len(spells)} spells in database")
    print("\nParsing spell descriptions...")
    
    updated = 0
    not_found = 0
    
    for spell_id, spell_data in spells.items():
        spell_name = spell_data['name']
        print(f"  Processing: {spell_name}...", end=' ')
        
        description_data = parse_spell_description(phb_content, spell_name)
        
        if description_data:
            # Update spell with full details
            spell_data['casting_time'] = description_data.get('casting_time', '')
            spell_data['range'] = description_data.get('range', '')
            spell_data['components'] = description_data.get('components', '')
            spell_data['duration'] = description_data.get('duration', '')
            spell_data['description'] = description_data.get('description', '')
            spell_data['at_higher_levels'] = description_data.get('at_higher_levels', '')
            
            updated += 1
            print("OK")
        else:
            not_found += 1
            print("NOT FOUND")
    
    print(f"\nSaving updated database...")
    save_spells_db(spells)
    
    print(f"\nComplete!")
    print(f"  Updated: {updated} spells")
    print(f"  Not found: {not_found} spells")

if __name__ == "__main__":
    main()
