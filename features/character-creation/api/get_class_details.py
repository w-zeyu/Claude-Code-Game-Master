#!/usr/bin/env python3
"""
Get detailed information about a specific class
Usage: uv run python get_class_details.py <class>
Example: uv run python get_class_details.py wizard
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from character_creation_core import fetch, output, error_output

def extract_class_details(class_data):
    """Extract key class information"""
    return {
        "name": class_data.get("name", "Unknown"),
        "hit_die": class_data.get("hit_die", 0),
        "primary_ability": class_data.get("primary_ability", ""),
        "saving_throw_proficiencies": [
            prof.get("name", "") for prof in class_data.get("saving_throws", [])
        ],
        "proficiencies": [
            prof.get("name", "") for prof in class_data.get("proficiencies", [])
        ],
        "skill_choices": {
            "choose": class_data.get("proficiency_choices", [{}])[0].get("choose", 0) if class_data.get("proficiency_choices") else 0,
            "from": [
                option.get("item", {}).get("name", "") 
                for option in class_data.get("proficiency_choices", [{}])[0].get("from", {}).get("options", [])
            ] if class_data.get("proficiency_choices") else []
        },
        "starting_equipment": [
            equip.get("equipment", {}).get("name", "") 
            for equip in class_data.get("starting_equipment", [])
        ],
        "spellcasting": bool(class_data.get("spellcasting", None)),
        "subclasses": [
            {
                "name": subclass.get("name", ""),
                "index": subclass.get("index", "")
            }
            for subclass in class_data.get("subclasses", [])
        ]
    }

def main():
    parser = argparse.ArgumentParser(description='Get class details')
    parser.add_argument('class_name', help='Class identifier (e.g., wizard, fighter)')
    
    args = parser.parse_args()
    
    # Convert to API format
    class_id = args.class_name.lower().replace(' ', '-')
    
    # Fetch class details
    data = fetch(f"/classes/{class_id}")
    
    if "error" in data:
        if data.get("error") == "HTTP 404":
            error_output(f"Class '{args.class_name}' not found")
        else:
            error_output(f"Failed to fetch class: {data.get('message', 'Unknown error')}")
    
    # Extract and output details
    output(extract_class_details(data))

if __name__ == "__main__":
    main()