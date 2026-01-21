#!/usr/bin/env python3
"""
Fix spell links - working version that processes all spells
"""

import re
from pathlib import Path

def fix_spells_in_file(file_path, class_name):
    """Add links to all unlinked spells"""
    print(f"Processing {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    level_map = {
        '## Cantrips': 0,
        '## Level 1 Spells': 1,
        '## Level 2 Spells': 2,
        '## Level 3 Spells': 3,
        '## Level 4 Spells': 4,
    }
    
    current_level = None
    lines = content.split('\n')
    new_lines = []
    changes_made = 0
    
    for line in lines:
        # Check if this is a level header
        level_found = False
        for level_header, level_num in level_map.items():
            if level_header in line:
                current_level = level_num
                new_lines.append(line)
                level_found = True
                break
        
        if not level_found:
            # Check if this is a spell line without a link
            if line.strip().startswith('- [') and '**' in line and '[[' not in line:
                # Extract spell name
                match = re.search(r'\*\*([^*]+)\*\*', line)
                if match:
                    spell_name = match.group(1).strip()
                    # Skip if it has special markers (Life Domain, etc.)
                    if '⭐' not in spell_name and spell_name and current_level is not None:
                        # Convert to filename
                        filename = spell_name.replace(' ', '_')
                        level_str = f"Level_{current_level}" if current_level > 0 else "Level_0"
                        link = f"[[Spell_Dictionary/{class_name}/{level_str}/{filename}|{spell_name}]]"
                        
                        # Replace spell name with link
                        new_line = line.replace(f'**{spell_name}**', f'**{link}**')
                        new_lines.append(new_line)
                        changes_made += 1
                        continue
            
            new_lines.append(line)
    
    # Write back
    new_content = '\n'.join(new_lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {file_path.name} - {changes_made} links added")

def main():
    base_path = Path(r"C:\Users\ksist\Documents\Obsidian\DnD\Player Characters")
    
    fix_spells_in_file(base_path / "Torgga_Brawnanvil_Spells.md", "Cleric")
    fix_spells_in_file(base_path / "Zephyr_Sparkwhistle_Spells.md", "Wizard")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
