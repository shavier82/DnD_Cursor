#!/usr/bin/env python3
"""
Update spell lists to link all spells to the spell dictionary.
"""

import re
from pathlib import Path
import sys

# Base paths
BASE_PATH = Path(r"C:\Users\ksist\Documents\Obsidian\DnD\Player Characters")

def spell_name_to_filename(spell_name):
    """Convert spell name to filename format"""
    # Handle special cases
    special_cases = {
        "Tasha's Hideous Laughter": "Tashas_Hideous_Laughter",
        "Tenser's Floating Disk": "Tensers_Floating_Disk",
        "Blindness/Deafness": "Blindness_Deafness",
        "Dragon's Breath": "Dragons_Breath",
        "Melf's Acid Arrow": "Melfs_Acid_Arrow",
        "Nystul's Magic Aura": "Nystuls_Magic_Aura",
        "Enlarge/Reduce": "Enlarge_Reduce",
        "Leomund's Tiny Hut": "Leomunds_Tiny_Hut",
        "Protection from Evil and Good": "Protection_from_Evil_and_Good",
        "Detect Evil and Good": "Detect_Evil_and_Good"
    }
    
    if spell_name in special_cases:
        return special_cases[spell_name]
    
    # Standard conversion
    return spell_name.replace(' ', '_').replace("'", "").replace("/", "_")

def update_spell_list(file_path, class_name, max_level=3):
    """Update spell list file with links to spell dictionary"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Process each spell level
    for level in range(0, max_level + 1):
        if level == 0:
            level_name = "Cantrips"
            level_folder = "Level_0"
        else:
            level_name = f"Level {level} Spells"
            level_folder = f"Level_{level}"
        
        # Find the section - look for the header and all content until next ## or end of file
        pattern = rf'(## {re.escape(level_name)}\s*\n\n.*?)(?=\n## |\Z)'
        section_match = re.search(pattern, content, re.DOTALL)
        
        if not section_match:
            print(f"  ⚠️  Section '{level_name}' not found")
            continue
        
        section = section_match.group(1)
        original_section = section
        
        # Find all spell entries - match the checkbox, spell name, and rest
        # Handle both linked and unlinked spells
        spell_pattern = r'- \[([ x])\] \*\*([^*\]]+?)\*\* - ([^\n]+)'
        
        def replace_spell(match):
            checkbox = match.group(1)
            spell_name = match.group(2).strip()
            rest = match.group(3).strip()
            
            # Check if already linked
            if '[[' in spell_name:
                return match.group(0)
            
            # Convert to filename
            filename = spell_name_to_filename(spell_name)
            
            # Create link
            link_path = f"Spell_Dictionary/{class_name}/{level_folder}/{filename}"
            linked_spell = f"[[{link_path}|{spell_name}]]"
            
            # Wrap link in bold markers
            return f'- [{checkbox}] **{linked_spell}** - {rest}'
        
        section = re.sub(spell_pattern, replace_spell, section)
        
        # Replace the section in content
        content = content.replace(original_section, section)
        print(f"  ✓ Updated {level_name}")
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated {file_path.name}")

def main():
    """Main function"""
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Update Zephyr's spell list (Wizard, levels 0-3)
    zephyr_file = BASE_PATH / "Zephyr_Sparkwhistle_Spells.md"
    if zephyr_file.exists():
        update_spell_list(zephyr_file, "Wizard", max_level=3)
    
    # Update Torgga's spell list (Cleric, levels 0-3)
    torgga_file = BASE_PATH / "Torgga_Brawnanvil_Spells.md"
    if torgga_file.exists():
        update_spell_list(torgga_file, "Cleric", max_level=3)
    
    print("\n✅ All spell lists updated!")

if __name__ == "__main__":
    main()
