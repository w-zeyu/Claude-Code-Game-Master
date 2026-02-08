#!/usr/bin/env python3
"""
Get all available D&D classes
Usage: uv run python get_classes.py
Example: uv run python get_classes.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from character_creation_core import fetch, output, error_output

def format_class_info(class_data):
    """Format class info for character creation"""
    return {
        "index": class_data.get("index", ""),
        "name": class_data.get("name", "Unknown"),
        "url": class_data.get("url", "")
    }

def main():
    # Fetch all classes
    data = fetch("/classes")
    
    if "error" in data:
        error_output(f"Failed to fetch classes: {data.get('message', 'Unknown error')}")
    
    # Format class list
    classes = []
    for class_item in data.get("results", []):
        classes.append(format_class_info(class_item))
    
    # Output formatted data
    output({
        "count": len(classes),
        "classes": classes
    })

if __name__ == "__main__":
    main()