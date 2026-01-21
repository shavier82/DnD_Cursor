#!/usr/bin/env python3
"""
Fix spell links in spell list files to link to Spell_Dictionary
"""

import re
import os
from pathlib import Path

def spell_name_to_file(spell_name):
    """Convert spell name to dictionary filename format"""
    # Replace spaces with underscores
    filename = spell_name.replace(' ', '_')
    # Handle special characters - apostrophes stay in display but become underscores in filename
    # But actually, looking at the files, they use underscores: Tasha's_Hideous_Laughter.md
    # So we need to handle apostrophes specially
    filename = filename.replace("'", "'")  # Keep apostrophe in filename
    return filename

def add_spell_links(content, class_name, level_num):
    """Add links to spells that don't have them"""
    if level_num == 0:
        level_str = "Level_0"
    else:
        level_str = f"Level_{level_num}"
    
    # Pattern to match spell list items: - [x] **Spell Name** - School
    # This needs to handle both linked and unlinked spells
    # Match: - [x] **Spell Name** - School (with optional notes)
    pattern = r'(- \[[ x]\]) \*\*([^*\n]+)\*\* - ([^\n]+)'
    
    def replace_spell(match):
        checkbox = match.group(1)
        spell_name_or_link = match.group(2).strip()
        school_info = match.group(3).strip()
        
        # Skip if already has a link
        if '[[' in spell_name_or_link:
            return match.group(0)
        
        # Extract just the spell name (remove any existing formatting)
        spell_name = spell_name_or_link.strip()
        
        # Convert spell name to filename format
        filename = spell_name.replace(' ', '_')
        # Handle apostrophes - they stay in the filename as-is
        # The files use straight apostrophes: Tasha's_Hideous_Laughter.md
        
        # Create link
        link_path = f"Spell_Dictionary/{class_name}/{level_str}/{filename}"
        linked_name = f"[[{link_path}|{spell_name}]]"
        
        return f'{checkbox} **{linked_name}** - {school_info}'
    
    return re.sub(pattern, replace_spell, content)

def main():
    base_path = Path(r"C:\Users\ksist\Documents\Obsidian\DnD\Player Characters")
    
    # Process Torgga's spell list
    torgga_file = base_path / "Torgga_Brawnanvil_Spells.md"
    if torgga_file.exists():
        print(f"Processing {torgga_file.name}...")
        with open(torgga_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Process each level
        # Handle cantrips separately
        if '## Cantrips' in content:
            content = add_spell_links(content, "Cleric", 0)
        
        for level in [1, 2, 3, 4]:
            # Find the level section
            level_pattern = rf'## Level {level} Spells'
            if level_pattern in content:
                # Add links for this level
                content = add_spell_links(content, "Cleric", level)
        
        with open(torgga_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {torgga_file.name}")
    
    # Process Zephyr's spell list
    zephyr_file = base_path / "Zephyr_Sparkwhistle_Spells.md"
    if zephyr_file.exists():
        print(f"Processing {zephyr_file.name}...")
        with open(zephyr_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Process each level
        # Handle cantrips separately
        if '## Cantrips' in content:
            content = add_spell_links(content, "Wizard", 0)
        
        for level in [1, 2, 3, 4]:
            # Find the level section
            level_pattern = rf'## Level {level} Spells'
            if level_pattern in content:
                # Add links for this level
                content = add_spell_links(content, "Wizard", level)
        
        with open(zephyr_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {zephyr_file.name}")
    
    print("\nDone! All spell links have been added.")

if __name__ == "__main__":
    main()
