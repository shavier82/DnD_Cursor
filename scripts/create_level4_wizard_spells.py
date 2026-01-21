#!/usr/bin/env python3
"""
Create spell files for all 4th-level Wizard spells.
"""

import json
import re
from pathlib import Path
import sys

# Base paths
BASE_PATH = Path(r"C:\Users\ksist\Documents\Obsidian\DnD\Player Characters")
SPELL_DICT_PATH = BASE_PATH / "Spell_Dictionary" / "Wizard" / "Level_4"
RULES_DB = Path(r"C:\DnD\DnD_Cursor\rules_database\spells.json")
SPELLS_BY_CLASS = Path(r"C:\DnD\DnD_Cursor\rules_database\spells_by_class.json")

def load_databases():
    """Load spells databases"""
    with open(RULES_DB, 'r', encoding='utf-8') as f:
        spells_db = json.load(f)
    with open(SPELLS_BY_CLASS, 'r', encoding='utf-8') as f:
        spells_by_class = json.load(f)
    return spells_db, spells_by_class

def get_spell_id_from_name(spell_name):
    """Convert spell name to spell_id format"""
    special_cases = {
        "Evard's Black Tentacles": "evards_black_tentacles",
        "Leomund's Secret Chest": "leomunds_secret_chest",
        "Mordenkainen's Faithful Hound": "mordenkainens_faithful_hound",
        "Mordenkainen's Private Sanctum": "mordenkainens_private_sanctum",
        "Otiluke's Resilient Sphere": "otilukes_resilient_sphere"
    }
    
    if spell_name in special_cases:
        return special_cases[spell_name]
    
    return spell_name.lower().replace(' ', '_').replace("'", "").replace("/", "_")

def create_spell_file(spell_name, spell_info, spells_db):
    """Create a spell markdown file"""
    spell_id = get_spell_id_from_name(spell_name)
    
    # Get full spell details
    full_spell = spells_db.get(spell_id)
    if not full_spell:
        # Try to find by name match
        for s_id, spell in spells_db.items():
            if spell['name'].lower() == spell_name.lower():
                full_spell = spell
                break
    
    if not full_spell:
        print(f"Warning: Could not find full details for {spell_name}")
        return False
    
    # Create filename
    filename = spell_name.replace("'", "").replace(" ", "_").replace("/", "_") + ".md"
    filepath = SPELL_DICT_PATH / filename
    
    # Extract properties
    concentration = full_spell.get('concentration', False)
    ritual = full_spell.get('ritual', False)
    material = full_spell.get('material', False)
    school = full_spell.get('school', 'Unknown')
    level = full_spell.get('level', 4)
    
    # Build components string
    components_list = []
    if concentration:
        components_list.append("Concentration")
    if ritual:
        components_list.append("Ritual")
    if material:
        components_list.append("Material")
    components_str = ", ".join(components_list) if components_list else "None"
    
    # Get spell details
    casting_time = full_spell.get('casting_time', 'Not available')
    range_info = full_spell.get('range', 'Not available')
    components_full = full_spell.get('components', 'Not available')
    duration = full_spell.get('duration', 'Not available')
    description = full_spell.get('description', 'Not available')
    at_higher_levels = full_spell.get('at_higher_levels', '')
    
    # Create frontmatter
    frontmatter = f"""---
spell_name: {spell_name}
spell_level: {level}
spell_school: {school}
spell_class: Wizard
properties: {components_str}
---"""
    
    # Create content
    level_text = f"Level {level}"
    concentration_str = 'Yes' if concentration else 'No'
    ritual_str = 'Yes' if ritual else 'No'
    
    content = f"""{frontmatter}

# {spell_name}

**Level:** {level_text}  
**School:** {school}  
**Class:** Wizard

## Properties

- **{components_str}**

## Spell Details

**Casting Time:** {casting_time}

**Range:** {range_info}

**Components:** {components_full}

**Duration:** {duration}

**Description:**

{description}"""

    if at_higher_levels:
        content += f"""

**At Higher Levels:**

{at_higher_levels}"""

    content += f"""

## Quick Reference

- **Concentration:** {concentration_str}
- **Ritual:** {ritual_str}
- **Material Components:** {'Yes' if material else 'No'}

## Quick Links

← **[[Zephyr_Sparkwhistle_Spells#Level 4 Spells|Back to Wizard Spell List]]**

---

*This spell file links back to the spellcaster's spell list. Full spell details are available via MCP tools during gameplay.*
"""
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    """Main function"""
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Load databases
    spells_db, spells_by_class = load_databases()
    
    # Get all 4th-level Wizard spells
    wizard_level4 = spells_by_class.get('wizard', {}).get('4', [])
    
    if not wizard_level4:
        print("No 4th-level Wizard spells found!")
        return
    
    print(f"Creating {len(wizard_level4)} 4th-level Wizard spell files...")
    
    created = 0
    for spell_data in wizard_level4:
        spell_name = spell_data['name']
        if create_spell_file(spell_name, spell_data, spells_db):
            created += 1
            print(f"✓ Created: {spell_name}")
        else:
            print(f"✗ Failed: {spell_name}")
    
    print(f"\n✅ Complete! Created {created}/{len(wizard_level4)} spell files.")

if __name__ == "__main__":
    main()
