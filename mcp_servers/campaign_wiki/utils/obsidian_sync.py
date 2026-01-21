"""Obsidian vault synchronization"""

import frontmatter
from pathlib import Path
from typing import Dict, Any


class ObsidianSync:
    """Sync campaign wiki to Obsidian vault"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)
    
    def export_npc(self, npc_data: Dict[str, Any], wiki_data: Dict[str, Any] = None):
        """Export NPC to Obsidian note with wiki links"""
        npc_folder = self.vault_path / "NPCs"
        npc_folder.mkdir(exist_ok=True)
        
        # Convert enum values to strings for YAML compatibility
        role = npc_data.get('role')
        if hasattr(role, 'value'):
            role = role.value
        
        status = npc_data.get('status')
        if hasattr(status, 'value'):
            status = status.value
        
        # Create frontmatter
        metadata = {
            'type': 'npc',
            'role': role,
            'faction': npc_data.get('faction'),
            'location': npc_data.get('location'),
            'status': status,
            'alive': npc_data.get('alive', True),
            'tags': npc_data.get('tags', []),
        }
        
        # Create content with wiki links
        content = f"# {npc_data['name']}\n\n"
        
        # Add quick info with links
        if npc_data.get('faction'):
            content += f"**Faction:** {npc_data['faction']}\n"
        if npc_data.get('location'):
            # Link to location if it exists
            location_name = npc_data['location']
            content += f"**Location:** [[{location_name}]]\n"
        if role:
            content += f"**Role:** {role}\n"
        if status:
            content += f"**Status:** {status}\n"
        content += "\n"
        
        if npc_data.get('description'):
            content += f"## Description\n{npc_data['description']}\n\n"
        
        if npc_data.get('personality'):
            content += f"## Personality\n{npc_data['personality']}\n\n"
        
        if npc_data.get('background'):
            content += f"## Background\n{npc_data['background']}\n\n"
        
        # Add Status section if NPC is dead or has a status
        if not npc_data.get('alive', True) or status:
            content += "## Status\n\n"
            if status:
                content += f"**Status:** {status}\n\n"
            if not npc_data.get('alive', True):
                content += "**DECEASED** - This NPC is dead.\n\n"
            if npc_data.get('last_seen'):
                content += f"**Last Seen:** {npc_data['last_seen']}\n\n"
        
        # Add relationships section with wiki links
        if wiki_data and wiki_data.get('relationships'):
            npc_id = npc_data.get('npc_id')
            npc_name = npc_data.get('name')
            # Find relationships where this NPC is involved (by ID or name)
            related_rels = []
            for r in wiki_data['relationships']:
                from_entity = r.get('from_entity', '')
                to_entity = r.get('to_entity', '')
                if (from_entity == npc_id or from_entity == npc_name or 
                    to_entity == npc_id or to_entity == npc_name):
                    related_rels.append(r)
            
            if related_rels:
                content += "## Relationships\n"
                for rel in related_rels:
                    # Find the other entity (by ID or name)
                    other_entity = rel['to_entity'] if (rel['from_entity'] == npc_id or rel['from_entity'] == npc_name) else rel['from_entity']
                    
                    # Try to find NPC by ID first, then by name
                    other_npc = None
                    for npc in wiki_data.get('npcs', {}).values():
                        if isinstance(npc, dict):
                            if npc.get('npc_id') == other_entity or npc.get('name') == other_entity:
                                other_npc = npc
                                break
                        else:
                            # Pydantic model
                            if npc.npc_id == other_entity or npc.name == other_entity:
                                other_npc = npc.model_dump() if hasattr(npc, 'model_dump') else dict(npc)
                                break
                    
                    if other_npc:
                        rel_type = rel.get('relationship_type')
                        if hasattr(rel_type, 'value'):
                            rel_type = rel_type.value
                        description = rel.get('description', '')
                        other_name = other_npc.get('name') if isinstance(other_npc, dict) else getattr(other_npc, 'name', other_entity)
                        content += f"- **[[{other_name}]]** - {rel_type}"
                        if description:
                            content += f": {description}"
                        content += "\n"
                content += "\n"
        
        if npc_data.get('quests'):
            content += f"## Related Quests\n"
            for quest in npc_data['quests']:
                content += f"- [[{quest}]]\n"
            content += "\n"
        
        # Create note with frontmatter
        post = frontmatter.Post(content, **metadata)
        
        # Write to file
        file_path = npc_folder / f"{npc_data['name'].replace(' ', '_')}.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
    
    def export_location(self, location_data: Dict[str, Any], wiki_data: Dict[str, Any] = None):
        """Export location to Obsidian note with wiki links"""
        loc_folder = self.vault_path / "Locations"
        loc_folder.mkdir(exist_ok=True)
        
        # Convert enum values to strings for YAML compatibility
        location_type = location_data.get('location_type')
        if hasattr(location_type, 'value'):
            location_type = location_type.value
        
        metadata = {
            'type': 'location',
            'location_type': location_type,
            'region': location_data.get('region'),
            'visited': location_data.get('visited', False),
            'tags': location_data.get('tags', []),
        }
        
        content = f"# {location_data['name']}\n\n"
        
        if location_data.get('description'):
            content += f"{location_data['description']}\n\n"
        
        if location_data.get('map_path'):
            content += f"![[{Path(location_data['map_path']).name}]]\n\n"
        
        # Add NPCs present at this location
        if wiki_data:
            npcs_here = [npc for npc in wiki_data['npcs'].values() if npc.get('location') == location_data['name']]
            if npcs_here:
                content += "## NPCs Present\n"
                for npc in npcs_here:
                    content += f"- [[{npc['name']}]]"
                    if npc.get('description'):
                        content += f" - {npc['description'][:50]}..."
                    content += "\n"
                content += "\n"
        
        # Add notes if any
        if location_data.get('notes'):
            content += "## Notes\n"
            for note in location_data['notes']:
                content += f"- {note}\n"
            content += "\n"
        
        post = frontmatter.Post(content, **metadata)
        file_path = loc_folder / f"{location_data['name'].replace(' ', '_')}.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
    
    def export_quest(self, quest_data: Dict[str, Any]):
        """Export quest to Obsidian note"""
        quest_folder = self.vault_path / "Quests"
        quest_folder.mkdir(exist_ok=True)
        
        # Convert enum values to strings for YAML compatibility
        status = quest_data.get('status')
        if hasattr(status, 'value'):
            status = status.value
        
        quest_type = quest_data.get('quest_type')
        if hasattr(quest_type, 'value'):
            quest_type = quest_type.value
        
        metadata = {
            'type': 'quest',
            'status': status,
            'quest_type': quest_type,
            'priority': quest_data.get('priority', 5),
            'tags': quest_data.get('tags', []),
        }
        
        content = f"# {quest_data['name']}\n\n"
        content += f"**Status:** {quest_data.get('status', 'unknown')}\n"
        content += f"**Type:** {quest_type}\n\n"
        
        if quest_data.get('quest_giver'):
            # Try to find quest giver name from wiki data if available
            quest_giver = quest_data['quest_giver']
            content += f"**Quest Giver:** [[{quest_giver}]]\n"
        
        if quest_data.get('date_accepted'):
            content += f"**Accepted:** {quest_data['date_accepted']}\n"
        if quest_data.get('date_completed'):
            content += f"**Completed:** {quest_data['date_completed']}\n"
        
        content += "\n"
        content += f"## Description\n{quest_data.get('description', 'No description')}\n\n"
        
        if quest_data.get('background'):
            content += f"## Background\n{quest_data['background']}\n\n"
        
        if quest_data.get('objectives'):
            content += "## Objectives\n"
            for i, obj in enumerate(quest_data['objectives']):
                completed = quest_data.get('objectives_completed', [])[i] if i < len(quest_data.get('objectives_completed', [])) else False
                checkbox = "[x]" if completed else "[ ]"
                content += f"- {checkbox} {obj}\n"
            content += "\n"
        
        # Rewards
        if quest_data.get('reward_gold', 0) > 0 or quest_data.get('reward_xp', 0) > 0 or quest_data.get('reward_items') or quest_data.get('reward_reputation'):
            content += "## Rewards\n"
            if quest_data.get('reward_gold', 0) > 0:
                content += f"- **Gold:** {quest_data['reward_gold']}\n"
            if quest_data.get('reward_xp', 0) > 0:
                content += f"- **XP:** {quest_data['reward_xp']}\n"
            if quest_data.get('reward_items'):
                content += f"- **Items:** {', '.join(quest_data['reward_items'])}\n"
            if quest_data.get('reward_reputation'):
                for faction, rep in quest_data['reward_reputation'].items():
                    content += f"- **Reputation ({faction}):** {rep:+d}\n"
            content += "\n"
        
        # Related content
        if quest_data.get('related_npcs') or quest_data.get('related_locations'):
            content += "## Related Content\n"
            if quest_data.get('related_npcs'):
                content += "**NPCs:**\n"
                for npc_id in quest_data['related_npcs']:
                    content += f"- [[{npc_id}]]\n"
            if quest_data.get('related_locations'):
                content += "**Locations:**\n"
                for loc_id in quest_data['related_locations']:
                    content += f"- [[{loc_id}]]\n"
            content += "\n"
        
        # Consequences
        if quest_data.get('consequences'):
            content += "## Consequences\n"
            for consequence in quest_data['consequences']:
                content += f"- {consequence}\n"
            content += "\n"
        
        # Notes
        if quest_data.get('notes'):
            content += "## Notes\n"
            for note in quest_data['notes']:
                content += f"- {note}\n"
            content += "\n"
        
        post = frontmatter.Post(content, **metadata)
        file_path = quest_folder / f"{quest_data['name'].replace(' ', '_')}.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
    
    def export_player_character(self, pc_data: Dict[str, Any]):
        """Export player character to Obsidian note with full character sheet
        
        NOTE: This function will NOT overwrite existing character files to prevent
        data loss. Use obsidian-sync MCP tools to update character data instead.
        """
        pc_folder = self.vault_path / "Player Characters"
        pc_folder.mkdir(exist_ok=True)
        
        # Check if file already exists - if so, skip to prevent overwriting detailed sheets
        char_name = pc_data.get('name', '').replace(' ', '_')
        char_file = pc_folder / f"{char_name}.md"
        if char_file.exists():
            # File exists - don't overwrite it to preserve detailed character data
            return
        
        # Calculate modifiers
        def calc_mod(score):
            return (score - 10) // 2
        
        ability_scores = pc_data.get('ability_scores', {})
        str_mod = calc_mod(ability_scores.get('strength', 10))
        dex_mod = calc_mod(ability_scores.get('dexterity', 10))
        con_mod = calc_mod(ability_scores.get('constitution', 10))
        int_mod = calc_mod(ability_scores.get('intelligence', 10))
        wis_mod = calc_mod(ability_scores.get('wisdom', 10))
        cha_mod = calc_mod(ability_scores.get('charisma', 10))
        
        # Frontmatter
        metadata = {
            'type': 'player_character',
            'class': pc_data.get('char_class', ''),
            'level': pc_data.get('level', 1),
            'race': pc_data.get('race', ''),
            'player': pc_data.get('player_name', ''),
            'xp': pc_data.get('xp', 0),
            'tags': ['pc', 'character'],
        }
        
        # Build character sheet
        content = f"# {pc_data['name']}\n\n"
        
        # Quick Stats
        content += "## Quick Stats\n\n"
        content += f"**Class:** {pc_data.get('char_class', 'Unknown')} {pc_data.get('level', 1)}\n"
        if pc_data.get('race'):
            content += f"**Race:** {pc_data.get('race')}\n"
        if pc_data.get('background'):
            content += f"**Background:** {pc_data.get('background')}\n"
        if pc_data.get('alignment'):
            content += f"**Alignment:** {pc_data.get('alignment')}\n"
        content += "\n"
        
        # Combat Stats
        hp = pc_data.get('hp', {})
        content += "## Combat Stats\n\n"
        content += f"**HP:** {hp.get('current', 0)}/{hp.get('maximum', 0)}"
        if hp.get('temporary', 0) > 0:
            content += f" (+{hp.get('temporary')} temp)"
        content += "\n"
        content += f"**AC:** {pc_data.get('ac', 10)}\n"
        content += f"**Initiative:** +{pc_data.get('initiative_bonus', dex_mod)}\n"
        content += f"**Speed:** {pc_data.get('speed', 30)} ft\n"
        content += f"**Proficiency Bonus:** +{pc_data.get('proficiency_bonus', 2)}\n"
        content += "\n"
        
        # Ability Scores
        content += "## Ability Scores\n\n"
        content += "| Stat | Score | Modifier |\n"
        content += "|------|-------|----------|\n"
        content += f"| STR  | {ability_scores.get('strength', 10)} | {str_mod:+d} |\n"
        content += f"| DEX  | {ability_scores.get('dexterity', 10)} | {dex_mod:+d} |\n"
        content += f"| CON  | {ability_scores.get('constitution', 10)} | {con_mod:+d} |\n"
        content += f"| INT  | {ability_scores.get('intelligence', 10)} | {int_mod:+d} |\n"
        content += f"| WIS  | {ability_scores.get('wisdom', 10)} | {wis_mod:+d} |\n"
        content += f"| CHA  | {ability_scores.get('charisma', 10)} | {cha_mod:+d} |\n"
        content += "\n"
        
        # Progression
        content += "## Progression\n\n"
        content += f"**XP:** {pc_data.get('xp', 0):,} / {pc_data.get('xp_to_next_level', 0):,}\n"
        xp_needed = pc_data.get('xp_to_next_level', 0) - pc_data.get('xp', 0)
        if xp_needed > 0:
            content += f"**Next Level:** {xp_needed:,} XP needed\n"
        content += "\n"
        
        # Spell Slots
        spell_slots = pc_data.get('spell_slots', [])
        if spell_slots:
            content += "## Spell Slots\n\n"
            for slot in sorted(spell_slots, key=lambda x: x.get('level', 0)):
                level = slot.get('level')
                maximum = slot.get('maximum')
                remaining = slot.get('remaining')
                used = maximum - remaining
                dots = "●" * remaining + "○" * used
                content += f"**Level {level}:** {dots} ({remaining}/{maximum})\n"
            content += "\n"
        
        # Class Resources
        resources = pc_data.get('class_resources', [])
        if resources:
            content += "## Class Resources\n\n"
            for res in resources:
                name = res.get('name')
                maximum = res.get('maximum')
                remaining = res.get('remaining')
                used = maximum - remaining
                dots = "●" * remaining + "○" * used
                content += f"**{name}:** {dots} ({remaining}/{maximum})\n"
            content += "\n"
        
        # Weapons & Attacks
        weapons = pc_data.get('weapons', [])
        if weapons:
            content += "## Weapons & Attacks\n\n"
            for weapon in weapons:
                name = weapon.get('name')
                attack_bonus = weapon.get('attack_bonus', 0)
                damage_dice = weapon.get('damage_dice', '')
                damage_type = weapon.get('damage_type', '')
                properties = weapon.get('properties', [])
                
                if attack_bonus > 0:
                    content += f"**{name}:** +{attack_bonus} to hit, {damage_dice} {damage_type}"
                elif attack_bonus == 0 and 'Spell Save' in str(properties):
                    content += f"**{name}:** {damage_dice} {damage_type}"
                else:
                    content += f"**{name}:** {damage_dice} {damage_type}"
                
                if properties:
                    props_str = ", ".join(properties)
                    content += f" ({props_str})"
                content += "\n"
            content += "\n"
        
        # Currency
        currency = pc_data.get('currency', {})
        if any(currency.values()):
            content += "## Currency\n\n"
            if currency.get('pp'):
                content += f"- **Platinum:** {currency.get('pp'):,} pp\n"
            if currency.get('gp'):
                content += f"- **Gold:** {currency.get('gp'):,} gp\n"
            if currency.get('ep'):
                content += f"- **Electrum:** {currency.get('ep'):,} ep\n"
            if currency.get('sp'):
                content += f"- **Silver:** {currency.get('sp'):,} sp\n"
            if currency.get('cp'):
                content += f"- **Copper:** {currency.get('cp'):,} cp\n"
            
            # Calculate total wealth in GP
            total_gp = (
                currency.get('pp', 0) * 10 +
                currency.get('gp', 0) +
                currency.get('ep', 0) / 2 +
                currency.get('sp', 0) / 10 +
                currency.get('cp', 0) / 100
            )
            content += f"\n**Total Wealth:** {total_gp:.2f} gp\n"
            content += "\n"
        
        # Inventory
        inventory = pc_data.get('inventory', [])
        if inventory:
            content += "## Inventory\n\n"
            equipped = [item for item in inventory if item.get('equipped')]
            unequipped = [item for item in inventory if not item.get('equipped')]
            
            if equipped:
                content += "### Equipped\n"
                for item in equipped:
                    qty = item.get('quantity', 1)
                    name = item.get('name')
                    if qty > 1:
                        content += f"- **{name}** (x{qty})\n"
                    else:
                        content += f"- **{name}**\n"
                content += "\n"
            
            if unequipped:
                content += "### Carried\n"
                for item in unequipped:
                    qty = item.get('quantity', 1)
                    name = item.get('name')
                    weight = item.get('weight', 0) * qty
                    if qty > 1:
                        content += f"- {name} (x{qty}) - {weight} lbs\n"
                    else:
                        content += f"- {name} - {weight} lbs\n"
                content += "\n"
            
            # Total weight
            total_weight = sum(item.get('weight', 0) * item.get('quantity', 1) for item in inventory)
            carrying_capacity = ability_scores.get('strength', 10) * 15
            content += f"**Total Weight:** {total_weight} / {carrying_capacity} lbs\n"
            content += "\n"
        
        # Proficiencies
        if any([
            pc_data.get('armor_proficiencies'),
            pc_data.get('weapon_proficiencies'),
            pc_data.get('skill_proficiencies'),
            pc_data.get('languages')
        ]):
            content += "## Proficiencies\n\n"
            if pc_data.get('armor_proficiencies'):
                content += f"**Armor:** {', '.join(pc_data.get('armor_proficiencies'))}\n"
            if pc_data.get('weapon_proficiencies'):
                content += f"**Weapons:** {', '.join(pc_data.get('weapon_proficiencies'))}\n"
            if pc_data.get('skill_proficiencies'):
                content += f"**Skills:** {', '.join(pc_data.get('skill_proficiencies'))}\n"
            if pc_data.get('languages'):
                content += f"**Languages:** {', '.join(pc_data.get('languages'))}\n"
            content += "\n"
        
        # Character Details
        if any([
            pc_data.get('personality_traits'),
            pc_data.get('ideals'),
            pc_data.get('bonds'),
            pc_data.get('flaws')
        ]):
            content += "## Personality\n\n"
            if pc_data.get('personality_traits'):
                content += f"**Traits:** {pc_data.get('personality_traits')}\n\n"
            if pc_data.get('ideals'):
                content += f"**Ideals:** {pc_data.get('ideals')}\n\n"
            if pc_data.get('bonds'):
                content += f"**Bonds:** {pc_data.get('bonds')}\n\n"
            if pc_data.get('flaws'):
                content += f"**Flaws:** {pc_data.get('flaws')}\n\n"
        
        # Backstory
        if pc_data.get('backstory'):
            content += "## Backstory\n\n"
            content += f"{pc_data.get('backstory')}\n\n"
        
        # Notes
        if pc_data.get('notes'):
            content += "## Notes\n\n"
            content += f"{pc_data.get('notes')}\n\n"
        
        # Create note
        post = frontmatter.Post(content, **metadata)
        file_path = pc_folder / f"{pc_data['name'].replace(' ', '_')}.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
    
    def export_faction(self, faction_data: Dict[str, Any], wiki_data: Dict[str, Any] = None):
        """Export faction to Obsidian note with reputation and rank tracking"""
        faction_folder = self.vault_path / "Factions"
        faction_folder.mkdir(exist_ok=True)
        
        # Convert enum values to strings for YAML compatibility
        faction_type = faction_data.get('faction_type')
        if hasattr(faction_type, 'value'):
            faction_type = faction_type.value
        
        metadata = {
            'type': 'faction',
            'faction_type': faction_type,
            'active': faction_data.get('active', True),
            'size': faction_data.get('size'),
            'tags': ['faction'],
        }
        
        content = f"# {faction_data['name']}\n\n"
        
        # Basic Info
        if faction_data.get('description'):
            content += f"## Description\n{faction_data['description']}\n\n"
        
        content += f"**Type:** {faction_type}\n"
        if faction_data.get('size'):
            content += f"**Size:** {faction_data['size']}\n"
        content += f"**Status:** {'Active' if faction_data.get('active', True) else 'Inactive'}\n\n"
        
        # Leadership
        if faction_data.get('leader'):
            leader_name = faction_data['leader']
            # Try to find NPC by ID or name
            if wiki_data:
                for npc in wiki_data.get('npcs', {}).values():
                    npc_dict = npc if isinstance(npc, dict) else (npc.model_dump() if hasattr(npc, 'model_dump') else dict(npc))
                    if npc_dict.get('npc_id') == leader_name or npc_dict.get('name') == leader_name:
                        leader_name = npc_dict.get('name', leader_name)
                        break
            content += f"**Leader:** [[{leader_name}]]\n"
        if faction_data.get('headquarters'):
            hq_name = faction_data['headquarters']
            content += f"**Headquarters:** [[{hq_name}]]\n"
        content += "\n"
        
        # Goals and Values
        if faction_data.get('goals'):
            content += "## Goals\n"
            for goal in faction_data['goals']:
                content += f"- {goal}\n"
            content += "\n"
        
        if faction_data.get('values'):
            content += "## Values\n"
            for value in faction_data['values']:
                content += f"- {value}\n"
            content += "\n"
        
        # Territory
        if faction_data.get('territory'):
            content += "## Territory\n"
            for territory in faction_data['territory']:
                content += f"- {territory}\n"
            content += "\n"
        
        # Rank Structure
        rank_structure = faction_data.get('rank_structure', [])
        if rank_structure:
            content += "## Rank Structure\n"
            content += "*(From lowest to highest)*\n\n"
            for i, rank in enumerate(rank_structure):
                content += f"{i+1}. **{rank}**"
                req = faction_data.get('requirements', {}).get(rank)
                if req:
                    content += f" - *Requires: {req}*"
                content += "\n"
            content += "\n"
        
        # Benefits by Rank
        benefits = faction_data.get('benefits', {})
        if benefits:
            content += "## Benefits by Rank\n\n"
            for rank, rank_benefits in benefits.items():
                if rank_benefits:
                    content += f"### {rank}\n"
                    for benefit in rank_benefits:
                        content += f"- {benefit}\n"
                    content += "\n"
        
        # Reputation Tracking (always show section)
        content += "## Reputation\n\n"
        reputation = faction_data.get('reputation', {})
        if reputation:
            content += "| Character/Party | Reputation | Level | Rank |\n"
            content += "|----------------|------------|-------|------|\n"
            
            for char_name, rep_value in sorted(reputation.items(), key=lambda x: x[1], reverse=True):
                # Determine reputation level
                if rep_value <= -50:
                    level = "Hated"
                elif rep_value <= -25:
                    level = "Hostile"
                elif rep_value <= -10:
                    level = "Unfriendly"
                elif rep_value < 10:
                    level = "Neutral"
                elif rep_value < 25:
                    level = "Friendly"
                elif rep_value < 50:
                    level = "Honored"
                else:
                    level = "Exalted"
                
                rank_title = faction_data.get('rank', {}).get(char_name, "None")
                content += f"| {char_name} | {rep_value:+d} | {level} | {rank_title} |\n"
        else:
            content += "*No reputation tracked yet.*\n"
        content += "\n"
        
        # Relationships
        allied = faction_data.get('allied_factions', [])
        enemies = faction_data.get('enemy_factions', [])
        if allied or enemies:
            content += "## Faction Relationships\n\n"
            if allied:
                content += "### Allies\n"
                for ally_id in allied:
                    # Try to find faction name
                    ally_name = ally_id
                    if wiki_data:
                        for fac in wiki_data.get('factions', {}).values():
                            fac_dict = fac if isinstance(fac, dict) else (fac.model_dump() if hasattr(fac, 'model_dump') else dict(fac))
                            if fac_dict.get('faction_id') == ally_id:
                                ally_name = fac_dict.get('name', ally_id)
                                break
                    content += f"- [[{ally_name}]]\n"
                content += "\n"
            if enemies:
                content += "### Enemies\n"
                for enemy_id in enemies:
                    # Try to find faction name
                    enemy_name = enemy_id
                    if wiki_data:
                        for fac in wiki_data.get('factions', {}).values():
                            fac_dict = fac if isinstance(fac, dict) else (fac.model_dump() if hasattr(fac, 'model_dump') else dict(fac))
                            if fac_dict.get('faction_id') == enemy_id:
                                enemy_name = fac_dict.get('name', enemy_id)
                                break
                    content += f"- [[{enemy_name}]]\n"
                content += "\n"
        
        # Members
        member_npcs = faction_data.get('member_npcs', [])
        if member_npcs:
            content += "## Members\n"
            for npc_id in member_npcs:
                # Try to find NPC name
                npc_name = npc_id
                if wiki_data:
                    for npc in wiki_data.get('npcs', {}).values():
                        npc_dict = npc if isinstance(npc, dict) else (npc.model_dump() if hasattr(npc, 'model_dump') else dict(npc))
                        if npc_dict.get('npc_id') == npc_id:
                            npc_name = npc_dict.get('name', npc_id)
                            break
                content += f"- [[{npc_name}]]\n"
            content += "\n"
        
        # Notes
        if faction_data.get('notes'):
            content += "## Notes\n\n"
            content += f"{faction_data['notes']}\n\n"
        
        # Create note
        post = frontmatter.Post(content, **metadata)
        file_path = faction_folder / f"{faction_data['name'].replace(' ', '_')}.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
    
    def sync_all(self, wiki_data: Dict[str, Any]):
        """Sync entire wiki to Obsidian with cross-references"""
        # Export player characters
        for pc in wiki_data.get('player_characters', {}).values():
            self.export_player_character(pc)
        
        # Export NPCs with wiki links
        for npc in wiki_data.get('npcs', {}).values():
            self.export_npc(npc, wiki_data)
        
        for location in wiki_data.get('locations', {}).values():
            self.export_location(location, wiki_data)
        
        for quest in wiki_data.get('quests', {}).values():
            self.export_quest(quest)
        
        # Export factions with wiki links
        for faction in wiki_data.get('factions', {}).values():
            faction_dict = faction if isinstance(faction, dict) else (faction.model_dump() if hasattr(faction, 'model_dump') else dict(faction))
            self.export_faction(faction_dict, wiki_data)

