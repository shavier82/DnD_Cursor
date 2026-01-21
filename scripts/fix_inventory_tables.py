#!/usr/bin/env python3
"""
Fix Inventory Tables - Convert list format to proper table format
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple

OBSIDIAN_VAULT = Path("C:/Users/ksist/Documents/Obsidian/DnD/Player Characters")

def parse_inventory_item(line: str) -> Dict[str, any]:
    """Parse an inventory item from list format"""
    # Format: "- Item Name - X.X lbs" or "- Item Name (xN) - X.X lbs"
    match = re.match(r'-\s*\*\*(.+?)\*\*|-\s*(.+?)\s*-\s*([\d.]+)\s*lbs', line)
    if not match:
        return None
    
    item_text = (match.group(1) or match.group(2)).strip()
    weight = float(match.group(3)) if match.group(3) else 0.0
    
    # Check for quantity in parentheses
    qty_match = re.search(r'\(x(\d+)\)', item_text)
    quantity = int(qty_match.group(1)) if qty_match else 1
    item_name = re.sub(r'\s*\(x\d+\)', '', item_text).strip()
    
    return {
        "name": item_text,  # Keep original format for now
        "quantity": quantity,
        "weight": weight
    }

def convert_inventory_to_tables(content: str) -> str:
    """Convert inventory section from list to table format"""
    
    # Find inventory section - look for "## Inventory" and capture until next ## or end of file
    inv_match = re.search(r'(## Inventory.*?)(?=\n## |\Z)', content, re.DOTALL)
    if not inv_match:
        # Try without the space after ##
        inv_match = re.search(r'(## Inventory.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not inv_match:
        return content
    
    inventory_section = inv_match.group(1)
    
    # Parse equipped and carried items
    equipped_items = []
    carried_items = []
    current_section = None
    
    for line in inventory_section.split('\n'):
        line = line.strip()
        if '### Equipped' in line:
            current_section = 'equipped'
        elif '### Carried' in line:
            current_section = 'carried'
        elif line.startswith('-') and current_section:
            item = parse_inventory_item(line)
            if item:
                if current_section == 'equipped':
                    equipped_items.append(item)
                else:
                    carried_items.append(item)
    
    # Build new inventory section with tables
    new_inventory = "## Equipment & Inventory\n\n"
    
    # Weapons table (if any weapons in equipped)
    weapons = [item for item in equipped_items if any(w in item['name'].lower() for w in ['sword', 'axe', 'mace', 'bow', 'dagger', 'rapier', 'staff', 'spear', 'javelin', 'hammer', 'warhammer', 'handaxe', 'greataxe', 'battleaxe', 'longsword', 'shortsword', 'quarterstaff'])]
    if weapons:
        new_inventory += "### Weapons\n\n"
        new_inventory += "| Weapon | Equipped | Attack | Damage | Properties | Special Effects |\n"
        new_inventory += "|--------|----------|--------|--------|------------|-----------------|\n"
        for weapon in weapons:
            # Extract weapon name (remove +1, etc. for base name)
            name = weapon['name'].replace('**', '').strip()
            new_inventory += f"| {name} | Yes | - | - | - | - |\n"
        new_inventory += "\n"
    
    # Armor & Shields table
    armor = [item for item in equipped_items if any(a in item['name'].lower() for a in ['armor', 'shield', 'mail', 'leather', 'plate', 'chain', 'breastplate', 'studded'])]
    if armor:
        new_inventory += "### Armor & Shields\n\n"
        new_inventory += "| Armor/Shield | Equipped | AC Bonus | Type | Properties | Special Effects |\n"
        new_inventory += "|--------------|----------|----------|------|------------|-----------------|\n"
        for item in armor:
            name = item['name'].replace('**', '').strip()
            # Try to extract AC bonus from name
            ac_match = re.search(r'\+(\d+)', name)
            ac_bonus = f"+{ac_match.group(1)}" if ac_match else "-"
            armor_type = "Heavy" if "chain" in name.lower() or "plate" in name.lower() else "Light" if "leather" in name.lower() else "Shield" if "shield" in name.lower() else "-"
            new_inventory += f"| {name} | Yes | {ac_bonus} | {armor_type} | - | - |\n"
        new_inventory += "\n"
    
    # Magic Items table
    magic_items = [item for item in (equipped_items + carried_items) if any(m in item['name'].lower() for m in ['+1', '+2', '+3', 'potion', 'ring', 'cloak', 'boots', 'gauntlets', 'staff', 'wand', 'scroll', 'magic'])]
    if magic_items:
        new_inventory += "### Magic Items\n\n"
        new_inventory += "| Item | Equipped/Attuned | Properties | Charges/Uses | Notes |\n"
        new_inventory += "|------|------------------|------------|--------------|-------|\n"
        for item in magic_items:
            name = item['name'].replace('**', '').strip()
            equipped = "Yes" if item in equipped_items else "No"
            new_inventory += f"| {name} | {equipped} | - | - | - |\n"
        new_inventory += "\n"
    
    # General Inventory table
    general_items = [item for item in carried_items if item not in magic_items]
    if general_items:
        new_inventory += "### General Inventory\n\n"
        new_inventory += "| Item | Quantity | Weight (lb) | Notes |\n"
        new_inventory += "|------|----------|-------------|-------|\n"
        
        # Consolidate duplicate items
        item_dict = {}
        for item in general_items:
            base_name = re.sub(r'\s*\(x\d+\)', '', item['name']).strip()
            if base_name in item_dict:
                item_dict[base_name]['quantity'] += item['quantity']
                item_dict[base_name]['weight'] += item['weight']
            else:
                item_dict[base_name] = item.copy()
                item_dict[base_name]['name'] = base_name
        
        for item in item_dict.values():
            new_inventory += f"| {item['name']} | {item['quantity']} | {item['weight']:.1f} |  |\n"
    
    # Replace inventory section
    content = content[:inv_match.start()] + new_inventory + content[inv_match.end():]
    
    return content

def fix_character_file(character_name: str):
    """Fix inventory tables for a character"""
    char_file = OBSIDIAN_VAULT / f"{character_name}.md"
    
    if not char_file.exists():
        print(f"ERROR: File not found: {char_file}")
        return False
    
    content = char_file.read_text(encoding='utf-8')
    new_content = convert_inventory_to_tables(content)
    
    if new_content != content:
        char_file.write_text(new_content, encoding='utf-8')
        print(f"OK: Fixed inventory tables for {character_name}")
        return True
    else:
        print(f"SKIP: No changes needed for {character_name}")
        return False

def main():
    """Fix inventory tables for all characters"""
    characters = [
        "Torgga_Brawnanvil",
        "Eglath_Bearkiller",
        "Brevin",
        "Vandross_Ephrates",
        "Zephyr_Sparkwhistle"
    ]
    
    print("Fixing inventory tables...\n")
    
    for char_name in characters:
        fix_character_file(char_name)
    
    print("\nDone!")

if __name__ == "__main__":
    main()
