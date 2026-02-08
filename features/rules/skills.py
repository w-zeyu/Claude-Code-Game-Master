#!/usr/bin/env python3
"""
Get D&D 5e skill information and rules
Usage: uv run python skills.py [skill]
Examples:
    uv run python skills.py                    # List all skills
    uv run python skills.py stealth            # Get stealth skill details
    uv run python skills.py "sleight of hand"  # Get sleight of hand details
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from rules_api_core import fetch, output, error_output

def format_skill_details(skill):
    """Format skill for detailed display"""
    formatted = {
        "name": skill.get("name", "Unknown"),
        "ability": skill.get("ability_score", {}).get("name", "Unknown"),
        "description": skill.get("desc", [])
    }
    
    # Add typical DCs
    formatted["typical_dcs"] = {
        "very_easy": 5,
        "easy": 10,
        "medium": 15,
        "hard": 20,
        "very_hard": 25,
        "nearly_impossible": 30
    }
    
    return formatted

def list_all_skills():
    """List all available skills grouped by ability"""
    data = fetch("/skills")
    
    if "error" in data:
        error_output(f"Failed to fetch skills: {data.get('message', 'Unknown error')}")
    
    # Group skills by ability
    skills_by_ability = {}
    
    for skill in data.get("results", []):
        ability = skill.get("ability_score", {}).get("name", "Unknown")
        if ability not in skills_by_ability:
            skills_by_ability[ability] = []
        
        skills_by_ability[ability].append({
            "name": skill["name"],
            "index": skill["index"]
        })
    
    return {
        "count": data.get("count", 0),
        "skills_by_ability": skills_by_ability,
        "usage": "Use 'uv run python skills.py <skill-name>' for details"
    }

def main():
    parser = argparse.ArgumentParser(description='Get D&D 5e skill information')
    parser.add_argument('skill', nargs='?', help='Skill name (optional)')
    parser.add_argument('--dc', type=int, help='Check what difficulty a DC represents')
    
    args = parser.parse_args()
    
    # If DC check requested
    if args.dc is not None:
        difficulties = [
            (5, "Very Easy"),
            (10, "Easy"),
            (15, "Medium"),
            (20, "Hard"),
            (25, "Very Hard"),
            (30, "Nearly Impossible")
        ]
        
        difficulty = "Beyond Nearly Impossible"
        for dc, desc in difficulties:
            if args.dc <= dc:
                difficulty = desc
                break
        
        output({
            "dc": args.dc,
            "difficulty": difficulty,
            "description": f"DC {args.dc} is considered '{difficulty}' by standard rules"
        })
        return
    
    # If no skill specified, list all
    if not args.skill:
        output(list_all_skills())
        return
    
    # Convert skill name to API format
    skill_index = args.skill.lower().replace(' ', '-')
    
    # Fetch specific skill
    data = fetch(f"/skills/{skill_index}")
    
    if "error" in data:
        if data.get("error") == "HTTP 404":
            # Try to find similar skills
            all_skills = fetch("/skills")
            if "error" not in all_skills:
                suggestions = []
                for skill in all_skills.get("results", []):
                    if args.skill.lower() in skill["name"].lower():
                        suggestions.append(skill["name"])
                
                if suggestions:
                    error_output(f"Skill '{args.skill}' not found. Did you mean:\n" + 
                               "\n".join([f"- {s}" for s in suggestions[:3]]))
            
            error_output(f"Skill '{args.skill}' not found")
        else:
            error_output(f"Failed to fetch skill: {data.get('message', 'Unknown error')}")
    
    # Format and output
    output(format_skill_details(data))

if __name__ == "__main__":
    main()