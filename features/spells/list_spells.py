#!/usr/bin/env python3
"""
List and search D&D 5e spells
Usage: uv run python list_spells.py [options]
Examples:
    uv run python list_spells.py                    # List all spells
    uv run python list_spells.py --search fire      # Search for fire spells
    uv run python list_spells.py --level 3          # Show 3rd level spells
    uv run python list_spells.py --school evocation # Show evocation spells
    uv run python list_spells.py --class wizard     # Show wizard spells
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from spell_api_core import fetch, output, error_output

def fetch_spell_details(spell_index):
    """Fetch full details for a spell"""
    return fetch(f"/api/2014/spells/{spell_index}")

def filter_spells(spells, args):
    """Apply filters to spell list"""
    results = []
    
    for spell in spells:
        # For filtering, we need full spell details
        if args.level is not None or args.school or args.spell_class or args.ritual or args.concentration:
            spell_data = fetch_spell_details(spell["index"])
            if "error" in spell_data:
                continue
        else:
            spell_data = spell
        
        # Search filter (works on basic data)
        if args.search:
            if args.search.lower() not in spell.get("name", "").lower():
                continue
        
        # Level filter
        if args.level is not None:
            if spell_data.get("level", -1) != args.level:
                continue
        
        # School filter
        if args.school:
            school_name = spell_data.get("school", {}).get("index", "")
            if school_name != args.school.lower():
                continue
        
        # Class filter
        if args.spell_class:
            classes = [c.get("index", "") for c in spell_data.get("classes", [])]
            if args.spell_class.lower() not in classes:
                continue
        
        # Ritual filter
        if args.ritual and not spell_data.get("ritual", False):
            continue
        
        # Concentration filter
        if args.concentration and not spell_data.get("concentration", False):
            continue
        
        # Build result entry
        result = {
            "index": spell.get("index"),
            "name": spell.get("name"),
            "url": spell.get("url")
        }
        
        # Add extra info if we fetched full details
        if "level" in spell_data:
            result["level"] = spell_data["level"]
            result["school"] = spell_data.get("school", {}).get("name", "Unknown")
            if args.ritual or args.concentration:
                result["ritual"] = spell_data.get("ritual", False)
                result["concentration"] = spell_data.get("concentration", False)
        
        results.append(result)
    
    return results

def format_spell_list(spells):
    """Format spells for display"""
    if not spells:
        return []
    
    # Group by level if level info is available
    if "level" in spells[0]:
        by_level = {}
        for spell in spells:
            level = spell["level"]
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(spell)
        
        formatted = []
        for level in sorted(by_level.keys()):
            level_name = "Cantrips" if level == 0 else f"Level {level}"
            formatted.append({"level": level_name, "spells": by_level[level]})
        
        return formatted
    
    return spells

def main():
    parser = argparse.ArgumentParser(description='List and search D&D 5e spells')
    parser.add_argument('--search', help='Search spells by name')
    parser.add_argument('--level', type=int, choices=range(10), 
                       help='Filter by spell level (0 for cantrips)')
    parser.add_argument('--school', 
                       choices=['abjuration', 'conjuration', 'divination', 
                               'enchantment', 'evocation', 'illusion', 
                               'necromancy', 'transmutation'],
                       help='Filter by magic school')
    parser.add_argument('--class', dest='spell_class',
                       choices=['barbarian', 'bard', 'cleric', 'druid', 
                               'fighter', 'monk', 'paladin', 'ranger', 
                               'rogue', 'sorcerer', 'warlock', 'wizard'],
                       help='Filter by class spell list')
    parser.add_argument('--ritual', action='store_true',
                       help='Show only ritual spells')
    parser.add_argument('--concentration', action='store_true',
                       help='Show only concentration spells')
    parser.add_argument('--limit', type=int, default=20,
                       help='Maximum results (default: 20)')
    
    args = parser.parse_args()
    
    # Fetch all spells
    data = fetch("/api/2014/spells")
    
    if "error" in data:
        error_output(f"Failed to fetch spells: {data.get('message', 'Unknown error')}")
    
    spells = data.get("results", [])
    
    # Apply filters
    if any([args.search, args.level is not None, args.school, 
            args.spell_class, args.ritual, args.concentration]):
        spells = filter_spells(spells, args)
    
    # Apply limit
    total = len(spells)
    if args.limit and len(spells) > args.limit:
        spells = spells[:args.limit]
    
    # Format output
    formatted = format_spell_list(spells)
    
    output({
        "count": len(spells),
        "total": total,
        "results": formatted if isinstance(formatted[0], dict) and "level" in formatted[0] else spells
    })

if __name__ == "__main__":
    main()