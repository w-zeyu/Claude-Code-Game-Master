#!/usr/bin/env python3
"""
Get D&D 5e damage type information
Usage: uv run python damage_types.py [damage-type]
Examples:
    uv run python damage_types.py         # List all damage types
    uv run python damage_types.py fire    # Get fire damage details
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from spell_api_core import fetch, output, error_output

def main():
    parser = argparse.ArgumentParser(description='Get damage type information')
    parser.add_argument('damage_type', nargs='?', 
                       help='Name of the damage type (optional)')
    
    args = parser.parse_args()
    
    if args.damage_type:
        # Get specific damage type
        damage_index = args.damage_type.lower()
        data = fetch(f"/api/2014/damage-types/{damage_index}")
        
        if "error" in data:
            if data.get("error") == "HTTP 404":
                error_output(f"Damage type '{args.damage_type}' not found")
            else:
                error_output(f"Failed to fetch damage type: {data.get('message', 'Unknown error')}")
        
        # Format the description nicely
        if "desc" in data:
            data["description"] = " ".join(data["desc"])
            del data["desc"]
        
        output(data)
    else:
        # List all damage types
        data = fetch("/api/2014/damage-types")
        
        if "error" in data:
            error_output(f"Failed to fetch damage types: {data.get('message', 'Unknown error')}")
        
        damage_types = data.get("results", [])
        
        # Fetch details for each type to get descriptions
        detailed_types = []
        for dtype in damage_types:
            type_data = fetch(dtype["url"])
            if "error" not in type_data:
                detailed_types.append({
                    "name": type_data.get("name", "Unknown"),
                    "index": type_data.get("index", ""),
                    "description": " ".join(type_data.get("desc", []))
                })
        
        output({
            "count": len(detailed_types),
            "damage_types": detailed_types
        })

if __name__ == "__main__":
    main()