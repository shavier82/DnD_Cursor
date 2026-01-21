#!/usr/bin/env python3
"""
Fix spell links in spell list files to link to Spell_Dictionary
"""

import re
from pathlib import Path

def add_spell_links_to_section(section_content, class_name, level_num):
    """Add links to spells in a section that don't have them"""
    if level_num == 0:
        level_str = "Level_0"
    else:
        level_str = f"Level_{level_num}"
    
    # Pattern to match spell list items: - [x] **Spell Name** - School
    pattern = r'(- \[[ x]\]) \*\*([^*\n]+)\*\* - ([^\n]+)'
    
    def replace_spell(match):
        checkbox = match.group(1)
        spell_name_or_link = match.group(2).strip()
        school_info = match.group(3).strip()
        
        # Skip if already has a link
        if '[[' in spell_name_or_link:
            return match.group(0)
        
        # Extract just the spell name
        spell_name = spell_name_or_link.strip()
        
        # Convert spell name to filename format
        filename = spell_name.replace(' ', '_')
        
        # Create link
        link_path = f"Spell_Dictionary/{class_name}/{level_str}/{filename}"
        linked_name = f"[[{link_path}|{spell_name}]]"
        
        return f'{checkbox} **{linked_name}** - {school_info}'
    
    return re.sub(pattern, replace_spell, section_content)

def process_file(file_path, class_name):
    """Process a spell list file and add links"""
    print(f"Processing {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into sections
    sections = re.split(r'(## .+?\n)', content)
    
    result_parts = []
    i = 0
    
    while i < len(sections):
        section_header = sections[i] if i < len(sections) else ""
        section_content = sections[i + 1] if i + 1 < len(sections) else ""
        
        # Determine level from header
        level = None
        if '## Cantrips' in section_header:
            level = 0
        elif '## Level 1 Spells' in section_header:
            level = 1
        elif '## Level 2 Spells' in section_header:
            level = 2
        elif '## Level 3 Spells' in section_header:
            level = 3
        elif '## Level 4 Spells' in section_header:
            level = 4
        
        if level is not None:
            # Process this section
            processed_content = add_spell_links_to_section(section_content, class_name, level)
            result_parts.append(section_header + processed_content)
            i += 2
        else:
            # Not a spell section, keep as-is
            result_parts.append(section_header)
            if section_content:
                result_parts.append(section_content)
                i += 2
            else:
                i += 1
    
    # Write back
    new_content = ''.join(result_parts)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {file_path.name}")

def main():
    base_path = Path(r"C:\Users\ksist\Documents\Obsidian\DnD\Player Characters")
    
    # Process Torgga's spell list
    torgga_file = base_path / "Torgga_Brawnanvil_Spells.md"
    if torgga_file.exists():
        process_file(torgga_file, "Cleric")
    
    # Process Zephyr's spell list
    zephyr_file = base_path / "Zephyr_Sparkwhistle_Spells.md"
    if zephyr_file.exists():
        process_file(zephyr_file, "Wizard")
    
    print("\nDone! All spell links have been added.")

if __name__ == "__main__":
    main()
