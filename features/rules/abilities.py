#!/usr/bin/env python3
"""
Get D&D 5e ability score rules and mechanics
Usage: uv run python abilities.py [ability]
Examples:
    uv run python abilities.py                 # List all abilities
    uv run python abilities.py strength        # Get strength rules
    uv run python abilities.py dexterity       # Get dexterity rules
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from rules_api_core import fetch, output, error_output

def calculate_modifier(score):
    """Calculate ability modifier from score"""
    return (score - 10) // 2

def format_ability_details(ability):
    """Format ability for detailed display"""
    formatted = {
        "name": ability.get("name", "Unknown"),
        "full_name": ability.get("full_name", ""),
        "description": ability.get("desc", []),
        "skills": []
    }
    
    # Add associated skills
    if "skills" in ability:
        for skill in ability["skills"]:
            formatted["skills"].append({
                "name": skill.get("name", ""),
                "url": skill.get("url", "")
            })
    
    # Add modifier table
    formatted["modifier_table"] = []
    for score in [1, 8, 10, 12, 14, 16, 18, 20]:
        formatted["modifier_table"].append({
            "score": score,
            "modifier": f"{calculate_modifier(score):+d}"
        })
    
    return formatted

def list_all_abilities():
    """List all available abilities"""
    data = fetch("/ability-scores")
    
    if "error" in data:
        error_output(f"Failed to fetch abilities: {data.get('message', 'Unknown error')}")
    
    abilities = []
    for ability in data.get("results", []):
        abilities.append({
            "name": ability["name"],
            "full_name": ability.get("full_name", ability["name"]),
            "index": ability["index"]
        })
    
    return {
        "count": len(abilities),
        "abilities": abilities,
        "usage": "Use 'uv run python abilities.py <ability-name>' for details"
    }

def main():
    parser = argparse.ArgumentParser(description='Get D&D 5e ability score information')
    parser.add_argument('ability', nargs='?', help='Ability name (optional)')
    parser.add_argument('--modifier', type=int, help='Calculate modifier for a specific score')
    
    args = parser.parse_args()
    
    # If modifier calculation requested
    if args.modifier is not None:
        modifier = calculate_modifier(args.modifier)
        output({
            "score": args.modifier,
            "modifier": f"{modifier:+d}",
            "description": f"An ability score of {args.modifier} gives a {modifier:+d} modifier"
        })
        return
    
    # If no ability specified, list all
    if not args.ability:
        output(list_all_abilities())
        return
    
    # Convert ability name to API format
    ability_map = {
        "str": "str",
        "strength": "str",
        "dex": "dex", 
        "dexterity": "dex",
        "con": "con",
        "constitution": "con",
        "int": "int",
        "intelligence": "int",
        "wis": "wis",
        "wisdom": "wis",
        "cha": "cha",
        "charisma": "cha"
    }
    
    ability_index = ability_map.get(args.ability.lower(), args.ability.lower())
    
    # Fetch specific ability
    data = fetch(f"/ability-scores/{ability_index}")
    
    if "error" in data:
        if data.get("error") == "HTTP 404":
            error_output(f"Ability '{args.ability}' not found. Valid abilities are: STR, DEX, CON, INT, WIS, CHA")
        else:
            error_output(f"Failed to fetch ability: {data.get('message', 'Unknown error')}")
    
    # Format and output
    output(format_ability_details(data))

if __name__ == "__main__":
    main()