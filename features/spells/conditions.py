#!/usr/bin/env python3
"""
Get D&D 5e condition information
Usage: uv run python conditions.py [condition-name]
Examples:
    uv run python conditions.py             # List all conditions
    uv run python conditions.py stunned     # Get stunned condition details
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from spell_api_core import fetch, output, error_output

def main():
    parser = argparse.ArgumentParser(description='Get condition information')
    parser.add_argument('condition_name', nargs='?', 
                       help='Name of the condition (optional)')
    
    args = parser.parse_args()
    
    if args.condition_name:
        # Get specific condition
        condition_index = args.condition_name.lower()
        data = fetch(f"/api/2014/conditions/{condition_index}")
        
        if "error" in data:
            if data.get("error") == "HTTP 404":
                error_output(f"Condition '{args.condition_name}' not found")
            else:
                error_output(f"Failed to fetch condition: {data.get('message', 'Unknown error')}")
        
        # Format the description nicely
        if "desc" in data:
            data["description"] = " ".join(data["desc"])
            data["effects"] = data["desc"]  # Keep the list format for effects
            del data["desc"]
        
        output(data)
    else:
        # List all conditions
        data = fetch("/api/2014/conditions")
        
        if "error" in data:
            error_output(f"Failed to fetch conditions: {data.get('message', 'Unknown error')}")
        
        conditions = data.get("results", [])
        
        # Fetch details for each condition to get descriptions
        detailed_conditions = []
        for condition in conditions:
            condition_data = fetch(condition["url"])
            if "error" not in condition_data:
                effects = condition_data.get("desc", [])
                detailed_conditions.append({
                    "name": condition_data.get("name", "Unknown"),
                    "index": condition_data.get("index", ""),
                    "summary": effects[0] if effects else "No description available",
                    "effects_count": len(effects)
                })
        
        output({
            "count": len(detailed_conditions),
            "conditions": detailed_conditions
        })

if __name__ == "__main__":
    main()