#!/usr/bin/env python3
"""
Semantic Query Definitions for RAG-based Extraction

Natural language query templates for identifying different content types.
No regex - pure semantic matching via embeddings.
"""

from typing import Dict, List


# Query templates for each content type
# Multiple queries per type to capture different phrasings and contexts
EXTRACTION_QUERIES: Dict[str, List[str]] = {
    "npc": [
        # Character identification
        "character named who is described as personality appearance",
        "NPC non-player character with stats abilities traits",
        "person individual creature with name description motivation",

        # Dialogue and interaction
        "character speaks says tells asks dialogue conversation",
        "personality trait behavior attitude disposition temperament",

        # Stats and abilities
        "character with AC HP hit points strength dexterity constitution",
        "NPC stat block challenge rating abilities skills",
        "creature monster enemy with combat statistics",

        # Roles and relationships
        "villain antagonist enemy threat adversary evil",
        "ally friend helper guide mentor companion",
        "shopkeeper merchant innkeeper tavern owner vendor",
        "noble lord lady duke duchess royalty aristocrat",
        "guard soldier warrior fighter knight defender",
    ],

    "location": [
        # Places
        "location place area region zone territory",
        "room chamber hall corridor passage hallway dungeon",
        "building structure tower castle fortress stronghold",
        "town city village settlement community outpost",
        "forest woods wilderness wild nature outdoor",
        "cave cavern underground tunnel mine depth",

        # Navigation
        "north south east west direction pathway route",
        "entrance exit door gate portal threshold",
        "stairs ladder climb descend ascent descent",
        "bridge path road trail journey travel",

        # Description
        "place described as decorated furnished contains features",
        "area with walls floor ceiling architecture style",
        "environment atmosphere mood lighting ambiance setting",
        "landmark notable feature prominent visible sight",
    ],

    "item": [
        # Treasure and wealth
        "gold silver copper platinum treasure wealth coins",
        "gp sp cp pp currency money payment reward",
        "gems jewels precious stones valuable treasure hoard",

        # Weapons
        "sword axe bow crossbow dagger staff polearm weapon",
        "blade edge sharp cutting piercing slashing damage",
        "ranged weapon projectile ammunition arrow bolt",

        # Armor and protection
        "armor shield helm helmet protection defense AC",
        "plate mail leather studded chain scale armor type",
        "resistance immunity protection ward barrier",

        # Magic items
        "magic magical enchanted cursed blessed item artifact",
        "ring amulet necklace pendant cloak robe wondrous item",
        "potion scroll wand rod staff consumable charge",
        "common uncommon rare very rare legendary artifact rarity",
        "plus one plus two plus three bonus enhancement",
        "attunement requires attuned magical property effect",
    ],

    "plot": [
        # Quests and objectives
        "quest mission task objective goal assignment",
        "adventure hook storyline plot narrative arc",
        "purpose reason motivation goal objective aim",

        # Conditions and triggers
        "if when after before once should trigger condition",
        "event happens occurs takes place transpires unfolds",
        "consequence result outcome effect impact aftermath",

        # Story elements
        "rumor legend story tale history lore myth",
        "mystery secret hidden unknown discovery revelation",
        "prophecy prediction foretelling destiny fate",
        "conflict challenge obstacle problem threat danger",

        # Rewards and progression
        "reward payment treasure prize compensation",
        "experience XP level advancement progression",
        "reputation fame renown honor standing",
        "faction guild organization group alliance",
    ],

    "voice": [
        # Direct dialogue
        "dialogue speech says speaks tells asks replies exclaims whispers",
        "quote direct speech conversation verbal exchange words",
        "character says tells asks responds answers declares states",

        # Speech patterns and manner
        "voice tone manner speaking accent dialect speech pattern",
        "speaks in a with manner voice characteristic verbal",
        "how character talks communicates addresses others",

        # Personality through speech
        "personality demeanor behavior mannerism characteristic trait",
        "attitude disposition temperament nature character quality",
        "when speaking addresses others interacts converses",
    ],
}


def get_queries_for_type(content_type: str) -> List[str]:
    """
    Get all query templates for a specific content type.

    Args:
        content_type: One of 'npc', 'location', 'item', 'plot', 'voice'

    Returns:
        List of query template strings
    """
    return EXTRACTION_QUERIES.get(content_type, [])


def get_all_types() -> List[str]:
    """Get all content type names."""
    return list(EXTRACTION_QUERIES.keys())


def get_combined_queries() -> Dict[str, str]:
    """
    Get a single combined query per type (for simpler matching).

    Returns:
        Dict mapping content type to combined query string.
    """
    return {
        content_type: " ".join(queries)
        for content_type, queries in EXTRACTION_QUERIES.items()
    }


def main():
    """Display query statistics."""
    print("Extraction Query Statistics:")
    print("=" * 40)

    for content_type, queries in EXTRACTION_QUERIES.items():
        print(f"\n{content_type.upper()} ({len(queries)} queries):")
        for i, query in enumerate(queries[:3], 1):
            print(f"  {i}. {query[:60]}...")
        if len(queries) > 3:
            print(f"  ... and {len(queries) - 3} more")

    print("\n" + "=" * 40)
    total = sum(len(q) for q in EXTRACTION_QUERIES.values())
    print(f"Total queries: {total}")


if __name__ == "__main__":
    main()
