#!/usr/bin/env python3
"""
Get all available D&D skills
Usage: uv run python get_skills.py
Example: uv run python get_skills.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from character_creation_core import fetch, output, error_output

def format_skill_info(skill_data):
    """Format skill info for character creation"""
    return {
        "index": skill_data.get("index", ""),
        "name": skill_data.get("name", "Unknown"),
        "url": skill_data.get("url", "")
    }

def main():
    # Fetch all skills
    data = fetch("/skills")
    
    if "error" in data:
        error_output(f"Failed to fetch skills: {data.get('message', 'Unknown error')}")
    
    # Format skill list
    skills = []
    for skill in data.get("results", []):
        skills.append(format_skill_info(skill))
    
    # Output formatted data
    output({
        "count": len(skills),
        "skills": skills
    })

if __name__ == "__main__":
    main()