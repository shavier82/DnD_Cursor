"""Export PARTY_PERSISTENT_DATA.json to Obsidian vault

This script exports:
1. Recurring Income - Cross-campaign income sources
2. Boons - Permanent benefits that persist
3. Permanent Benefits - Titles, memberships, etc.
4. Cross-Campaign Relationships - NPCs/contacts that carry over

All organized in Obsidian with proper linking and metadata.
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime
import frontmatter

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Paths
PARTY_PERSISTENT_DATA_PATH = Path("C:/DnD/PARTY_PERSISTENT_DATA.json")
OBSIDIAN_VAULT = Path("C:/Users/ksist/Documents/Obsidian/DnD")

def format_date(timestamp_str: str) -> str:
    """Format ISO timestamp to readable date"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d")
    except:
        return timestamp_str.split('T')[0] if 'T' in timestamp_str else timestamp_str

def export_persistent_data():
    """Export persistent party data to Obsidian"""
    print("=" * 80)
    print("EXPORTING PARTY PERSISTENT DATA TO OBSIDIAN")
    print("=" * 80)
    print()
    
    # Read PARTY_PERSISTENT_DATA.json
    if not PARTY_PERSISTENT_DATA_PATH.exists():
        print(f"❌ ERROR: {PARTY_PERSISTENT_DATA_PATH} not found")
        return
    
    with open(PARTY_PERSISTENT_DATA_PATH, 'r', encoding='utf-8') as f:
        persistent_data = json.load(f)
    
    # Create folders
    persistent_folder = OBSIDIAN_VAULT / "Party_Persistent_Data"
    recurring_income_folder = persistent_folder / "Recurring_Income"
    boons_folder = persistent_folder / "Boons"
    permanent_benefits_folder = persistent_folder / "Permanent_Benefits"
    relationships_folder = persistent_folder / "Cross_Campaign_Relationships"
    
    persistent_folder.mkdir(exist_ok=True)
    recurring_income_folder.mkdir(exist_ok=True)
    boons_folder.mkdir(exist_ok=True)
    permanent_benefits_folder.mkdir(exist_ok=True)
    relationships_folder.mkdir(exist_ok=True)
    
    # Export Recurring Income
    print("Exporting Recurring Income...")
    recurring_income = persistent_data.get("recurring_income", [])
    income_files = []
    
    for income in recurring_income:
        income_id = income.get("id", "unknown")
        name = income.get("name", "Unknown Income")
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
        filename = f"{safe_name.replace(' ', '_')}.md"
        filepath = recurring_income_folder / filename
        
        # Create frontmatter
        metadata = {
            'type': 'recurring_income',
            'income_id': income_id,
            'status': income.get("status", "active"),
            'source_campaign': income.get("source_campaign", ""),
            'date_acquired': format_date(income.get("agreement_date", "")),
            'tags': ['recurring_income', 'cross_campaign', 'persistent'],
        }
        
        # Build content
        content = f"# {name}\n\n"
        content += f"**Status:** {income.get('status', 'active').title()}\n"
        content += f"**Source Campaign:** {income.get('source_campaign', 'Unknown')}\n"
        content += f"**Source:** {income.get('source', 'Unknown')}\n"
        content += f"**Date Acquired:** {format_date(income.get('agreement_date', ''))}\n\n"
        
        content += f"## Description\n{income.get('description', '')}\n\n"
        
        # Terms
        terms = income.get("terms", {})
        if terms:
            content += "## Terms\n\n"
            for key, value in terms.items():
                content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            content += "\n"
        
        # Notes
        if income.get("notes"):
            content += f"## Notes\n{income.get('notes')}\n\n"
        
        # Write file
        post = frontmatter.Post(content, **metadata)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        income_files.append((filename, name, income.get("status", "active")))
        print(f"  [+] {filename}")
    
    print(f"\n[+] Exported {len(recurring_income)} recurring income sources\n")
    
    # Export Boons
    print("Exporting Boons...")
    boons = persistent_data.get("boons", [])
    boon_files = []
    
    for boon in boons:
        boon_id = boon.get("id", "unknown")
        name = boon.get("name", "Unknown Boon")
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
        filename = f"{safe_name.replace(' ', '_')}.md"
        filepath = boons_folder / filename
        
        # Create frontmatter
        metadata = {
            'type': 'boon',
            'boon_id': boon_id,
            'status': boon.get("status", "active"),
            'source_campaign': boon.get("source_campaign", ""),
            'date_acquired': format_date(boon.get("acquired_date", "")),
            'tags': ['boon', 'cross_campaign', 'persistent'],
        }
        
        # Build content
        content = f"# {name}\n\n"
        content += f"**Status:** {boon.get('status', 'active').title()}\n"
        content += f"**Source Campaign:** {boon.get('source_campaign', 'Unknown')}\n"
        content += f"**Source:** {boon.get('source', 'Unknown')}\n"
        content += f"**Date Acquired:** {format_date(boon.get('acquired_date', ''))}\n\n"
        
        content += f"## Description\n{boon.get('description', '')}\n\n"
        
        # Benefits
        benefits = boon.get("benefits", [])
        if benefits:
            content += "## Benefits\n\n"
            for benefit in benefits:
                content += f"- {benefit}\n"
            content += "\n"
        
        # Notes
        if boon.get("notes"):
            content += f"## Notes\n{boon.get('notes')}\n\n"
        
        # Write file
        post = frontmatter.Post(content, **metadata)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        boon_files.append((filename, name, boon.get("status", "active")))
        print(f"  [+] {filename}")
    
    print(f"\n[+] Exported {len(boons)} boons\n")
    
    # Export Permanent Benefits
    print("Exporting Permanent Benefits...")
    permanent_benefits = persistent_data.get("permanent_benefits", [])
    benefit_files = []
    
    for benefit in permanent_benefits:
        benefit_id = benefit.get("id", "unknown")
        name = benefit.get("name", "Unknown Benefit")
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
        filename = f"{safe_name.replace(' ', '_')}.md"
        filepath = permanent_benefits_folder / filename
        
        # Create frontmatter
        metadata = {
            'type': 'permanent_benefit',
            'benefit_id': benefit_id,
            'status': benefit.get("status", "active"),
            'source_campaign': benefit.get("source_campaign", ""),
            'date_acquired': format_date(benefit.get("acquired_date", "")),
            'tags': ['permanent_benefit', 'cross_campaign', 'persistent'],
        }
        
        # Build content
        content = f"# {name}\n\n"
        content += f"**Status:** {benefit.get('status', 'active').title()}\n"
        content += f"**Source Campaign:** {benefit.get('source_campaign', 'Unknown')}\n"
        content += f"**Source:** {benefit.get('source', 'Unknown')}\n"
        content += f"**Date Acquired:** {format_date(benefit.get('acquired_date', ''))}\n\n"
        
        if benefit.get("rank"):
            content += f"**Rank:** {benefit.get('rank')}\n"
        if benefit.get("faction"):
            content += f"**Faction:** {benefit.get('faction')}\n"
        content += "\n"
        
        content += f"## Description\n{benefit.get('description', '')}\n\n"
        
        # Benefits
        benefits_list = benefit.get("benefits", [])
        if benefits_list:
            content += "## Benefits\n\n"
            for b in benefits_list:
                content += f"- {b}\n"
            content += "\n"
        
        # Members
        members = benefit.get("members", [])
        if members:
            content += "## Members\n\n"
            for member in members:
                content += f"- [[{member}]]\n"
            content += "\n"
        
        # Notes
        if benefit.get("notes"):
            content += f"## Notes\n{benefit.get('notes')}\n\n"
        
        # Write file
        post = frontmatter.Post(content, **metadata)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        benefit_files.append((filename, name, benefit.get("status", "active")))
        print(f"  [+] {filename}")
    
    print(f"\n[+] Exported {len(permanent_benefits)} permanent benefits\n")
    
    # Export Cross-Campaign Relationships
    print("Exporting Cross-Campaign Relationships...")
    relationships = persistent_data.get("cross_campaign_relationships", [])
    relationship_files = []
    
    for rel in relationships:
        rel_id = rel.get("id", "unknown")
        name = rel.get("name", "Unknown Relationship")
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
        filename = f"{safe_name.replace(' ', '_')}.md"
        filepath = relationships_folder / filename
        
        # Create frontmatter
        metadata = {
            'type': 'cross_campaign_relationship',
            'relationship_id': rel_id,
            'relationship_type': rel.get("type", ""),
            'status': rel.get("status", "active"),
            'source_campaign': rel.get("source_campaign", ""),
            'tags': ['relationship', 'cross_campaign', 'persistent'],
        }
        
        # Build content
        content = f"# {name}\n\n"
        content += f"**Type:** {rel.get('type', 'Unknown').replace('_', ' ').title()}\n"
        content += f"**Status:** {rel.get('status', 'active').title()}\n"
        content += f"**Source Campaign:** {rel.get('source_campaign', 'Unknown')}\n"
        content += f"**Relationship:** {rel.get('relationship', 'Unknown')}\n"
        if rel.get("organization"):
            content += f"**Organization:** {rel.get('organization')}\n"
        if rel.get("location"):
            content += f"**Location:** {rel.get('location')}\n"
        content += "\n"
        
        content += f"## Description\n{rel.get('description', '')}\n\n"
        
        # Write file
        post = frontmatter.Post(content, **metadata)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        relationship_files.append((filename, name, rel.get("status", "active")))
        print(f"  [+] {filename}")
    
    print(f"\n[+] Exported {len(relationships)} cross-campaign relationships\n")
    
    # Create index files
    print("Creating index files...")
    
    # Main index
    main_index = persistent_folder / "00_Party_Persistent_Data_Index.md"
    with open(main_index, 'w', encoding='utf-8') as f:
        f.write("# Party Persistent Data\n\n")
        f.write(f"**Party Name:** {persistent_data.get('party_name', 'Unknown')}\n")
        f.write(f"**Last Updated:** {format_date(persistent_data.get('last_updated', ''))}\n\n")
        f.write(f"{persistent_data.get('description', '')}\n\n")
        
        f.write("## Recurring Income\n\n")
        for filename, name, status in income_files:
            f.write(f"- [[Recurring_Income/{filename.replace('.md', '')}|{name}]] ({status})\n")
        f.write("\n")
        
        f.write("## Boons\n\n")
        for filename, name, status in boon_files:
            f.write(f"- [[Boons/{filename.replace('.md', '')}|{name}]] ({status})\n")
        f.write("\n")
        
        f.write("## Permanent Benefits\n\n")
        for filename, name, status in benefit_files:
            f.write(f"- [[Permanent_Benefits/{filename.replace('.md', '')}|{name}]] ({status})\n")
        f.write("\n")
        
        f.write("## Cross-Campaign Relationships\n\n")
        for filename, name, status in relationship_files:
            f.write(f"- [[Cross_Campaign_Relationships/{filename.replace('.md', '')}|{name}]] ({status})\n")
        f.write("\n")
    
    print(f"  [+] Created main index\n")
    
    print("=" * 80)
    print("EXPORT COMPLETE")
    print("=" * 80)
    print(f"[+] Recurring Income: {len(recurring_income)} files")
    print(f"[+] Boons: {len(boons)} files")
    print(f"[+] Permanent Benefits: {len(permanent_benefits)} files")
    print(f"[+] Cross-Campaign Relationships: {len(relationships)} files")
    print(f"\nLocation: {OBSIDIAN_VAULT}")
    print(f"- Party_Persistent_Data/")

if __name__ == "__main__":
    export_persistent_data()
