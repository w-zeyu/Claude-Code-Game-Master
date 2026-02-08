#!/usr/bin/env python3
"""
Get D&D 5e condition rules and effects
Usage: uv run python conditions.py [condition]
Examples:
    uv run python conditions.py                # List all conditions
    uv run python conditions.py stunned        # Get stunned condition details
    uv run python conditions.py paralyzed      # Get paralyzed condition details
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from rules_api_core import fetch, output, error_output

def format_condition_details(condition):
    """Format condition for detailed display"""
    formatted = {
        "name": condition.get("name", "Unknown"),
        "effects": condition.get("desc", []),
    }
    
    # Add any additional fields if they exist
    if "url" in condition:
        formatted["reference"] = condition["url"]
    
    return formatted

def list_all_conditions():
    """List all available conditions"""
    data = fetch("/conditions")
    
    if "error" in data:
        error_output(f"Failed to fetch conditions: {data.get('message', 'Unknown error')}")
    
    conditions = []
    for condition in data.get("results", []):
        conditions.append({
            "name": condition["name"],
            "index": condition["index"]
        })
    
    return {
        "count": len(conditions),
        "conditions": conditions,
        "usage": "Use 'uv run python conditions.py <condition-name>' for details"
    }

def main():
    parser = argparse.ArgumentParser(description='Get D&D 5e condition information')
    parser.add_argument('condition', nargs='?', help='Condition name (optional)')
    
    args = parser.parse_args()
    
    # If no condition specified, list all
    if not args.condition:
        output(list_all_conditions())
        return
    
    # Convert condition name to API format
    condition_index = args.condition.lower().replace(' ', '-')
    
    # Fetch specific condition
    data = fetch(f"/conditions/{condition_index}")
    
    if "error" in data:
        if data.get("error") == "HTTP 404":
            # Try to find similar conditions
            all_conditions = fetch("/conditions")
            if "error" not in all_conditions:
                suggestions = []
                for cond in all_conditions.get("results", []):
                    if args.condition.lower() in cond["name"].lower():
                        suggestions.append(cond["name"])
                
                if suggestions:
                    error_output(f"Condition '{args.condition}' not found. Did you mean:\n" + 
                               "\n".join([f"- {s}" for s in suggestions[:3]]))
            
            error_output(f"Condition '{args.condition}' not found")
        else:
            error_output(f"Failed to fetch condition: {data.get('message', 'Unknown error')}")
    
    # Format and output
    output(format_condition_details(data))

if __name__ == "__main__":
    main()