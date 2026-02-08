#!/usr/bin/env python3
"""
Get spells for a specific class and level
Usage: uv run python get_spells.py --class <class> --level <level>
Example: uv run python get_spells.py --class wizard --level 1
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from character_creation_core import fetch, output, error_output

def format_spell_info(spell_data):
    """Format spell info for display"""
    return {
        "index": spell_data.get("index", ""),
        "name": spell_data.get("name", "Unknown"),
        "level": spell_data.get("level", 0),
        "url": spell_data.get("url", "")
    }

def main():
    parser = argparse.ArgumentParser(description='Get class spells by level')
    parser.add_argument('--class', dest='class_name', required=True, 
                       help='Class name (e.g., wizard, cleric)')
    parser.add_argument('--level', type=int, required=True,
                       help='Spell level (0-9, where 0 is cantrips)')
    
    args = parser.parse_args()
    
    # Validate spell level
    if args.level < 0 or args.level > 9:
        error_output("Spell level must be between 0 and 9")
    
    # Convert to API format
    class_id = args.class_name.lower().replace(' ', '-')
    
    # First check if class exists and can cast spells
    class_data = fetch(f"/classes/{class_id}")
    
    if "error" in class_data:
        if class_data.get("error") == "HTTP 404":
            error_output(f"Class '{args.class_name}' not found")
        else:
            error_output(f"Failed to fetch class: {class_data.get('message', 'Unknown error')}")
    
    if not class_data.get("spellcasting"):
        error_output(f"{args.class_name} is not a spellcasting class")
    
    # Fetch spells for this class and level
    spells_data = fetch(f"/classes/{class_id}/spells?level={args.level}")
    
    if "error" in spells_data:
        error_output(f"Failed to fetch spells: {spells_data.get('message', 'Unknown error')}")
    
    # Format spell list
    spells = []
    for spell in spells_data.get("results", []):
        spells.append(format_spell_info(spell))
    
    # Output formatted data
    output({
        "class": class_data.get("name", ""),
        "spell_level": args.level,
        "count": len(spells),
        "spells": spells
    })

if __name__ == "__main__":
    main()