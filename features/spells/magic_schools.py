#!/usr/bin/env python3
"""
Get D&D 5e magic school information
Usage: uv run python magic_schools.py [school-name]
Examples:
    uv run python magic_schools.py              # List all magic schools
    uv run python magic_schools.py evocation    # Get evocation school details
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from spell_api_core import fetch, output, error_output

def main():
    parser = argparse.ArgumentParser(description='Get magic school information')
    parser.add_argument('school_name', nargs='?', 
                       help='Name of the magic school (optional)')
    
    args = parser.parse_args()
    
    if args.school_name:
        # Get specific school
        school_index = args.school_name.lower()
        data = fetch(f"/api/2014/magic-schools/{school_index}")
        
        if "error" in data:
            if data.get("error") == "HTTP 404":
                error_output(f"Magic school '{args.school_name}' not found")
            else:
                error_output(f"Failed to fetch school: {data.get('message', 'Unknown error')}")
        
        # Format the description nicely
        if "desc" in data:
            data["description"] = " ".join(data["desc"])
            del data["desc"]
        
        output(data)
    else:
        # List all schools
        data = fetch("/api/2014/magic-schools")
        
        if "error" in data:
            error_output(f"Failed to fetch magic schools: {data.get('message', 'Unknown error')}")
        
        schools = data.get("results", [])
        
        # Fetch details for each school to get descriptions
        detailed_schools = []
        for school in schools:
            school_data = fetch(school["url"])
            if "error" not in school_data:
                detailed_schools.append({
                    "name": school_data.get("name", "Unknown"),
                    "index": school_data.get("index", ""),
                    "description": " ".join(school_data.get("desc", []))[:200] + "..."
                })
        
        output({
            "count": len(detailed_schools),
            "schools": detailed_schools
        })

if __name__ == "__main__":
    main()