#!/usr/bin/env python3
"""Generate spell list files for spellcasters"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def generate_spell_list(character_name, char_class, max_spell_level, output_path):
    """Generate a markdown spell list file for a character"""
    
    # Load spells from database
    spells_file = Path("rules_database/spells.json")
    with open(spells_file, 'r', encoding='utf-8') as f:
        all_spells = json.load(f)
    
    # Filter spells for this class and level
    class_spells = {}
    for spell_id, spell_data in all_spells.items():
        if char_class in spell_data.get('classes', []):
            level = spell_data.get('level', 0)
            if level <= max_spell_level:
                class_spells[spell_id] = spell_data
    
    # Organize by level
    spells_by_level = defaultdict(list)
    for spell_data in class_spells.values():
        level = spell_data.get('level', 0)
        spells_by_level[level].append(spell_data)
    
    # Sort spells alphabetically within each level
    for level in spells_by_level:
        spells_by_level[level].sort(key=lambda s: s['name'])
    
    # Generate markdown
    content = f"""---
character: {character_name}
class: {char_class}
max_spell_level: {max_spell_level}
type: spell_list
---

# {character_name} - Spell List

**Class:** {char_class}  
**Available Spell Levels:** 0-{max_spell_level}

---

## How to Use This List

- **Check the box** next to spells you have **prepared** (or known)
- **Cantrips (Level 0)** are always prepared
- **Clerics** can prepare a number of spells equal to WIS modifier + Cleric level
- **Wizards** know a number of spells in their spellbook (2 per level + INT modifier at level 1)

---

"""
    
    # Add spells by level
    for level in sorted(spells_by_level.keys()):
        level_name = "Cantrips" if level == 0 else f"Level {level} Spells"
        spells = spells_by_level[level]
        
        content += f"## {level_name}\n\n"
        content += f"*{len(spells)} spells available*\n\n"
        
        for spell in spells:
            school = spell.get('school', 'Unknown')
            concentration = " (C)" if spell.get('concentration') else ""
            ritual = " (R)" if spell.get('ritual') else ""
            
            content += f"- [ ] **{spell['name']}** - {school}{concentration}{ritual}\n"
        
        content += "\n"
    
    # Add legend
    content += """---

## Legend

- **(C)** = Concentration
- **(R)** = Ritual

---

## Spell Preparation Rules

### Cleric (Torgga)
- **Cantrips:** All cantrips are always prepared
- **Prepared Spells:** Can prepare WIS modifier + Cleric level = **3 + 5 = 8 spells**
- **Change Prepared Spells:** After a long rest, can change prepared spell list

### Wizard (Zephyr)
- **Cantrips:** All cantrips are always prepared
- **Spellbook:** Knows spells in spellbook (starts with 6 at level 1, gains 2 per level)
- **Prepared Spells:** Can prepare INT modifier + Wizard level = **3 + 5 = 8 spells**
- **Change Prepared Spells:** After a long rest, can change prepared spell list

---

*Check boxes to mark prepared/known spells. Update after long rests.*
"""
    
    # Write file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Generated spell list for {character_name}")
    print(f"   {sum(len(spells) for spells in spells_by_level.values())} total spells")
    print(f"   Saved to: {output_file}")
    return len(class_spells)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("\n📚 Generating Spell Lists...\n")
    
    # Torgga (Cleric 5 - has up to 3rd level spells)
    torgga_count = generate_spell_list(
        "Torgga Brawnanvil",
        "Cleric",
        3,
        "C:/Users/ksist/Documents/Obsidian/DnD/Player Characters/Torgga_Brawnanvil_Spells.md"
    )
    
    print()
    
    # Zephyr (Wizard 5 - has up to 3rd level spells)
    zephyr_count = generate_spell_list(
        "Zephyr Sparkwhistle",
        "Wizard",
        3,
        "C:/Users/ksist/Documents/Obsidian/DnD/Player Characters/Zephyr_Sparkwhistle_Spells.md"
    )
    
    print(f"\n✅ Spell lists generated!")
    print(f"   Torgga: {torgga_count} spells")
    print(f"   Zephyr: {zephyr_count} spells")

if __name__ == "__main__":
    main()




