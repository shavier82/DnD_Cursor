#!/usr/bin/env python3
"""
Obsidian Sync MCP Server for D&D Campaigns
Manages character sheets, NPCs, and campaign data in Obsidian vault.
"""

import sys
import json
import re
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
except ImportError:
    print("ERROR: mcp package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

class ObsidianSyncServer:
    def __init__(self):
        self.vault_path = Path("C:/Users/ksist/Documents/Obsidian")
        
    def read_character_file(self, character_name: str) -> Optional[str]:
        """Read a character's markdown file."""
        char_file = self.vault_path / "DnD" / "Player Characters" / f"{character_name}.md"
        if char_file.exists():
            return char_file.read_text(encoding="utf-8")
        return None
    
    def write_character_file(self, character_name: str, content: str):
        """Write to a character's markdown file."""
        char_file = self.vault_path / "DnD" / "Player Characters" / f"{character_name}.md"
        char_file.parent.mkdir(parents=True, exist_ok=True)
        char_file.write_text(content, encoding="utf-8")
    
    def update_character_hp(self, character_name: str, new_hp: int, max_hp: int) -> dict:
        """Update character's HP in their sheet."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        # Update HP line
        content = re.sub(
            r'HP:.*',
            f'HP: {new_hp}/{max_hp}',
            content
        )
        
        self.write_character_file(character_name, content)
        return {
            "success": True,
            "character": character_name,
            "hp": f"{new_hp}/{max_hp}"
        }
    
    def update_character_xp(self, character_name: str, xp_to_add: int) -> dict:
        """Add XP to a character."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        # Find current XP
        xp_match = re.search(r'XP:\s*(\d+)', content)
        if xp_match:
            current_xp = int(xp_match.group(1))
            new_xp = current_xp + xp_to_add
            content = re.sub(r'XP:\s*\d+', f'XP: {new_xp}', content)
        else:
            # Add XP line if not found
            content += f"\nXP: {xp_to_add}\n"
            new_xp = xp_to_add
        
        self.write_character_file(character_name, content)
        return {
            "success": True,
            "character": character_name,
            "xp_added": xp_to_add,
            "total_xp": new_xp
        }
    
    def update_character_currency(self, character_name: str, cp: int = 0, sp: int = 0, 
                                   gp: int = 0, pp: int = 0) -> dict:
        """Add currency to a character (accumulates, doesn't replace).
        
        Supports all currency types: Platinum (pp), Gold (gp), Silver (sp), Copper (cp).
        Looks for format: - **Platinum:** X pp, - **Gold:** X gp, etc.
        """
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        # Try multi-line format first (format: "- **Gold:** 6,074 gp" etc.)
        platinum_pattern = r'-\s*\*\*Platinum:\*\*\s*([0-9,]+)\s*pp'
        gold_pattern = r'-\s*\*\*Gold:\*\*\s*([0-9,]+)\s*gp'
        silver_pattern = r'-\s*\*\*Silver:\*\*\s*(\d+)\s*sp'
        copper_pattern = r'-\s*\*\*Copper:\*\*\s*(\d+)\s*cp'
        
        platinum_match = re.search(platinum_pattern, content)
        gold_match = re.search(gold_pattern, content)
        silver_match = re.search(silver_pattern, content)
        copper_match = re.search(copper_pattern, content)
        
        if platinum_match or gold_match or silver_match or copper_match:
            # Multi-line format found - parse and update each line
            current_pp = int(platinum_match.group(1).replace(',', '')) if platinum_match else 0
            current_gp = int(gold_match.group(1).replace(',', '')) if gold_match else 0
            current_sp = int(silver_match.group(1)) if silver_match else 0
            current_cp = int(copper_match.group(1)) if copper_match else 0
            
            # Add new currency
            new_pp = current_pp + pp
            new_gp = current_gp + gp
            new_sp = current_sp + sp
            new_cp = current_cp + cp
            
            # Format with commas for readability
            new_pp_str = f"{new_pp:,}"
            new_gp_str = f"{new_gp:,}"
            
            # Update each currency line (in order: Platinum, Gold, Silver, Copper)
            if platinum_match:
                content = re.sub(platinum_pattern, f'- **Platinum:** {new_pp_str} pp', content)
            elif pp > 0 or new_pp > 0:
                # Platinum line doesn't exist but we're adding platinum - insert it before Gold
                if "### Currency" in content:
                    currency_section = content.find("### Currency")
                    # Find where to insert (before first currency line or after header)
                    gold_line = content.find("- **Gold:", currency_section)
                    silver_line = content.find("- **Silver:", currency_section)
                    copper_line = content.find("- **Copper:", currency_section)
                    
                    # Find the earliest currency line to insert before it
                    insert_pos = -1
                    for line_pos in [gold_line, silver_line, copper_line]:
                        if line_pos != -1:
                            if insert_pos == -1 or line_pos < insert_pos:
                                insert_pos = line_pos
                    
                    if insert_pos != -1:
                        # Insert before the first existing currency line
                        content = content[:insert_pos] + f"- **Platinum:** {new_pp_str} pp\n" + content[insert_pos:]
                    else:
                        # No currency lines found, add after Currency header (skip blank line if present)
                        header_end = content.find("\n", currency_section)
                        if header_end != -1:
                            # Check if next line is blank
                            next_char = content[header_end + 1] if header_end + 1 < len(content) else ''
                            if next_char == '\n':
                                # Skip the blank line
                                content = content[:header_end + 2] + f"- **Platinum:** {new_pp_str} pp\n" + content[header_end + 2:]
                            else:
                                content = content[:header_end + 1] + f"\n- **Platinum:** {new_pp_str} pp" + content[header_end + 1:]
                        else:
                            # Fallback: append after Currency header
                            content = content[:currency_section] + f"### Currency\n\n- **Platinum:** {new_pp_str} pp\n" + content[currency_section + len("### Currency"):]
            
            if gold_match:
                content = re.sub(gold_pattern, f'- **Gold:** {new_gp_str} gp', content)
            elif gp > 0:
                # Gold line doesn't exist but we're adding gold - add it
                if "### Currency" in content:
                    currency_section = content.find("### Currency")
                    next_section = content.find("##", currency_section + 1)
                    if next_section == -1:
                        next_section = len(content)
                    content = content[:next_section] + f"\n- **Gold:** {new_gp_str} gp" + content[next_section:]
            
            if silver_match:
                content = re.sub(silver_pattern, f'- **Silver:** {new_sp} sp', content)
            elif sp > 0:
                # Silver line doesn't exist but we're adding silver - add it
                if "### Currency" in content:
                    currency_section = content.find("### Currency")
                    next_section = content.find("##", currency_section + 1)
                    if next_section == -1:
                        next_section = len(content)
                    content = content[:next_section] + f"\n- **Silver:** {new_sp} sp" + content[next_section:]
            
            if copper_match:
                content = re.sub(copper_pattern, f'- **Copper:** {new_cp} cp', content)
            elif cp > 0:
                # Copper line doesn't exist but we're adding copper - add it
                if "### Currency" in content:
                    currency_section = content.find("### Currency")
                    next_section = content.find("##", currency_section + 1)
                    if next_section == -1:
                        next_section = len(content)
                    content = content[:next_section] + f"\n- **Copper:** {new_cp} cp" + content[next_section:]
        else:
            # Try single-line format (format: "- **4,807 gp, 7 sp, 5 cp**")
            currency_pattern = r'-\s*\*\*([0-9,]+)\s*gp,\s*(\d+)\s*sp,\s*(\d+)\s*cp'
        match = re.search(currency_pattern, content)
        
        if match:
            # Parse current currency
            current_gp = int(match.group(1).replace(',', ''))
            current_sp = int(match.group(2))
            current_cp = int(match.group(3))
            
            # Add new currency (single-line format doesn't track platinum, so start from 0)
            new_pp = pp  # New platinum (wasn't in old format)
            new_gp = current_gp + gp
            new_sp = current_sp + sp
            new_cp = current_cp + cp
            
            # Format with commas for readability
            new_gp_str = f"{new_gp:,}"
            
            # Update content (keep single-line format, but we'll track pp separately)
            content = re.sub(
                currency_pattern,
                f'- **{new_gp_str} gp, {new_sp} sp, {new_cp} cp**',
                content
            )
            
            # If we're adding platinum, add it as a new line
            if pp > 0:
                if "### Currency" in content:
                    currency_section = content.find("### Currency")
                    next_section = content.find("##", currency_section + 1)
                    if next_section == -1:
                        next_section = len(content)
                    content = content[:next_section] + f"\n- **Platinum:** {pp:,} pp" + content[next_section:]
        else:
            # Currency not found, add new lines in Currency section (in order: Platinum, Gold, Silver, Copper)
            currency_lines = []
            if pp > 0:
                currency_lines.append(f"- **Platinum:** {pp:,} pp")
            if gp > 0:
                currency_lines.append(f"- **Gold:** {gp:,} gp")
            if sp > 0:
                currency_lines.append(f"- **Silver:** {sp} sp")
            if cp > 0:
                currency_lines.append(f"- **Copper:** {cp} cp")
            
            if "### Currency" in content:
                currency_section = content.find("### Currency")
                next_section = content.find("##", currency_section + 1)
                if next_section == -1:
                    next_section = len(content)
                content = content[:next_section] + "\n" + "\n".join(currency_lines) + content[next_section:]
            else:
                content += f"\n### Currency\n" + "\n".join(currency_lines) + "\n"
            new_pp, new_gp, new_sp, new_cp = pp, gp, sp, cp
        
        # Ensure new_pp is defined if we didn't set it above
        if 'new_pp' not in locals():
            new_pp = pp
        
        self.write_character_file(character_name, content)
        
        # Build return message with all currency types
        currency_parts = []
        if new_pp > 0:
            currency_parts.append(f"{new_pp:,} pp")
        if new_gp > 0:
            currency_parts.append(f"{new_gp:,} gp")
        if new_sp > 0:
            currency_parts.append(f"{new_sp} sp")
        if new_cp > 0:
            currency_parts.append(f"{new_cp} cp")
        
        return {
            "success": True,
            "character": character_name,
            "new_total": ", ".join(currency_parts) if currency_parts else "0"
        }
    
    def add_inventory_item(self, character_name: str, item_name: str, quantity: int = 1, weight: float = 0) -> dict:
        """Add an item to character's General Inventory table (with quantity and weight).
        
        Uses line-by-line parsing for reliability (no regex bugs).
        """
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        lines = content.split('\n')
        modified = False
        
        # Find "### General Inventory" section
        general_inv_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "### General Inventory":
                general_inv_idx = i
                break
        
        if general_inv_idx == -1:
            # No General Inventory section - create one at the end
            if not lines[-1].strip():
                lines = lines[:-1]  # Remove trailing blank line
            
            lines.extend([
                "",
                "### General Inventory",
                "",
                "| Item | Quantity | Weight (lb) | Notes |",
                "|------|----------|-------------|-------|",
                f"| {item_name} | {quantity} | {weight} |  |",
                ""
            ])
            modified = True
        else:
            # Find the table header (should be right after section header)
            table_start_idx = -1
            for i in range(general_inv_idx + 1, len(lines)):
                if "| Item | Quantity | Weight" in lines[i]:
                    table_start_idx = i
                    break
            
            if table_start_idx == -1:
                return {"error": "General Inventory section exists but no table found"}
            
            # Find the separator line (should be right after header)
            separator_idx = table_start_idx + 1
            if separator_idx >= len(lines) or not lines[separator_idx].strip().startswith('|---'):
                return {"error": "Invalid table format - missing separator"}
            
            # Find all table rows (lines starting with | that aren't header/separator)
            table_end_idx = separator_idx + 1
            existing_item_idx = -1
            
            for i in range(separator_idx + 1, len(lines)):
                line = lines[i].strip()
                if not line or not line.startswith('|'):
                    # End of table
                    table_end_idx = i
                    break
                
                # Check if this row contains our item
                if f"| {item_name} |" in line:
                    existing_item_idx = i
                    # Don't break - keep finding table end
            else:
                # Reached end of file
                table_end_idx = len(lines)
            
            if existing_item_idx != -1:
                # Item exists - update quantity and weight
                parts = lines[existing_item_idx].split('|')
                if len(parts) >= 5:
                    # Parse existing values
                    try:
                        existing_qty = int(parts[2].strip())
                        existing_weight = float(parts[3].strip())
                        existing_notes = parts[4].strip()
                        
                        new_qty = existing_qty + quantity
                        new_weight = existing_weight + weight
                        
                        # Update the line
                        lines[existing_item_idx] = f"| {item_name} | {new_qty} | {new_weight} | {existing_notes} |"
                        modified = True
                    except (ValueError, IndexError):
                        return {"error": f"Could not parse existing item row: {lines[existing_item_idx]}"}
            else:
                # Item doesn't exist - insert new row at table_end_idx
                new_row = f"| {item_name} | {quantity} | {weight} |  |"
                lines.insert(table_end_idx, new_row)
                modified = True
        
        if modified:
            new_content = '\n'.join(lines)
            self.write_character_file(character_name, new_content)
            # Automatically recalculate total weight
            self.calculate_and_update_weight(character_name)
        
        return {
            "success": True,
            "character": character_name,
            "item": item_name,
            "quantity": quantity,
            "weight": weight
        }
    
    def remove_inventory_item(self, character_name: str, item_name: str, quantity: int = 1) -> dict:
        """Remove an item from character's General Inventory (or reduce quantity)."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        lines = content.split('\n')
        
        # Find "### General Inventory" section
        general_inv_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "### General Inventory":
                general_inv_idx = i
                break
        
        if general_inv_idx == -1:
            return {"error": "General Inventory section not found"}
        
        # Find table
        table_start_idx = -1
        for i in range(general_inv_idx + 1, len(lines)):
            if "| Item | Quantity | Weight" in lines[i]:
                table_start_idx = i
                break
        
        if table_start_idx == -1:
            return {"error": "General Inventory table not found"}
        
        separator_idx = table_start_idx + 1
        
        # Find the item
        item_idx = -1
        for i in range(separator_idx + 1, len(lines)):
            line = lines[i].strip()
            if not line or not line.startswith('|'):
                break
            if f"| {item_name} |" in line:
                item_idx = i
                break
        
        if item_idx == -1:
            return {"error": f"Item '{item_name}' not found in inventory"}
        
        # Parse current quantity
        parts = lines[item_idx].split('|')
        if len(parts) >= 5:
            try:
                current_qty = int(parts[2].strip())
                current_weight = float(parts[3].strip())
                
                if current_qty <= quantity:
                    # Remove item completely
                    lines.pop(item_idx)
                    message = f"Removed {item_name} (all {current_qty})"
                else:
                    # Reduce quantity
                    new_qty = current_qty - quantity
                    # Adjust weight proportionally
                    weight_per_item = current_weight / current_qty
                    new_weight = weight_per_item * new_qty
                    notes = parts[4].strip()
                    lines[item_idx] = f"| {item_name} | {new_qty} | {new_weight:.1f} | {notes} |"
                    message = f"Removed {quantity}x {item_name} ({new_qty} remaining)"
                
                new_content = '\n'.join(lines)
                self.write_character_file(character_name, new_content)
                # Automatically recalculate total weight
                self.calculate_and_update_weight(character_name)
                
                return {
                    "success": True,
                    "character": character_name,
                    "item": item_name,
                    "quantity_removed": quantity,
                    "message": message
                }
            except (ValueError, IndexError) as e:
                return {"error": f"Could not parse item row: {str(e)}"}
        
        return {"error": "Invalid item row format"}
    
    def add_weapon(self, character_name: str, weapon_name: str, attack_bonus: int, 
                   damage: str, properties: str = "-", special_effects: str = "-",
                   equipped: bool = False) -> dict:
        """Add a weapon to character's Weapons table."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        lines = content.split('\n')
        
        # Find "### Weapons" section
        weapons_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "### Weapons":
                weapons_idx = i
                break
        
        if weapons_idx == -1:
            return {"error": "Weapons section not found"}
        
        # Find table
        table_start_idx = -1
        for i in range(weapons_idx + 1, len(lines)):
            if "| Weapon | Equipped | Attack | Damage" in lines[i]:
                table_start_idx = i
                break
        
        if table_start_idx == -1:
            return {"error": "Weapons table not found"}
        
        separator_idx = table_start_idx + 1
        
        # Find end of table
        table_end_idx = separator_idx + 1
        for i in range(separator_idx + 1, len(lines)):
            line = lines[i].strip()
            if not line or not line.startswith('|'):
                table_end_idx = i
                break
        
        # Add new weapon row
        equipped_str = "Yes" if equipped else "No"
        new_row = f"| {weapon_name} | {equipped_str} | +{attack_bonus} | {damage} | {properties} | {special_effects} |"
        lines.insert(table_end_idx, new_row)
        
        new_content = '\n'.join(lines)
        self.write_character_file(character_name, new_content)
        
        return {
            "success": True,
            "character": character_name,
            "weapon": weapon_name,
            "equipped": equipped
        }
    
    def remove_weapon(self, character_name: str, weapon_name: str) -> dict:
        """Remove a weapon from character's Weapons table."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        lines = content.split('\n')
        
        # Find "### Weapons" section
        weapons_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "### Weapons":
                weapons_idx = i
                break
        
        if weapons_idx == -1:
            return {"error": "Weapons section not found"}
        
        # Find the weapon
        weapon_idx = -1
        for i in range(weapons_idx, len(lines)):
            if f"| {weapon_name} |" in lines[i]:
                weapon_idx = i
                break
        
        if weapon_idx == -1:
            return {"error": f"Weapon '{weapon_name}' not found"}
        
        lines.pop(weapon_idx)
        
        new_content = '\n'.join(lines)
        self.write_character_file(character_name, new_content)
        
        return {
            "success": True,
            "character": character_name,
            "weapon": weapon_name,
            "message": f"Removed {weapon_name}"
        }
    
    def equip_weapon(self, character_name: str, weapon_name: str, equipped: bool = True) -> dict:
        """Toggle equipped status for a weapon."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        lines = content.split('\n')
        
        # Find the weapon
        weapon_idx = -1
        for i, line in enumerate(lines):
            if "### Weapons" in line:
                # Start searching from weapons section
                for j in range(i, len(lines)):
                    if f"| {weapon_name} |" in lines[j]:
                        weapon_idx = j
                        break
                break
        
        if weapon_idx == -1:
            return {"error": f"Weapon '{weapon_name}' not found"}
        
        # Toggle equipped status
        parts = lines[weapon_idx].split('|')
        if len(parts) >= 3:
            equipped_str = "Yes" if equipped else "No"
            parts[2] = f" {equipped_str} "
            lines[weapon_idx] = '|'.join(parts)
            
            new_content = '\n'.join(lines)
            self.write_character_file(character_name, new_content)
            
            return {
                "success": True,
                "character": character_name,
                "weapon": weapon_name,
                "equipped": equipped
            }
        
        return {"error": "Invalid weapon row format"}
    
    def add_armor(self, character_name: str, armor_name: str, ac_bonus: int,
                  armor_type: str, properties: str = "-", special_effects: str = "-",
                  equipped: bool = False) -> dict:
        """Add armor to character's Armor & Shields table."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        lines = content.split('\n')
        
        # Find "### Armor & Shields" section
        armor_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "### Armor & Shields":
                armor_idx = i
                break
        
        if armor_idx == -1:
            return {"error": "Armor & Shields section not found"}
        
        # Find table
        table_start_idx = -1
        for i in range(armor_idx + 1, len(lines)):
            if "| Armor/Shield | Equipped | AC Bonus" in lines[i]:
                table_start_idx = i
                break
        
        if table_start_idx == -1:
            return {"error": "Armor & Shields table not found"}
        
        separator_idx = table_start_idx + 1
        
        # Find end of table
        table_end_idx = separator_idx + 1
        for i in range(separator_idx + 1, len(lines)):
            line = lines[i].strip()
            if not line or not line.startswith('|'):
                table_end_idx = i
                break
        
        # Add new armor row
        equipped_str = "Yes" if equipped else "No"
        ac_display = f"+{ac_bonus}" if ac_bonus > 0 else str(ac_bonus)
        new_row = f"| {armor_name} | {equipped_str} | {ac_display} | {armor_type} | {properties} | {special_effects} |"
        lines.insert(table_end_idx, new_row)
        
        new_content = '\n'.join(lines)
        self.write_character_file(character_name, new_content)
        
        return {
            "success": True,
            "character": character_name,
            "armor": armor_name,
            "equipped": equipped
        }
    
    def remove_armor(self, character_name: str, armor_name: str) -> dict:
        """Remove armor from character's Armor & Shields table."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        lines = content.split('\n')
        
        # Find the armor
        armor_idx = -1
        for i, line in enumerate(lines):
            if "### Armor & Shields" in line:
                for j in range(i, len(lines)):
                    if f"| {armor_name} |" in lines[j]:
                        armor_idx = j
                        break
                break
        
        if armor_idx == -1:
            return {"error": f"Armor '{armor_name}' not found"}
        
        lines.pop(armor_idx)
        
        new_content = '\n'.join(lines)
        self.write_character_file(character_name, new_content)
        
        return {
            "success": True,
            "character": character_name,
            "armor": armor_name,
            "message": f"Removed {armor_name}"
        }
    
    def equip_armor(self, character_name: str, armor_name: str, equipped: bool = True) -> dict:
        """Toggle equipped status for armor."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        lines = content.split('\n')
        
        # Find the armor
        armor_idx = -1
        for i, line in enumerate(lines):
            if "### Armor & Shields" in line:
                for j in range(i, len(lines)):
                    if f"| {armor_name} |" in lines[j]:
                        armor_idx = j
                        break
                break
        
        if armor_idx == -1:
            return {"error": f"Armor '{armor_name}' not found"}
        
        # Toggle equipped status
        parts = lines[armor_idx].split('|')
        if len(parts) >= 3:
            equipped_str = "Yes" if equipped else "No"
            parts[2] = f" {equipped_str} "
            lines[armor_idx] = '|'.join(parts)
            
            new_content = '\n'.join(lines)
            self.write_character_file(character_name, new_content)
            
            return {
                "success": True,
                "character": character_name,
                "armor": armor_name,
                "equipped": equipped
            }
        
        return {"error": "Invalid armor row format"}
    
    def add_magic_item(self, character_name: str, item_name: str, properties: str,
                       charges: str = "-", notes: str = "-", attuned: bool = False) -> dict:
        """Add a magic item to character's Magic Items table."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        lines = content.split('\n')
        
        # Find "### Magic Items" section
        magic_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "### Magic Items":
                magic_idx = i
                break
        
        if magic_idx == -1:
            return {"error": "Magic Items section not found"}
        
        # Find table
        table_start_idx = -1
        for i in range(magic_idx + 1, len(lines)):
            if "| Item | Equipped/Attuned | Properties" in lines[i]:
                table_start_idx = i
                break
        
        if table_start_idx == -1:
            return {"error": "Magic Items table not found"}
        
        separator_idx = table_start_idx + 1
        
        # Find end of table
        table_end_idx = separator_idx + 1
        for i in range(separator_idx + 1, len(lines)):
            line = lines[i].strip()
            if not line or not line.startswith('|'):
                table_end_idx = i
                break
        
        # Add new magic item row
        attuned_str = "Yes" if attuned else "No"
        new_row = f"| {item_name} | {attuned_str} | {properties} | {charges} | {notes} |"
        lines.insert(table_end_idx, new_row)
        
        new_content = '\n'.join(lines)
        self.write_character_file(character_name, new_content)
        
        return {
            "success": True,
            "character": character_name,
            "item": item_name,
            "attuned": attuned
        }
    
    def remove_magic_item(self, character_name: str, item_name: str) -> dict:
        """Remove a magic item from character's Magic Items table."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        lines = content.split('\n')
        
        # Find the magic item
        item_idx = -1
        for i, line in enumerate(lines):
            if "### Magic Items" in line:
                for j in range(i, len(lines)):
                    if f"| {item_name} |" in lines[j]:
                        item_idx = j
                        break
                break
        
        if item_idx == -1:
            return {"error": f"Magic item '{item_name}' not found"}
        
        lines.pop(item_idx)
        
        new_content = '\n'.join(lines)
        self.write_character_file(character_name, new_content)
        
        return {
            "success": True,
            "character": character_name,
            "item": item_name,
            "message": f"Removed {item_name}"
        }
    
    def attune_item(self, character_name: str, item_name: str, attuned: bool = True) -> dict:
        """Toggle attuned status for a magic item."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        lines = content.split('\n')
        
        # Find the magic item
        item_idx = -1
        for i, line in enumerate(lines):
            if "### Magic Items" in line:
                for j in range(i, len(lines)):
                    if f"| {item_name} |" in lines[j]:
                        item_idx = j
                        break
                break
        
        if item_idx == -1:
            return {"error": f"Magic item '{item_name}' not found"}
        
        # Toggle attuned status
        parts = lines[item_idx].split('|')
        if len(parts) >= 3:
            attuned_str = "Yes" if attuned else "No"
            parts[2] = f" {attuned_str} "
            lines[item_idx] = '|'.join(parts)
            
            new_content = '\n'.join(lines)
            self.write_character_file(character_name, new_content)
            
            return {
                "success": True,
                "character": character_name,
                "item": item_name,
                "attuned": attuned
            }
        
        return {"error": "Invalid magic item row format"}
    
    def create_npc(self, npc_name: str, race: str, role: str, location: str, 
                   description: str, disposition: str = "neutral") -> dict:
        """Create a new NPC in the Obsidian vault."""
        npc_file = self.vault_path / "NPCs" / f"{npc_name}.md"
        npc_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""---
name: {npc_name}
race: {race}
role: {role}
location: {location}
disposition: {disposition}
first_met: {self._get_current_date()}
---

# {npc_name}

## Basic Information
- **Race:** {race}
- **Role:** {role}
- **Location:** {location}
- **Disposition:** {disposition}

## Description
{description}

## Interactions
- First met on {self._get_current_date()}

## Knowledge
(No knowledge tracked yet)

## Relationships
(None yet)
"""
        
        npc_file.write_text(content, encoding="utf-8")
        return {
            "success": True,
            "npc": npc_name,
            "file": str(npc_file)
        }
    
    def _get_current_date(self) -> str:
        """Get current campaign date (placeholder)."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_character_combat_stats(self, character_name: str) -> dict:
        """Extract combat stats from character sheet for combat-engine."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        stats = {
            "name": character_name,
            "creature_type": "player"
        }
        
        # Extract speed
        speed_match = re.search(r'\*\*Speed:\*\*\s*(\d+)', content)
        if speed_match:
            stats["speed"] = int(speed_match.group(1))
        
        # Extract initiative bonus
        init_match = re.search(r'\*\*Initiative:\*\*\s*([+-]?\d+)', content)
        if init_match:
            stats["initiative_bonus"] = int(init_match.group(1))
        
        # Extract AC
        ac_match = re.search(r'\*\*AC:\*\*\s*(\d+)', content)
        if ac_match:
            stats["ac"] = int(ac_match.group(1))
        
        # Extract HP
        hp_match = re.search(r'\*\*HP:\s*(\d+)/(\d+)', content)
        if hp_match:
            stats["current_hp"] = int(hp_match.group(1))
            stats["max_hp"] = int(hp_match.group(2))
        
        # Extract ability scores from table
        ability_pattern = r'\|\s*(\w{3})\s*\|\s*(\d+)\s*\|\s*([+-]?\d+)\s*\|'
        for match in re.finditer(ability_pattern, content):
            ability = match.group(1).lower()
            score = int(match.group(2))
            if ability == 'str':
                stats["strength"] = score
            elif ability == 'dex':
                stats["dexterity"] = score
            elif ability == 'con':
                stats["constitution"] = score
            elif ability == 'int':
                stats["intelligence"] = score
            elif ability == 'wis':
                stats["wisdom"] = score
            elif ability == 'cha':
                stats["charisma"] = score
        
        return stats
    
    def calculate_and_update_weight(self, character_name: str, capacity: Optional[int] = None) -> dict:
        """
        Calculate total weight from inventory table and update the Total Weight line.
        For characters, calculates capacity from STR if not provided.
        For wagons/storage, uses provided capacity.
        """
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character/storage '{character_name}' not found"}
        
        lines = content.split('\n')
        total_weight = 0.0
        in_inventory = False
        header_passed = False
        
        # Find and parse inventory table
        for i, line in enumerate(lines):
            # Look for inventory section
            if "### General Inventory" in line or "## Inventory" in line:
                in_inventory = True
                header_passed = False
                continue
            
            # Check if we've left the inventory section
            if in_inventory and line.startswith("##") and "Inventory" not in line:
                break
            
            # Skip header row and separator row
            if in_inventory and line.strip().startswith("|"):
                if "Item" in line and "Quantity" in line:
                    header_passed = True
                    continue
                if line.strip().startswith("|---"):
                    continue
                
                # Parse inventory rows (after header)
                if header_passed:
                    parts = [p.strip() for p in line.split('|')]
                    # Remove empty first and last elements
                    if parts and not parts[0]:
                        parts = parts[1:]
                    if parts and not parts[-1]:
                        parts = parts[:-1]
                    
                    if len(parts) >= 3:
                        try:
                            # Column structure: Item | Quantity | Weight (lb) | Notes
                            qty_str = parts[1].strip()
                            weight_str = parts[2].strip()
                            
                            # Extract quantity (handle formats like "5" or "5 (100.0)")
                            qty_match = re.search(r'(\d+)', qty_str)
                            qty = int(qty_match.group(1)) if qty_match else 1
                            
                            # Extract weight (handle formats like "100.0" or "100")
                            weight_match = re.search(r'(\d+\.?\d*)', weight_str)
                            if weight_match:
                                weight = float(weight_match.group(1))
                                # Weight in table is total weight for that item
                                total_weight += weight
                        except (ValueError, IndexError, AttributeError):
                            pass  # Skip malformed rows
        
        # Get capacity if not provided
        if capacity is None:
            # Try to get STR from ability scores for characters
            str_match = re.search(r'STR\s*\|\s*(\d+)', content)
            if str_match:
                str_score = int(str_match.group(1))
                capacity = str_score * 15  # Carrying capacity = STR * 15
            else:
                # Try to get capacity from frontmatter (for wagons)
                capacity_match = re.search(r'capacity_lbs:\s*(\d+)', content)
                if capacity_match:
                    capacity = int(capacity_match.group(1))
                else:
                    # Fallback: try to parse from existing Total Weight line
                    existing_match = re.search(r'Total Weight.*?/\s*(\d+)', content)
                    if existing_match:
                        capacity = int(existing_match.group(1))
                    else:
                        capacity = 0  # Unknown capacity
        
        # Find and update Total Weight line
        total_weight_line_idx = -1
        for i, line in enumerate(lines):
            if "Total Weight" in line or "Current Weight" in line:
                total_weight_line_idx = i
                break
        
        # Format total weight (1 decimal place)
        total_weight_str = f"{total_weight:.1f}"
        available_space = max(0, capacity - total_weight)
        
        if total_weight_line_idx != -1:
            # Update existing line
            if capacity > 0:
                lines[total_weight_line_idx] = f"**Total Weight:** {total_weight_str} / {capacity} lbs"
            else:
                lines[total_weight_line_idx] = f"**Total Weight:** {total_weight_str} lbs"
        else:
            # Add new line after inventory section
            # Find end of inventory section
            inv_end_idx = -1
            for i, line in enumerate(lines):
                if "### General Inventory" in line or "## Inventory" in line:
                    # Find the end of the table
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].strip().startswith('|'):
                            inv_end_idx = j
                            break
                    break
            
            if inv_end_idx != -1:
                if capacity > 0:
                    lines.insert(inv_end_idx, f"**Total Weight:** {total_weight_str} / {capacity} lbs")
                else:
                    lines.insert(inv_end_idx, f"**Total Weight:** {total_weight_str} lbs")
        
        # Also update "Available Space" if it exists (for wagons)
        available_space_idx = -1
        for i, line in enumerate(lines):
            if "Available Space" in line:
                available_space_idx = i
                break
        
        if available_space_idx != -1:
            lines[available_space_idx] = f"**Available Space:** {available_space:.1f} lbs"
        
        # Write updated content
        new_content = '\n'.join(lines)
        self.write_character_file(character_name, new_content)
        
        return {
            "success": True,
            "character": character_name,
            "total_weight": total_weight,
            "capacity": capacity,
            "available_space": available_space,
            "message": f"Updated total weight: {total_weight_str} / {capacity} lbs"
        }
    
    def use_spell_slot(self, character_name: str, spell_level: int) -> dict:
        """
        Automatically deduct a spell slot when a spell is cast.
        Updates the spell slot display in Obsidian.
        """
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character '{character_name}' not found"}
        
        # Find the spell slot line for this level
        # Format: **Level X:** ●●● (3/4)
        pattern = rf'\*\*Level {spell_level}:\*\*\s*([●○]+)\s*\((\d+)/(\d+)\)'
        match = re.search(pattern, content)
        
        if not match:
            return {"error": f"Level {spell_level} spell slots not found for {character_name}"}
        
        dots = match.group(1)
        current_slots = int(match.group(2))
        max_slots = int(match.group(3))
        
        if current_slots <= 0:
            return {
                "success": False,
                "error": f"No level {spell_level} spell slots remaining",
                "character": character_name,
                "spell_level": spell_level,
                "slots_remaining": 0
            }
        
        # Deduct one slot
        new_slots = current_slots - 1
        
        # Update dots: ● for remaining, ○ for used
        new_dots = "●" * new_slots + "○" * (max_slots - new_slots)
        replacement = f'**Level {spell_level}:** {new_dots} ({new_slots}/{max_slots})'
        
        content = re.sub(pattern, replacement, content)
        self.write_character_file(character_name, content)
        
        return {
            "success": True,
            "character": character_name,
            "spell_level": spell_level,
            "slots_remaining": new_slots,
            "slots_max": max_slots,
            "message": f"Used 1 level {spell_level} spell slot. {new_slots}/{max_slots} remaining."
        }
    
    def read_vault_file(self, file_path: str) -> dict:
        """Read a file from the Obsidian vault (hardened, allowlist-only).
        
        SECURITY: Only allows reading files in the allowlist
        Blocks path traversal, absolute paths, and non-allowlisted files.
        
        Args:
            file_path: Path relative to vault root (must match allowlist exactly)
        
        Returns:
            dict with 'success', 'content', and optionally 'error'
        """
        # Hard allowlist - only these files are allowed
        # Pattern matching for battlemap files: combat_positions_<location_code>.json
        # Must match exact resources files OR battlemap pattern
        import re
        
        # Normalize path (remove leading/trailing slashes, normalize separators)
        file_path = file_path.strip().replace('\\', '/')
        if file_path.startswith('/'):
            file_path = file_path[1:]
        
        # Exact matches
        ALLOWED_EXACT = {
            "DnD/state/resources_state.json",
            "DnD/state/resources_state.sync_meta.json",
            "DnD/state/resources_state.md",  # Dashboard markdown
            "DnD/state/quests_state.json",
            "DnD/state/quests_state.sync_meta.json",
            "DnD/state/quests_state.md"  # Optional dashboard markdown
        }
        
        # Pattern matches (battlemap files)
        BATTLEMAP_PATTERN = re.compile(r"^DnD/state/combat_positions_[a-z0-9_]+\.json$")
        BATTLEMAP_META_PATTERN = re.compile(r"^DnD/state/combat_positions_[a-z0-9_]+\.sync_meta\.json$")
        
        # Boons and Rewards markdown files
        BOONS_PATTERN = re.compile(r"^DnD/Boons_And_Rewards/[a-zA-Z0-9_\-\s]+\.md$")
        
        # Security checks
        if file_path not in ALLOWED_EXACT:
            if not BATTLEMAP_PATTERN.match(file_path) and not BATTLEMAP_META_PATTERN.match(file_path) and not BOONS_PATTERN.match(file_path):
                return {"success": False, "error": f"BLOCKED: File not in allowlist: {file_path}"}
        
        # Block path traversal attempts
        if '..' in file_path or ':' in file_path or file_path.startswith('~'):
            return {"success": False, "error": "BLOCKED: Path traversal detected"}
        
        # Ensure .json or .md extension
        if not file_path.endswith('.json') and not file_path.endswith('.md'):
            return {"success": False, "error": "BLOCKED: Only .json and .md files allowed"}
        
        try:
            full_path = self.vault_path / file_path
            if not full_path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Size limit: 256 KB
            MAX_SIZE = 256 * 1024
            if full_path.stat().st_size > MAX_SIZE:
                return {"success": False, "error": f"BLOCKED: File too large (> {MAX_SIZE} bytes)"}
            
            content = full_path.read_text(encoding="utf-8")
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_vault_file(self, file_path: str, content: str) -> dict:
        """Write a file to the Obsidian vault (hardened, allowlist-only with provenance).
        
        SECURITY: Only allows writing DnD/state/resources_state.json
        Blocks path traversal, absolute paths, and non-allowlisted files.
        Writes a provenance marker file to prove sync went through MCP.
        
        Args:
            file_path: Path relative to vault root (must match allowlist exactly)
            content: File content to write
        
        Returns:
            dict with 'success' and optionally 'error'
        """
        # Hard allowlist - only specific files are allowed
        # Pattern matching for battlemap files: combat_positions_<location_code>.json
        import re
        
        MAX_SIZE = 256 * 1024  # 256 KB limit
        
        # Normalize path (remove leading/trailing slashes, normalize separators)
        file_path = file_path.strip().replace('\\', '/')
        if file_path.startswith('/'):
            file_path = file_path[1:]
        
        # Exact matches
        ALLOWED_EXACT = {
            "DnD/state/resources_state.json",
            "DnD/state/resources_state.md",  # Dashboard markdown
            "DnD/state/quests_state.json",
            "DnD/state/quests_state.md"  # Optional dashboard markdown
        }
        
        # Pattern matches (battlemap files)
        BATTLEMAP_PATTERN = re.compile(r"^DnD/state/combat_positions_[a-z0-9_]+\.json$")
        
        # Boons and Rewards markdown files
        BOONS_PATTERN = re.compile(r"^DnD/Boons_And_Rewards/[a-zA-Z0-9_\-\s]+\.md$")
        
        # Security checks
        if file_path not in ALLOWED_EXACT:
            if not BATTLEMAP_PATTERN.match(file_path) and not BOONS_PATTERN.match(file_path):
                return {"success": False, "error": f"BLOCKED: File not in allowlist: {file_path}"}
        
        # Block path traversal attempts
        if '..' in file_path or ':' in file_path or file_path.startswith('~'):
            return {"success": False, "error": "BLOCKED: Path traversal detected"}
        
        # Ensure .json or .md extension
        if not file_path.endswith('.json') and not file_path.endswith('.md'):
            return {"success": False, "error": "BLOCKED: Only .json and .md files allowed"}
        
        # Size limit check
        if len(content.encode('utf-8')) > MAX_SIZE:
            return {"success": False, "error": f"BLOCKED: Content too large (> {MAX_SIZE} bytes)"}
        
        try:
            full_path = self.vault_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            
            # Write provenance marker to prove sync went through MCP
            # This is a separate file that proves the write happened via MCP
            import datetime
            import re
            
            # Determine provenance marker path based on file_path
            # Only create provenance marker for JSON files (dashboard .md is derived, not synced independently)
            if file_path == "DnD/state/resources_state.json":
                provenance_path = self.vault_path / "DnD/state/resources_state.sync_meta.json"
            elif file_path == "DnD/state/quests_state.json":
                provenance_path = self.vault_path / "DnD/state/quests_state.sync_meta.json"
            elif re.match(r"^DnD/state/combat_positions_[a-z0-9_]+\.json$", file_path):
                # Extract location code from battlemap file path
                match = re.match(r"^DnD/state/combat_positions_([a-z0-9_]+)\.json$", file_path)
                if match:
                    location_code = match.group(1)
                    provenance_path = self.vault_path / f"DnD/state/combat_positions_{location_code}.sync_meta.json"
                else:
                    provenance_path = None
            else:
                provenance_path = None
            
            if provenance_path:
                provenance_data = {
                    "_synced_via": "mcp",
                    "_last_sync": datetime.datetime.now().isoformat(),
                    "_tool": "write_vault_file"
                }
                provenance_path.parent.mkdir(parents=True, exist_ok=True)
                provenance_path.write_text(json.dumps(provenance_data, indent=2), encoding="utf-8")
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Initialize MCP server
app = Server("obsidian-sync")
server = ObsidianSyncServer()


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="update_character_hp",
            description="Update a character's HP",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "new_hp": {"type": "integer"},
                    "max_hp": {"type": "integer"}
                },
                "required": ["character_name", "new_hp", "max_hp"]
            }
        ),
        Tool(
            name="update_character_xp",
            description="Add XP to a character",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "xp_to_add": {"type": "integer"}
                },
                "required": ["character_name", "xp_to_add"]
            }
        ),
        Tool(
            name="update_character_currency",
            description="Update character's currency",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "cp": {"type": "integer"},
                    "sp": {"type": "integer"},
                    "gp": {"type": "integer"},
                    "pp": {"type": "integer"}
                },
                "required": ["character_name"]
            }
        ),
        Tool(
            name="add_inventory_item",
            description="Add an item to character inventory table (with quantity and weight)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Character name (e.g., 'Torgga_Brawnanvil')"},
                    "item_name": {"type": "string", "description": "Item name"},
                    "quantity": {"type": "integer", "description": "Quantity to add (default: 1)"},
                    "weight": {"type": "number", "description": "Weight in pounds (default: 0)"}
                },
                "required": ["character_name", "item_name"]
            }
        ),
        Tool(
            name="remove_inventory_item",
            description="Remove an item from character inventory (or reduce quantity)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "item_name": {"type": "string"},
                    "quantity": {"type": "integer", "description": "Quantity to remove (default: 1)"}
                },
                "required": ["character_name", "item_name"]
            }
        ),
        Tool(
            name="add_weapon",
            description="Add a weapon to character's Weapons table",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "weapon_name": {"type": "string"},
                    "attack_bonus": {"type": "integer"},
                    "damage": {"type": "string", "description": "e.g., '1d8+3 slashing'"},
                    "properties": {"type": "string", "description": "e.g., 'Versatile, Two-Handed'"},
                    "special_effects": {"type": "string"},
                    "equipped": {"type": "boolean", "description": "Is weapon equipped?"}
                },
                "required": ["character_name", "weapon_name", "attack_bonus", "damage"]
            }
        ),
        Tool(
            name="remove_weapon",
            description="Remove a weapon from character's Weapons table",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "weapon_name": {"type": "string"}
                },
                "required": ["character_name", "weapon_name"]
            }
        ),
        Tool(
            name="equip_weapon",
            description="Toggle equipped status for a weapon",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "weapon_name": {"type": "string"},
                    "equipped": {"type": "boolean"}
                },
                "required": ["character_name", "weapon_name", "equipped"]
            }
        ),
        Tool(
            name="add_armor",
            description="Add armor to character's Armor & Shields table",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "armor_name": {"type": "string"},
                    "ac_bonus": {"type": "integer"},
                    "armor_type": {"type": "string", "description": "e.g., 'Heavy', 'Light', 'Shield'"},
                    "properties": {"type": "string"},
                    "special_effects": {"type": "string"},
                    "equipped": {"type": "boolean"}
                },
                "required": ["character_name", "armor_name", "ac_bonus", "armor_type"]
            }
        ),
        Tool(
            name="remove_armor",
            description="Remove armor from character's Armor & Shields table",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "armor_name": {"type": "string"}
                },
                "required": ["character_name", "armor_name"]
            }
        ),
        Tool(
            name="equip_armor",
            description="Toggle equipped status for armor",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "armor_name": {"type": "string"},
                    "equipped": {"type": "boolean"}
                },
                "required": ["character_name", "armor_name", "equipped"]
            }
        ),
        Tool(
            name="add_magic_item",
            description="Add a magic item to character's Magic Items table",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "item_name": {"type": "string"},
                    "properties": {"type": "string"},
                    "charges": {"type": "string", "description": "e.g., '3/3' or 'N/A'"},
                    "notes": {"type": "string"},
                    "attuned": {"type": "boolean"}
                },
                "required": ["character_name", "item_name", "properties"]
            }
        ),
        Tool(
            name="remove_magic_item",
            description="Remove a magic item from character's Magic Items table",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "item_name": {"type": "string"}
                },
                "required": ["character_name", "item_name"]
            }
        ),
        Tool(
            name="attune_item",
            description="Toggle attuned status for a magic item",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "item_name": {"type": "string"},
                    "attuned": {"type": "boolean"}
                },
                "required": ["character_name", "item_name", "attuned"]
            }
        ),
        Tool(
            name="create_npc",
            description="Create a new NPC in Obsidian",
            inputSchema={
                "type": "object",
                "properties": {
                    "npc_name": {"type": "string"},
                    "race": {"type": "string"},
                    "role": {"type": "string"},
                    "location": {"type": "string"},
                    "description": {"type": "string"},
                    "disposition": {"type": "string"}
                },
                "required": ["npc_name", "race", "role", "location", "description"]
            }
        ),
        Tool(
            name="get_character_combat_stats",
            description="Read character combat stats from Obsidian sheet (HP, AC, speed, abilities, initiative)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Character name (e.g., 'Torgga_Brawnanvil')"}
                },
                "required": ["character_name"]
            }
        ),
        Tool(
            name="calculate_and_update_weight",
            description="Calculate total weight from inventory table and update the Total Weight line. Automatically calculates capacity from STR for characters, or uses provided capacity for storage items.",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Character name or storage item name (e.g., 'Party_Wagon')"},
                    "capacity": {"type": "integer", "description": "Optional: Override capacity (for storage items). If not provided, calculates from STR for characters or reads from frontmatter for storage."}
                },
                "required": ["character_name"]
            }
        ),
        Tool(
            name="read_vault_file",
            description="Read a file from the Obsidian vault (generic file read)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path relative to vault root (e.g., 'DnD/state/resources_state.json')"}
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="write_vault_file",
            description="Write a file to the Obsidian vault (generic file write)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path relative to vault root (e.g., 'DnD/state/resources_state.json')"},
                    "content": {"type": "string", "description": "File content to write"}
                },
                "required": ["file_path", "content"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "update_character_hp":
            result = server.update_character_hp(
                arguments["character_name"],
                arguments["new_hp"],
                arguments["max_hp"]
            )
        elif name == "update_character_xp":
            result = server.update_character_xp(
                arguments["character_name"],
                arguments["xp_to_add"]
            )
        elif name == "update_character_currency":
            result = server.update_character_currency(
                arguments["character_name"],
                arguments.get("cp", 0),
                arguments.get("sp", 0),
                arguments.get("gp", 0),
                arguments.get("pp", 0)
            )
        elif name == "add_inventory_item":
            result = server.add_inventory_item(
                arguments["character_name"],
                arguments["item_name"],
                arguments.get("quantity", 1),
                arguments.get("weight", 0)
            )
        elif name == "remove_inventory_item":
            result = server.remove_inventory_item(
                arguments["character_name"],
                arguments["item_name"],
                arguments.get("quantity", 1)
            )
        elif name == "add_weapon":
            result = server.add_weapon(
                arguments["character_name"],
                arguments["weapon_name"],
                arguments["attack_bonus"],
                arguments["damage"],
                arguments.get("properties", "-"),
                arguments.get("special_effects", "-"),
                arguments.get("equipped", False)
            )
        elif name == "remove_weapon":
            result = server.remove_weapon(
                arguments["character_name"],
                arguments["weapon_name"]
            )
        elif name == "equip_weapon":
            result = server.equip_weapon(
                arguments["character_name"],
                arguments["weapon_name"],
                arguments["equipped"]
            )
        elif name == "add_armor":
            result = server.add_armor(
                arguments["character_name"],
                arguments["armor_name"],
                arguments["ac_bonus"],
                arguments["armor_type"],
                arguments.get("properties", "-"),
                arguments.get("special_effects", "-"),
                arguments.get("equipped", False)
            )
        elif name == "remove_armor":
            result = server.remove_armor(
                arguments["character_name"],
                arguments["armor_name"]
            )
        elif name == "equip_armor":
            result = server.equip_armor(
                arguments["character_name"],
                arguments["armor_name"],
                arguments["equipped"]
            )
        elif name == "add_magic_item":
            result = server.add_magic_item(
                arguments["character_name"],
                arguments["item_name"],
                arguments["properties"],
                arguments.get("charges", "-"),
                arguments.get("notes", "-"),
                arguments.get("attuned", False)
            )
        elif name == "remove_magic_item":
            result = server.remove_magic_item(
                arguments["character_name"],
                arguments["item_name"]
            )
        elif name == "attune_item":
            result = server.attune_item(
                arguments["character_name"],
                arguments["item_name"],
                arguments["attuned"]
            )
        elif name == "create_npc":
            result = server.create_npc(
                arguments["npc_name"],
                arguments["race"],
                arguments["role"],
                arguments["location"],
                arguments["description"],
                arguments.get("disposition", "neutral")
            )
        elif name == "get_character_combat_stats":
            result = server.get_character_combat_stats(arguments["character_name"])
        elif name == "calculate_and_update_weight":
            result = server.calculate_and_update_weight(
                arguments["character_name"],
                arguments.get("capacity")
            )
        elif name == "use_spell_slot":
            result = server.use_spell_slot(
                arguments["character_name"],
                arguments["spell_level"]
            )
        elif name == "read_vault_file":
            result = server.read_vault_file(arguments["file_path"])
        elif name == "write_vault_file":
            result = server.write_vault_file(
                arguments["file_path"],
                arguments["content"]
            )
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())


