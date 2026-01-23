#!/usr/bin/env python3
"""
Render Resources Dashboard - Generate human-readable markdown from resources_state.json

Reads resources_state.json and pc_roster.json to generate a markdown dashboard
that can be synced to Obsidian as DnD/state/resources_state.md
"""

import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
RESOURCES = ROOT / "resources_state.json"
ROSTER = ROOT / "pc_roster.json"

def titleize_actor_id(actor_id: str) -> str:
    """Convert actor_id (e.g., 'torgga_brawnanvil') to Obsidian note name (e.g., 'Torgga_Brawnanvil')."""
    parts = actor_id.split("_")
    return "_".join([p[:1].upper() + p[1:] if p else "" for p in parts if p])

def load_roster_map() -> dict:
    """
    Load PC roster mapping to Obsidian note names.
    
    Expected pc_roster.json shapes:
    - { "torgga_brawnanvil": {"sheet":"Torgga_Brawnanvil","spells":"Torgga_Brawnanvil_Spells"} }
    - or { "pcs": [ {"id":"torgga_brawnanvil","sheet":"Torgga_Brawnanvil", ...}, ...] }
    """
    if not ROSTER.exists():
        return {}
    
    try:
        data = json.loads(ROSTER.read_text(encoding="utf-8"))
    except Exception:
        return {}
    
    out = {}
    if isinstance(data, dict) and "pcs" in data and isinstance(data["pcs"], list):
        # Array format: {"pcs": [{"id": "...", "sheet": "...", "spells": "..."}, ...]}
        for pc in data["pcs"]:
            pid = pc.get("id")
            if pid:
                out[pid] = {
                    "sheet": pc.get("sheet"),
                    "spells": pc.get("spells"),
                }
    elif isinstance(data, dict):
        # Direct mapping format: {"actor_id": {"sheet": "...", "spells": "..."}, ...}
        for k, v in data.items():
            if isinstance(v, dict):
                out[k] = {
                    "sheet": v.get("sheet"),
                    "spells": v.get("spells"),
                }
    return out

def format_spell_slots(slots: dict) -> str:
    """Format spell slots dict as readable text."""
    if not slots:
        return "_None_"
    parts = []
    # Sort by level (numeric keys like "1", "2", "3")
    for lvl in sorted(slots.keys(), key=lambda x: int(x) if str(x).isdigit() else 999):
        count = slots[lvl]
        parts.append(f"L{lvl}: **{count}**")
    return ", ".join(parts)

def render(resources: dict, roster_map: dict) -> str:
    """Generate markdown dashboard from resources and roster mapping."""
    lines = []
    lines.append("# Party Resources (AUTO)")
    lines.append("")
    lines.append(f"_Last generated: {datetime.now().isoformat(timespec='seconds')}_")
    lines.append("")
    lines.append("> Source of truth: `DnD/state/resources_state.json`")
    lines.append("")

    for actor_id in sorted(resources.keys()):
        r = resources[actor_id] or {}
        # Get Obsidian note names from roster, or fallback to titleized actor_id
        sheet = (roster_map.get(actor_id, {}) or {}).get("sheet") or titleize_actor_id(actor_id)
        spells = (roster_map.get(actor_id, {}) or {}).get("spells") or f"{sheet}_Spells"

        lines.append(f"## [[{sheet}]]")
        lines.append(f"- Spells: [[{spells}]]")
        lines.append("")

        # Spell slots
        slots = r.get("spell_slots") or {}
        lines.append(f"- Spell Slots: {format_spell_slots(slots)}")

        # Scalar resources (everything except spell_slots)
        scalar_keys = [k for k in r.keys() if k != "spell_slots" and isinstance(r.get(k), int)]
        
        # Character-specific resources to always show (even at 0) based on class
        # This ensures class resources are visible even when depleted
        character_resources = {
            "eglath_bearkiller": {"rage"},  # Barbarian
            "torgga_brawnanvil": {"channel_divinity"},  # Cleric
            "vandross_ephrates": {"superiority_die"},  # Fighter (Battle Master)
            # Add more as needed: ki for Monk, bardic_inspiration for Bard, etc.
        }
        
        relevant_keys = []
        if scalar_keys:
            for k in sorted(scalar_keys):
                value = r.get(k, 0)
                # Show if value > 0 OR if it's relevant to this character's class
                if value > 0 or k in character_resources.get(actor_id, set()):
                    relevant_keys.append((k, value))
        
        if relevant_keys:
            for k, value in relevant_keys:
                # Format key: "channel_divinity" -> "Channel Divinity"
                display_name = k.replace("_", " ").title()
                lines.append(f"- {display_name}: **{value}**")
        elif not slots:
            # Only show "no resources tracked" if character has no slots and no relevant resources
            lines.append("- _No resources tracked_")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

def main():
    """Generate and print markdown dashboard."""
    if not RESOURCES.exists():
        print(f"ERROR: Missing {RESOURCES}", file=sys.stderr)
        sys.exit(1)

    try:
        resources = json.loads(RESOURCES.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to load resources: {e}", file=sys.stderr)
        sys.exit(1)
    
    roster_map = load_roster_map()
    md = render(resources, roster_map)

    # Print to stdout so caller can pipe it into MCP write tool
    print(md, end="")

if __name__ == "__main__":
    import sys
    main()
