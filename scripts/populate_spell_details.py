#!/usr/bin/env python3
"""
Populate spell files with actual spell details from MCP tools.
This script looks up each spell and fills in the spell details section.
"""

import json
import re
from pathlib import Path
import subprocess
import sys

# Base paths
BASE_PATH = Path(r"C:\Users\ksist\Documents\Obsidian\DnD\Player Characters")
SPELL_DICT_PATH = BASE_PATH / "Spell_Dictionary"
RULES_DB = Path(r"C:\DnD\DnD_Cursor\rules_database\spells.json")

def load_spells_db():
    """Load spells database"""
    with open(RULES_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_spell_id(spell_name):
    """Convert spell name to spell_id format"""
    # Handle special cases first
    special_cases = {
        "blindness deafness": "blindness/deafness",
        "tashas hideous laughter": "tashas_hideous_laughter",
        "tensers floating disk": "tensers_floating_disk",
        "leomunds tiny hut": "leomunds_tiny_hut",
        "melfs acid arrow": "melfs_acid_arrow",
        "nystuls magic aura": "nystuls_magic_aura",
        "dragons breath": "dragons_breath",
        "enlarge reduce": "enlarge/reduce"
    }
    
    spell_lower = spell_name.lower()
    if spell_lower in special_cases:
        return special_cases[spell_lower]
    
    # Standard conversion
    return spell_lower.replace(' ', '_').replace("'", "").replace("/", "_")

def get_spell_info(spell_name, spells_db):
    """Get spell information from database"""
    spell_id = get_spell_id(spell_name)
    
    if spell_id in spells_db:
        return spells_db[spell_id]
    
    # Try partial match
    for s_id, spell in spells_db.items():
        if spell_name.lower() == spell['name'].lower():
            return spell
    
    return None

def update_spell_file(spell_path, spell_info):
    """Update spell file with actual spell details"""
    if not spell_path.exists():
        return False
    
    with open(spell_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract current properties
    properties_match = re.search(r'properties:\s*(.+?)\n', content)
    properties = properties_match.group(1) if properties_match else "None"
    
    # Determine concentration and ritual
    concentration = spell_info.get('concentration', False)
    ritual = spell_info.get('ritual', False)
    material = spell_info.get('material', False)
    
    # Build components string
    components = []
    if concentration:
        components.append("Concentration")
    if ritual:
        components.append("Ritual")
    if material:
        components.append("Material")
    components_str = ", ".join(components) if components else "None"
    
    # Build classes string
    classes_str = ", ".join(spell_info.get('classes', []))
    
    # Create spell details section with full information
    level_text = "Cantrip" if spell_info['level'] == 0 else f"Level {spell_info['level']}"
    
    # Get full spell details from database
    casting_time = spell_info.get('casting_time', 'Not available')
    range_info = spell_info.get('range', 'Not available')
    components_full = spell_info.get('components', 'Not available')
    duration = spell_info.get('duration', 'Not available')
    description = spell_info.get('description', 'Not available')
    at_higher_levels = spell_info.get('at_higher_levels', '')
    
    concentration_str = 'Yes' if concentration else 'No'
    ritual_str = 'Yes' if ritual else 'No'
    material_str = 'Yes' if material else 'No'
    
    spell_details = f"""## Spell Details

**Level:** {level_text}  
**School:** {spell_info['school']}  
**Classes:** {classes_str}  
**Source:** {spell_info.get('source', 'PHB 2024')}

**Casting Time:** {casting_time}  
**Range:** {range_info}  
**Components:** {components_full}  
**Duration:** {duration}

**Description:**  
{description}
"""
    
    if at_higher_levels:
        spell_details += f"""
**At Higher Levels:**  
{at_higher_levels}
"""
    
    spell_details += f"""
**Quick Reference:**
- **Concentration:** {concentration_str}
- **Ritual:** {ritual_str}
- **Material:** {material_str}

**Note:** Full spell details from PHB 2024 are included above. Use MCP tools during gameplay for additional spell information if needed.
"""
    
    # Replace the Spell Details section
    # Use regex to match from "## Spell Details" to "## Quick Links"
    # Handle both old format (with placeholder text) and new format
    pattern = r'(## Spell Details\n\n).*?(\n## Quick Links)'
    replacement = r'\1' + spell_details.rstrip() + r'\2'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # If replacement didn't work, try finding manually
    if new_content == content:
        spell_details_start = content.find('## Spell Details')
        if spell_details_start != -1:
            quick_links_start = content.find('\n## Quick Links', spell_details_start)
            if quick_links_start != -1:
                before = content[:spell_details_start]
                after = content[quick_links_start + 1:]  # +1 to skip the newline
                content = before + spell_details.rstrip() + '\n' + after
            else:
                return False
        else:
            return False
    else:
        content = new_content
    
    # Write updated content
    with open(spell_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("Loading spells database...")
    spells_db = load_spells_db()
    print(f"Loaded {len(spells_db)} spells")
    
    print("\nUpdating spell files with details...")
    updated = 0
    failed = 0
    
    # Process all spell files
    for class_folder in ['Cleric', 'Wizard']:
        class_path = SPELL_DICT_PATH / class_folder
        if not class_path.exists():
            continue
        
        for level_folder in class_path.iterdir():
            if not level_folder.is_dir():
                continue
            
            for spell_file in level_folder.glob('*.md'):
                spell_name = spell_file.stem.replace('_', ' ')
                # Handle special cases - convert back to proper spell names
                special_cases = {
                    'Blindness Deafness': 'Blindness/Deafness',
                    'Dragons Breath': "Dragon's Breath",
                    'Tashas Hideous Laughter': "Tasha's Hideous Laughter",
                    'Tensers Floating Disk': "Tenser's Floating Disk",
                    'Leomunds Tiny Hut': "Leomund's Tiny Hut",
                    'Nystuls Magic Aura': "Nystul's Magic Aura",
                    'Melfs Acid Arrow': "Melf's Acid Arrow",
                    'Enlarge Reduce': 'Enlarge/Reduce'
                }
                if spell_name in special_cases:
                    spell_name = special_cases[spell_name]
                
                spell_info = get_spell_info(spell_name, spells_db)
                if spell_info:
                    if update_spell_file(spell_file, spell_info):
                        updated += 1
                        print(f"  Updated: {spell_file.relative_to(BASE_PATH)}")
                    else:
                        failed += 1
                else:
                    print(f"  Warning: Could not find spell info for '{spell_name}'")
                    failed += 1
    
    print(f"\nComplete! Updated {updated} spell files, {failed} failed or skipped.")

if __name__ == "__main__":
    main()
