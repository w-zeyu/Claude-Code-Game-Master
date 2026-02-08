#!/usr/bin/env python3
"""
Get traits for a specific race
Usage: uv run python get_traits.py <race>
Example: uv run python get_traits.py elf
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from character_creation_core import fetch, output, error_output

def get_trait_details(trait_url):
    """Fetch details for a specific trait"""
    # Handle both full URLs and relative URLs
    if trait_url.startswith("http"):
        # Extract endpoint from full URL
        endpoint = trait_url.replace("https://www.dnd5eapi.co/api/2014", "")
    elif trait_url.startswith("/api/2014"):
        # Already a relative URL with /api/2014 prefix - strip it
        endpoint = trait_url.replace("/api/2014", "")
    else:
        # Already the correct endpoint format
        endpoint = trait_url

    trait_data = fetch(endpoint)
    
    if "error" in trait_data:
        return None
    
    return {
        "name": trait_data.get("name", ""),
        "desc": trait_data.get("desc", []),
        "proficiencies": [
            prof.get("name", "") for prof in trait_data.get("proficiencies", [])
        ]
    }

def main():
    parser = argparse.ArgumentParser(description='Get racial traits')
    parser.add_argument('race', help='Race identifier (e.g., elf, dwarf)')
    
    args = parser.parse_args()
    
    # Convert to API format
    race_id = args.race.lower().replace(' ', '-')
    
    # First fetch race details to get trait URLs
    race_data = fetch(f"/races/{race_id}")
    
    if "error" in race_data:
        if race_data.get("error") == "HTTP 404":
            error_output(f"Race '{args.race}' not found")
        else:
            error_output(f"Failed to fetch race: {race_data.get('message', 'Unknown error')}")
    
    # Get detailed trait information
    traits = []
    for trait_ref in race_data.get("traits", []):
        trait_details = get_trait_details(trait_ref.get("url", ""))
        if trait_details:
            traits.append(trait_details)
    
    # Output formatted data
    output({
        "race": race_data.get("name", ""),
        "count": len(traits),
        "traits": traits
    })

if __name__ == "__main__":
    main()