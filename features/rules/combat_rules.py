#!/usr/bin/env python3
"""
D&D 5e combat rules quick reference
Usage: uv run python combat_rules.py [topic]
Examples:
    uv run python combat_rules.py              # List combat topics
    uv run python combat_rules.py actions      # List combat actions
    uv run python combat_rules.py cover        # Get cover rules
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from rules_api_core import fetch, output, error_output

# Combat rules reference data
COMBAT_TOPICS = {
    "actions": {
        "name": "Combat Actions",
        "description": "Actions you can take in combat",
        "content": {
            "Attack": "Make one melee or ranged attack",
            "Cast a Spell": "Cast a spell with casting time of 1 action",
            "Dash": "Double your movement for the turn",
            "Dodge": "Attacks against you have disadvantage, Dex saves have advantage",
            "Help": "Give advantage to an ally's next ability check or attack",
            "Hide": "Make a Stealth check to become hidden",
            "Ready": "Prepare to trigger an action with a reaction",
            "Search": "Devote your attention to finding something",
            "Use an Object": "Interact with an object that requires an action"
        }
    },
    "bonus-actions": {
        "name": "Bonus Actions",
        "description": "Can only use if a feature grants you one",
        "content": {
            "General": "Only one bonus action per turn",
            "Timing": "Can be taken before, after, or between attacks",
            "Examples": "Off-hand attack, Cunning Action, Healing Word, etc."
        }
    },
    "reactions": {
        "name": "Reactions",
        "description": "Instant responses to triggers",
        "content": {
            "Frequency": "One reaction per round (resets on your turn)",
            "Opportunity Attack": "When enemy leaves your reach using movement",
            "Readied Action": "When your specified trigger occurs",
            "Spells": "Shield, Counterspell, etc. when triggered"
        }
    },
    "movement": {
        "name": "Movement Rules",
        "description": "How movement works in combat",
        "content": {
            "Breaking Up": "Can split movement before/after/between actions",
            "Difficult Terrain": "Every 1 foot costs 2 feet of movement",
            "Prone": "Crawling costs 2 feet per 1 foot, standing up costs half movement",
            "Grappled": "Speed becomes 0, can't benefit from speed bonuses"
        }
    },
    "cover": {
        "name": "Cover Rules",
        "description": "Protection from attacks and effects",
        "content": {
            "Half Cover": "+2 AC and Dex saves (low wall, furniture, creatures)",
            "Three-Quarters": "+5 AC and Dex saves (arrow slit, thick tree)",
            "Total Cover": "Can't be targeted directly (completely concealed)"
        }
    },
    "conditions": {
        "name": "Common Combat Conditions",
        "description": "Status effects in combat",
        "content": {
            "Advantage": "Roll twice, take higher",
            "Disadvantage": "Roll twice, take lower",
            "See Also": "Use 'uv run python conditions.py' for full condition list"
        }
    },
    "death": {
        "name": "Death & Dying",
        "description": "Rules for 0 hit points",
        "content": {
            "Unconscious": "At 0 HP, fall unconscious",
            "Death Saves": "DC 10 Con save, 3 successes = stable, 3 failures = death",
            "Natural 20": "Regain 1 HP and consciousness",
            "Natural 1": "Counts as 2 failures",
            "Damage at 0 HP": "Auto-fail 1 death save (2 if crit)"
        }
    },
    "surprise": {
        "name": "Surprise Rules",
        "description": "Ambush mechanics",
        "content": {
            "Determination": "Compare Stealth vs Passive Perception",
            "Effect": "Surprised creatures can't move or act on first turn",
            "After Turn": "Can take reactions after their first turn ends"
        }
    },
    "two-weapon": {
        "name": "Two-Weapon Fighting",
        "description": "Fighting with two weapons",
        "content": {
            "Requirements": "Both weapons must have 'light' property",
            "Bonus Action": "Attack with off-hand weapon",
            "No Modifier": "Don't add ability modifier to damage (unless negative)",
            "Fighting Style": "Two-Weapon Fighting style adds modifier to damage"
        }
    },
    "grappling": {
        "name": "Grappling Rules",
        "description": "Grabbing and restraining",
        "content": {
            "Initiate": "Attack action, Athletics vs Athletics/Acrobatics",
            "Effect": "Target's speed becomes 0",
            "Escape": "Action to contest check again",
            "Moving": "Half speed when dragging grappled creature"
        }
    },
    "shoving": {
        "name": "Shoving Rules",
        "description": "Pushing creatures",
        "content": {
            "Initiate": "Attack action, Athletics vs Athletics/Acrobatics",
            "Effect": "Push 5 feet away OR knock prone",
            "Size": "Can't shove creature more than one size larger"
        }
    }
}

def get_combat_topic(topic):
    """Get specific combat topic details"""
    topic_key = topic.lower().replace(' ', '-')
    
    if topic_key in COMBAT_TOPICS:
        return COMBAT_TOPICS[topic_key]
    
    # Try to find partial matches
    matches = []
    for key, data in COMBAT_TOPICS.items():
        if topic.lower() in data["name"].lower() or topic.lower() in key:
            matches.append(data["name"])
    
    if matches:
        return {
            "error": f"Topic '{topic}' not found. Did you mean:",
            "suggestions": matches
        }
    
    return {"error": f"Combat topic '{topic}' not found"}

def list_combat_topics():
    """List all available combat topics"""
    topics = []
    for key, data in COMBAT_TOPICS.items():
        topics.append({
            "topic": key,
            "name": data["name"],
            "description": data["description"]
        })
    
    return {
        "combat_topics": topics,
        "usage": "Use 'uv run python combat_rules.py <topic>' for details"
    }

def main():
    parser = argparse.ArgumentParser(description='D&D 5e combat rules reference')
    parser.add_argument('topic', nargs='?', help='Combat topic (optional)')
    
    args = parser.parse_args()
    
    # If no topic specified, list all
    if not args.topic:
        output(list_combat_topics())
        return
    
    # Get specific topic
    result = get_combat_topic(args.topic)
    
    if "error" in result:
        if "suggestions" in result:
            error_output(f"{result['error']}\n" + 
                       "\n".join([f"- {s}" for s in result['suggestions']]))
        else:
            error_output(result["error"])
    
    output(result)

if __name__ == "__main__":
    main()