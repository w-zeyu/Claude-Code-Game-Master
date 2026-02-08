#!/usr/bin/env python3
"""
Get D&D 5e spell details
Usage: uv run python get_spell.py <spell-name> [options]
Example: uv run python get_spell.py fireball
         uv run python get_spell.py "mage armor" --combat
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from spell_api_core import fetch, output, error_output, format_spell_index

def extract_combat_info(spell):
    """Extract essential combat information"""
    components = spell.get("components", [])
    material = spell.get("material", "")
    
    comp_str = ", ".join(components)
    if "M" in components and material:
        comp_str += f" ({material})"
    
    combat_info = {
        "name": spell.get("name", "Unknown"),
        "level": spell.get("level", 0),
        "school": spell.get("school", {}).get("name", "Unknown"),
        "casting_time": spell.get("casting_time", "Unknown"),
        "range": spell.get("range", "Unknown"),
        "components": comp_str,
        "duration": spell.get("duration", "Unknown"),
        "description": " ".join(spell.get("desc", [])),
    }
    
    # Add damage info if present
    if spell.get("damage"):
        damage_info = spell["damage"]
        if damage_info.get("damage_at_slot_level"):
            combat_info["damage"] = damage_info["damage_at_slot_level"]
        elif damage_info.get("damage_at_character_level"):
            combat_info["damage"] = damage_info["damage_at_character_level"]
    
    # Add save info if present
    if spell.get("dc"):
        dc_info = spell["dc"]
        combat_info["save"] = f"{dc_info.get('dc_type', {}).get('name', 'Unknown')} save"
        if dc_info.get("dc_success"):
            combat_info["save"] += f" ({dc_info['dc_success']})"
    
    # Add higher level info if present
    if spell.get("higher_level"):
        combat_info["higher_level"] = " ".join(spell["higher_level"])
    
    return combat_info

def format_combat_card(spell_info):
    """Format spell as a combat reference card"""
    level_str = "Cantrip" if spell_info["level"] == 0 else f"{spell_info['level']}{'st' if spell_info['level'] == 1 else 'nd' if spell_info['level'] == 2 else 'rd' if spell_info['level'] == 3 else 'th'} level"
    
    card = f"🔮 {spell_info['name'].upper()} ({level_str})\n"
    card += f"School: {spell_info['school']} | Range: {spell_info['range']}\n"
    card += f"Casting Time: {spell_info['casting_time']} | Duration: {spell_info['duration']}\n"
    card += f"Components: {spell_info['components']}\n\n"
    
    # Shorten description for combat use
    desc = spell_info['description']
    if len(desc) > 300:
        desc = desc[:297] + "..."
    card += desc
    
    if spell_info.get("damage"):
        card += f"\n\nDamage: {spell_info['damage']}"
    
    if spell_info.get("save"):
        card += f"\nSave: {spell_info['save']}"
    
    if spell_info.get("higher_level"):
        card += f"\n\nHigher Levels: {spell_info['higher_level']}"
    
    return card

def main():
    parser = argparse.ArgumentParser(description='Get spell details from D&D 5e API')
    parser.add_argument('spell_name', help='Name of the spell')
    parser.add_argument('--combat', action='store_true', 
                       help='Show combat-ready format')
    parser.add_argument('--description', action='store_true',
                       help='Show only the spell description')
    
    args = parser.parse_args()
    
    # Convert spell name to API format
    spell_index = format_spell_index(args.spell_name)
    
    # Fetch spell data
    data = fetch(f"/api/2014/spells/{spell_index}")
    
    # Check for errors
    if "error" in data:
        if data.get("error") == "HTTP 404":
            error_output(f"Spell '{args.spell_name}' not found")
        else:
            error_output(f"Failed to fetch spell: {data.get('message', 'Unknown error')}")
    
    # Output based on mode
    if args.description:
        output({
            "name": data.get("name", "Unknown"),
            "description": " ".join(data.get("desc", []))
        })
    elif args.combat:
        combat_info = extract_combat_info(data)
        print(format_combat_card(combat_info))
    else:
        output(data)

if __name__ == "__main__":
    main()