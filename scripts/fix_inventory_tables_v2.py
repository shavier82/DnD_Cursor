#!/usr/bin/env python3
"""
Fix Inventory Tables V2 - Properly convert list format to table format
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

OBSIDIAN_VAULT = Path("C:/Users/ksist/Documents/Obsidian/DnD/Player Characters")

def parse_item_line(line: str) -> Dict:
    """Parse an inventory item line"""
    # Format: "- Item Name - X.X lbs" or "- **Item Name** - X.X lbs" or "- Item Name (xN) - X.X lbs"
    line = line.strip()
    if not line.startswith('-'):
        return None
    
    # Remove leading "- "
    line = line[2:].strip()
    
    # Check for bold items (equipped)
    is_bold = line.startswith('**') and line.endswith('**')
    if is_bold:
        line = line[2:-2].strip()
    
    # Split on " - " to separate item name from weight
    parts = line.split(' - ')
    if len(parts) < 2:
        return None
    
    item_text = parts[0].strip()
    weight_text = parts[-1].strip()
    
    # Extract weight
    weight_match = re.search(r'([\d.]+)', weight_text)
    weight = float(weight_match.group(1)) if weight_match else 0.0
    
    # Extract quantity from parentheses
    qty_match = re.search(r'\(x(\d+)\)', item_text)
    quantity = int(qty_match.group(1)) if qty_match else 1
    item_name = re.sub(r'\s*\(x\d+\)', '', item_text).strip()
    
    return {
        "name": item_name,
        "quantity": quantity,
        "weight": weight,
        "is_equipped": is_bold
    }

def categorize_item(item_name: str) -> str:
    """Categorize an item into weapon, armor, magic, or general"""
    name_lower = item_name.lower()
    
    # Weapons
    weapon_keywords = ['sword', 'axe', 'mace', 'bow', 'dagger', 'rapier', 'staff', 'spear', 
                      'javelin', 'hammer', 'warhammer', 'handaxe', 'greataxe', 'battleaxe', 
                      'longsword', 'shortsword', 'quarterstaff', 'crossbow', 'whip', 'flail',
                      'club', 'scimitar', 'trident', 'glaive', 'halberd', 'lance', 'pike']
    if any(kw in name_lower for kw in weapon_keywords):
        return 'weapon'
    
    # Armor & Shields
    armor_keywords = ['armor', 'shield', 'mail', 'leather', 'plate', 'chain', 'breastplate', 
                     'studded', 'scale', 'splint', 'ring', 'half plate', 'full plate']
    if any(kw in name_lower for kw in armor_keywords):
        return 'armor'
    
    # Magic Items
    magic_keywords = ['+1', '+2', '+3', 'potion', 'ring', 'cloak', 'boots', 'gauntlets', 
                     'staff', 'wand', 'scroll', 'magic', 'amulet', 'bracers', 'belt']
    if any(kw in name_lower for kw in magic_keywords):
        return 'magic'
    
    return 'general'

def consolidate_items(items: List[Dict]) -> Dict[str, Dict]:
    """Consolidate duplicate items"""
    consolidated = {}
    for item in items:
        base_name = item['name']
        if base_name in consolidated:
            consolidated[base_name]['quantity'] += item['quantity']
            consolidated[base_name]['weight'] += item['weight']
        else:
            consolidated[base_name] = item.copy()
    return consolidated

def convert_inventory_section(content: str) -> str:
    """Convert inventory section from list to table format"""
    
    # Find the inventory section
    inv_start = content.find('## Inventory')
    if inv_start == -1:
        print("  DEBUG: Could not find '## Inventory' section")
        return content
    
    # Find where inventory section ends (next ## or end of file)
    remaining = content[inv_start + 12:]  # Skip past "## Inventory"
    inv_end_match = re.search(r'\n## ', remaining)
    if inv_end_match:
        inv_end = inv_start + 12 + inv_end_match.start()
    else:
        inv_end = len(content)
    
    inventory_section = content[inv_start:inv_end]
    print(f"  DEBUG: Found inventory section from {inv_start} to {inv_end}, length {len(inventory_section)}")
    
    # Parse all items
    all_items = []
    current_section = None
    
    for line in inventory_section.split('\n'):
        line_stripped = line.strip()
        if '### Equipped' in line_stripped:
            current_section = 'equipped'
            continue
        elif '### Carried' in line_stripped:
            current_section = 'carried'
            continue
        elif line_stripped.startswith('-'):
            item = parse_item_line(line_stripped)
            if item:
                all_items.append(item)
    
    # Separate equipped and carried
    equipped_items = [item for item in all_items if item['is_equipped']]
    carried_items = [item for item in all_items if not item['is_equipped']]
    
    # Categorize items
    weapons = []
    armor = []
    magic_items = []
    general_items = []
    
    for item in equipped_items + carried_items:
        category = categorize_item(item['name'])
        if category == 'weapon':
            weapons.append(item)
        elif category == 'armor':
            armor.append(item)
        elif category == 'magic':
            magic_items.append(item)
        else:
            general_items.append(item)
    
    # Build new inventory section
    new_section = "## Equipment & Inventory\n\n"
    
    # Weapons table
    if weapons:
        new_section += "### Weapons\n\n"
        new_section += "| Weapon | Equipped | Attack | Damage | Properties | Special Effects |\n"
        new_section += "|--------|----------|--------|--------|------------|-----------------|\n"
        
        # Consolidate weapons
        weapons_consolidated = consolidate_items(weapons)
        for item in weapons_consolidated.values():
            name = item['name']
            equipped = "Yes" if item['is_equipped'] else "No"
            # Try to extract attack/damage from name if it's a magic weapon
            attack = "-"
            damage = "-"
            if "+" in name:
                plus_match = re.search(r'\+(\d+)', name)
                if plus_match:
                    bonus = plus_match.group(1)
                    attack = f"+{bonus}"
                    damage = f"1d8+{bonus}"  # Default, should be customized
            new_section += f"| {name} | {equipped} | {attack} | {damage} | - | - |\n"
        new_section += "\n"
    
    # Armor & Shields table
    if armor:
        new_section += "### Armor & Shields\n\n"
        new_section += "| Armor/Shield | Equipped | AC Bonus | Type | Properties | Special Effects |\n"
        new_section += "|--------------|----------|----------|------|------------|-----------------|\n"
        
        armor_consolidated = consolidate_items(armor)
        for item in armor_consolidated.values():
            name = item['name']
            equipped = "Yes" if item['is_equipped'] else "No"
            # Try to extract AC bonus
            ac_bonus = "-"
            armor_type = "-"
            name_lower = name.lower()
            if "shield" in name_lower:
                armor_type = "Shield"
                if "+" in name:
                    plus_match = re.search(r'\+(\d+)', name)
                    if plus_match:
                        ac_bonus = f"+{plus_match.group(1)}"
                    else:
                        ac_bonus = "+2"
                else:
                    ac_bonus = "+2"
            elif "chain mail" in name_lower or "chain" in name_lower:
                armor_type = "Heavy"
                ac_bonus = "16"
            elif "leather" in name_lower:
                armor_type = "Light"
                ac_bonus = "11"
            elif "studded" in name_lower:
                armor_type = "Light"
                ac_bonus = "12"
            elif "plate" in name_lower:
                armor_type = "Heavy"
                ac_bonus = "18"
            elif "breastplate" in name_lower:
                armor_type = "Medium"
                ac_bonus = "14"
            
            new_section += f"| {name} | {equipped} | {ac_bonus} | {armor_type} | - | - |\n"
        new_section += "\n"
    
    # Magic Items table
    if magic_items:
        new_section += "### Magic Items\n\n"
        new_section += "| Item | Equipped/Attuned | Properties | Charges/Uses | Notes |\n"
        new_section += "|------|------------------|------------|--------------|-------|\n"
        
        magic_consolidated = consolidate_items(magic_items)
        for item in magic_consolidated.values():
            name = item['name']
            equipped = "Yes" if item['is_equipped'] else "No"
            new_section += f"| {name} | {equipped} | - | - | - |\n"
        new_section += "\n"
    
    # General Inventory table
    if general_items:
        new_section += "### General Inventory\n\n"
        new_section += "| Item | Quantity | Weight (lb) | Notes |\n"
        new_section += "|------|----------|-------------|-------|\n"
        
        general_consolidated = consolidate_items(general_items)
        for item in sorted(general_consolidated.values(), key=lambda x: x['name']):
            name = item['name']
            quantity = item['quantity']
            weight = item['weight']
            new_section += f"| {name} | {quantity} | {weight:.1f} |  |\n"
    
    # Replace the inventory section
    new_content = content[:inv_start] + new_section + content[inv_end:]
    
    return new_content

def fix_character_file(character_name: str):
    """Fix inventory tables for a character"""
    char_file = OBSIDIAN_VAULT / f"{character_name}.md"
    
    if not char_file.exists():
        print(f"ERROR: File not found: {char_file}")
        return False
    
    content = char_file.read_text(encoding='utf-8')
    new_content = convert_inventory_section(content)
    
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
