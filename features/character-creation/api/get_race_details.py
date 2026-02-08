#!/usr/bin/env python3
"""
Get detailed information about a specific race
Usage: uv run python get_race_details.py <race>
Example: uv run python get_race_details.py elf
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from character_creation_core import fetch, output, error_output

def extract_race_details(race_data):
    """Extract key race information"""
    return {
        "name": race_data.get("name", "Unknown"),
        "size": race_data.get("size", ""),
        "speed": race_data.get("speed", 30),
        "ability_bonuses": [
            {
                "ability": bonus.get("ability_score", {}).get("name", ""),
                "bonus": bonus.get("bonus", 0)
            }
            for bonus in race_data.get("ability_bonuses", [])
        ],
        "traits": [
            {
                "name": trait.get("name", ""),
                "url": trait.get("url", "")
            }
            for trait in race_data.get("traits", [])
        ],
        "languages": [
            lang.get("name", "") for lang in race_data.get("languages", [])
        ],
        "subraces": [
            {
                "name": subrace.get("name", ""),
                "index": subrace.get("index", "")
            }
            for subrace in race_data.get("subraces", [])
        ]
    }

def main():
    parser = argparse.ArgumentParser(description='Get race details')
    parser.add_argument('race', help='Race identifier (e.g., elf, dwarf)')
    
    args = parser.parse_args()
    
    # Convert to API format
    race_id = args.race.lower().replace(' ', '-')
    
    # Fetch race details
    data = fetch(f"/races/{race_id}")
    
    if "error" in data:
        if data.get("error") == "HTTP 404":
            error_output(f"Race '{args.race}' not found")
        else:
            error_output(f"Failed to fetch race: {data.get('message', 'Unknown error')}")
    
    # Extract and output details
    output(extract_race_details(data))

if __name__ == "__main__":
    main()