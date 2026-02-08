#!/usr/bin/env python3
"""
Get all available D&D races
Usage: uv run python get_races.py
Example: uv run python get_races.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from character_creation_core import fetch, output, error_output

def format_race_info(race_data):
    """Format race info for character creation"""
    return {
        "index": race_data.get("index", ""),
        "name": race_data.get("name", "Unknown"),
        "url": race_data.get("url", "")
    }

def main():
    # Fetch all races
    data = fetch("/races")
    
    if "error" in data:
        error_output(f"Failed to fetch races: {data.get('message', 'Unknown error')}")
    
    # Format race list
    races = []
    for race in data.get("results", []):
        races.append(format_race_info(race))
    
    # Output formatted data
    output({
        "count": len(races),
        "races": races
    })

if __name__ == "__main__":
    main()