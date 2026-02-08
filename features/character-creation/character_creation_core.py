#!/usr/bin/env python3
"""
Character Creation Core - Simple request wrapper for D&D 5e API
Just makes requests and returns JSON. Nothing fancy.
"""

import json
import sys
import urllib.request
import urllib.error

BASE_URL = "https://www.dnd5eapi.co/api/2014"

def fetch(endpoint):
    """Fetch data from API and return as dict"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "message": e.reason}
    except Exception as e:
        return {"error": "Request failed", "message": str(e)}

def output(data):
    """Output data as JSON to stdout"""
    print(json.dumps(data, indent=2))

def error_output(message):
    """Output error in consistent format"""
    output({"error": message})
    sys.exit(1)