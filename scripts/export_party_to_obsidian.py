#!/usr/bin/env python3
"""Export party characters directly to Obsidian from party_characters.json"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.campaign_wiki.models.player_character import PlayerCharacter
from mcp_servers.campaign_wiki.models.campaign_wiki import CampaignWiki
from mcp_servers.campaign_wiki.utils.obsidian_sync import ObsidianSync

def calculate_modifier(score: int) -> int:
    """Calculate ability modifier"""
    return (score - 10) // 2

def main():
    # Load party data
    party_file = Path("campaign_data/party_characters.json")
    if not party_file.exists():
        print(f"❌ Error: {party_file} not found")
        return
    
    with open(party_file, 'r', encoding='utf-8') as f:
        party_data = json.load(f)
    
    # Initialize wiki
    wiki = CampaignWiki(
        campaign_name="Mines of Phandelver",
        campaign_id="mines_of_phandelver"
    )
    
    # Convert characters
    print("\n📊 Loading party characters...\n")
    for char_data in party_data['characters']:
        stats = char_data['stats']
        
        # Convert spell slots to proper format
        spell_slots_list = []
        for slot in char_data.get('spell_slots', []):
            spell_slots_list.append({
                'level': slot['level'],
                'maximum': slot['max'],
                'remaining': slot['current']
            })
        
        # Convert resources to proper format
        resources_list = []
        for res in char_data.get('resources', []):
            resources_list.append({
                'name': res['name'],
                'maximum': res['max'],
                'remaining': res['current'],
                'active': False,
                'recharge': res.get('resets_on', 'long_rest')
            })
        
        # Convert to PlayerCharacter model
        pc = PlayerCharacter(
            character_id=char_data['character_id'],
            name=char_data['name'],
            player_name=char_data.get('player'),
            race=char_data.get('race'),
            char_class=char_data.get('class'),
            level=char_data.get('level', 1),
            xp=char_data.get('xp', 0),
            xp_to_next_level=char_data.get('xp_to_next', 0),
            hp={'current': char_data['hp_current'], 'maximum': char_data['hp_max'], 'temporary': 0},
            ac=char_data.get('ac', 10),
            speed=char_data.get('speed', 30),
            initiative_bonus=char_data.get('initiative_bonus', calculate_modifier(stats['dex'])),
            proficiency_bonus=char_data.get('proficiency_bonus', 2),
            ability_scores={
                'strength': stats['str'],
                'dexterity': stats['dex'],
                'constitution': stats['con'],
                'intelligence': stats['int'],
                'wisdom': stats['wis'],
                'charisma': stats['cha']
            },
            currency=char_data.get('currency', {}),
            spell_slots=spell_slots_list,
            class_resources=resources_list,
            features=char_data.get('features', []),
            notes=char_data.get('notes', ''),
            weapons=char_data.get('weapons', [])
        )
        
        wiki.player_characters[pc.character_id] = pc
        
        print(f"✅ {pc.name}")
        print(f"   {pc.char_class} {pc.level} | HP: {pc.hp.current}/{pc.hp.maximum} | AC: {pc.ac}")
        print(f"   STR {stats['str']} ({calculate_modifier(stats['str']):+d}), "
              f"DEX {stats['dex']} ({calculate_modifier(stats['dex']):+d}), "
              f"CON {stats['con']} ({calculate_modifier(stats['con']):+d})")
        print(f"   INT {stats['int']} ({calculate_modifier(stats['int']):+d}), "
              f"WIS {stats['wis']} ({calculate_modifier(stats['wis']):+d}), "
              f"CHA {stats['cha']} ({calculate_modifier(stats['cha']):+d})")
        print()
    
    # Export to Obsidian
    obsidian_path = Path("C:/Users/ksist/Documents/Obsidian/DnD")
    if not obsidian_path.exists():
        print(f"❌ Error: Obsidian vault not found at {obsidian_path}")
        print(f"   Creating vault directory...")
        obsidian_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📝 Exporting to Obsidian: {obsidian_path}\n")
    
    sync = ObsidianSync(str(obsidian_path))
    
    for pc in wiki.player_characters.values():
        print(f"   Writing: {pc.name}.md")
        sync.export_player_character(pc.model_dump())
    
    print(f"\n✅ Exported {len(wiki.player_characters)} characters to Obsidian!")
    print(f"\n📂 Location: {obsidian_path / 'Player Characters'}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

