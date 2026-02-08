#!/usr/bin/env python3
"""
List and search D&D 5e rules
Usage: uv run python list_rules.py [options]
Examples:
    uv run python list_rules.py                    # List all rules
    uv run python list_rules.py --search combat    # Search for combat rules
    uv run python list_rules.py --limit 5          # Show only 5 rules
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from rules_api_core import fetch, output, error_output

def filter_rules(rules, args):
    """Apply filters to rules list"""
    results = []
    
    for rule in rules:
        # Search filter
        if args.search:
            if args.search.lower() not in rule["name"].lower():
                continue
        
        results.append({
            "name": rule["name"],
            "index": rule["index"],
            "url": rule["url"]
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description='List and search D&D 5e rules')
    parser.add_argument('--search', help='Search rules by name')
    parser.add_argument('--limit', type=int, default=20, help='Max results (default: 20)')
    parser.add_argument('--sections', action='store_true', help='List rule sections instead')
    
    args = parser.parse_args()
    
    # Fetch the appropriate endpoint
    if args.sections:
        data = fetch("/rule-sections")
    else:
        data = fetch("/rules")
    
    if "error" in data:
        error_output(f"Failed to fetch rules: {data.get('message', 'Unknown error')}")
    
    rules = data.get("results", [])
    
    # Apply filters
    if args.search:
        rules = filter_rules(rules, args)
    
    # Apply limit
    if args.limit and len(rules) > args.limit:
        rules = rules[:args.limit]
    
    # Format output
    output({
        "count": len(rules),
        "total": data.get("count", 0),
        "type": "rule-sections" if args.sections else "rules",
        "results": rules
    })

if __name__ == "__main__":
    main()