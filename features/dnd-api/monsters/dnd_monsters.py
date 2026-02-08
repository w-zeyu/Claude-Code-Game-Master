#!/usr/bin/env python3
"""
List and search D&D monsters with instant CR filtering
Usage: uv run python dnd_monsters_instant.py [options]
Examples:
    uv run python dnd_monsters_instant.py                    # List all monsters
    uv run python dnd_monsters_instant.py --cr 5            # CR 5 monsters
    uv run python dnd_monsters_instant.py --cr 1-5          # CR range
    uv run python dnd_monsters_instant.py --search dragon   # Search by name
"""

import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dnd_api_core import fetch, output, error_output

# Common monster CRs (pre-cached for instant filtering)
# This covers the most common monsters to avoid API calls
MONSTER_CR_TABLE = {
    # CR 0
    "awakened-shrub": 0, "baboon": 0, "badger": 0, "bat": 0, "cat": 0, "commoner": 0,
    "crab": 0, "crawling-claw": 0, "deer": 0, "eagle": 0, "frog": 0, "giant-fire-beetle": 0,
    "goat": 0, "hawk": 0, "homunculus": 0, "hyena": 0, "jackal": 0, "lemure": 0, "lizard": 0,
    "myconid-sprout": 0, "octopus": 0, "owl": 0, "quipper": 0, "rat": 0, "raven": 0,
    "scorpion": 0, "sea-horse": 0, "shrieker": 0, "spider": 0, "vulture": 0, "weasel": 0,
    
    # CR 0.125 (1/8)
    "bandit": 0.125, "blood-hawk": 0.125, "boggle": 0.125, "camel": 0.125, "cultist": 0.125,
    "dolphin": 0.125, "flumph": 0.125, "flying-snake": 0.125, "giant-crab": 0.125,
    "giant-rat": 0.125, "giant-weasel": 0.125, "guard": 0.125, "kobold": 0.125,
    "manes": 0.125, "mastiff": 0.125, "merfolk": 0.125, "monodrone": 0.125, "mule": 0.125,
    "neogi-hatchling": 0.125, "noble": 0.125, "poisonous-snake": 0.125, "pony": 0.125,
    "slaad-tadpole": 0.125, "stirge": 0.125, "tribal-warrior": 0.125, "twig-blight": 0.125,
    
    # CR 0.25 (1/4)
    "acolyte": 0.25, "aarakocra": 0.25, "axe-beak": 0.25, "blink-dog": 0.25, "boar": 0.25,
    "bullywug": 0.25, "constrictor-snake": 0.25, "draft-horse": 0.25, "dretch": 0.25,
    "drow": 0.25, "duodrone": 0.25, "elk": 0.25, "flying-sword": 0.25, "giant-badger": 0.25,
    "giant-bat": 0.25, "giant-centipede": 0.25, "giant-frog": 0.25, "giant-lizard": 0.25,
    "giant-owl": 0.25, "giant-poisonous-snake": 0.25, "giant-wolf-spider": 0.25,
    "goblin": 0.25, "grimlock": 0.25, "grung": 0.25, "kenku": 0.25, "kuo-toa": 0.25,
    "mud-mephit": 0.25, "needle-blight": 0.25, "panther": 0.25, "pixie": 0.25,
    "pseudodragon": 0.25, "pteranodon": 0.25, "riding-horse": 0.25, "skeleton": 0.25,
    "smoke-mephit": 0.25, "sprite": 0.25, "steam-mephit": 0.25, "swarm-of-bats": 0.25,
    "swarm-of-rats": 0.25, "swarm-of-ravens": 0.25, "troglodyte": 0.25, "vegepygmy": 0.25,
    "violet-fungus": 0.25, "winged-kobold": 0.25, "wolf": 0.25, "xvart": 0.25, "zombie": 0.25,
    
    # CR 0.5 (1/2)
    "ape": 0.5, "black-bear": 0.5, "chitine": 0.5, "cockatrice": 0.5, "crocodile": 0.5,
    "darkmantle": 0.5, "dust-mephit": 0.5, "firenewt-warrior": 0.5, "gas-spore": 0.5,
    "giant-goat": 0.5, "giant-sea-horse": 0.5, "giant-wasp": 0.5, "gnoll": 0.5,
    "gray-ooze": 0.5, "hobgoblin": 0.5, "ice-mephit": 0.5, "jackalwere": 0.5,
    "lizardfolk": 0.5, "magma-mephit": 0.5, "magmin": 0.5, "myconid-adult": 0.5,
    "orc": 0.5, "piercer": 0.5, "reef-shark": 0.5, "rust-monster": 0.5, "sahuagin": 0.5,
    "satyr": 0.5, "scout": 0.5, "shadow": 0.5, "skulk": 0.5, "swarm-of-insects": 0.5,
    "thug": 0.5, "tridrone": 0.5, "vine-blight": 0.5, "warhorse": 0.5, "warhorse-skeleton": 0.5,
    "worg": 0.5,
    
    # CR 1
    "animated-armor": 1, "brass-dragon-wyrmling": 1, "brown-bear": 1, "bugbear": 1,
    "choker": 1, "copper-dragon-wyrmling": 1, "death-dog": 1, "deinonychus": 1, "dire-wolf": 1,
    "dryad": 1, "duergar": 1, "faerie-dragon-young": 1, "fire-snake": 1, "ghoul": 1,
    "giant-eagle": 1, "giant-hyena": 1, "giant-octopus": 1, "giant-spider": 1, "giant-toad": 1,
    "giant-vulture": 1, "goblin-boss": 1, "half-ogre": 1, "harpy": 1, "hippogriff": 1,
    "imp": 1, "kuo-toa-whip": 1, "lion": 1, "quadrone": 1, "quaggoth-spore-servant": 1,
    "quasit": 1, "scarecrow": 1, "specter": 1, "spy": 1, "stirge": 1, "stone-cursed": 1,
    "swarm-of-quippers": 1, "thri-kreen": 1, "tiger": 1, "yuan-ti-pureblood": 1,
    
    # CR 2
    "allosaurus": 2, "ankheg": 2, "awakened-tree": 2, "azer": 2, "bandit-captain": 2,
    "berbalang": 2, "berserker": 2, "black-dragon-wyrmling": 2, "bronze-dragon-wyrmling": 2,
    "carrion-crawler": 2, "cave-bear": 2, "centaur": 2, "cult-fanatic": 2, "druid": 2,
    "ettercap": 2, "faerie-dragon-adult": 2, "gargoyle": 2, "gelatinous-cube": 2,
    "ghast": 2, "giant-boar": 2, "giant-constrictor-snake": 2, "giant-elk": 2,
    "gibbering-mouther": 2, "githyanki-warrior": 2, "githzerai-monk": 2, "gnoll-pack-lord": 2,
    "green-dragon-wyrmling": 2, "grick": 2, "griffon": 2, "guard-drake": 2, "hunter-shark": 2,
    "intellect-devourer": 2, "lizardfolk-shaman": 2, "meenlock": 2, "merrow": 2, "mimic": 2,
    "minotaur-skeleton": 2, "nothic": 2, "ochre-jelly": 2, "ogre": 2, "ogre-zombie": 2,
    "orc-eye-of-gruumsh": 2, "orog": 2, "pegasus": 2, "pentadrone": 2, "peryton": 2,
    "plesiosaurus": 2, "polar-bear": 2, "poltergeist": 2, "priest": 2, "quaggoth": 2,
    "rhinoceros": 2, "rug-of-smothering": 2, "saber-toothed-tiger": 2, "sahuagin-priestess": 2,
    "sea-hag": 2, "shadow-mastiff": 2, "silver-dragon-wyrmling": 2, "spined-devil": 2,
    "swarm-of-poisonous-snakes": 2, "tortle-druid": 2, "vegepygmy-chief": 2, "wererat": 2,
    "white-dragon-wyrmling": 2, "will-o-wisp": 2, "yuan-ti-broodguard": 2,
    
    # Higher CRs (common ones)
    "ankylosaurus": 3, "basilisk": 3, "bearded-devil": 3, "blue-dragon-wyrmling": 3,
    "bugbear-chief": 3, "cave-fisher": 3, "choldrith": 3, "doppelganger": 3, "giant-scorpion": 3,
    "gold-dragon-wyrmling": 3, "green-hag": 3, "hell-hound": 3, "hobgoblin-captain": 3,
    "hook-horror": 3, "killer-whale": 3, "knight": 3, "manticore": 3, "minotaur": 3,
    "mummy": 3, "neogi": 3, "nightmare": 3, "owlbear": 3, "phase-spider": 3, "quaggoth-thonot": 3,
    "red-dragon-wyrmling": 3, "shadow-demon": 3, "spectator": 3, "vampire-spawn": 3,
    "water-weird": 3, "werewolf": 3, "wight": 3, "winter-wolf": 3, "yeti": 3,
    "yuan-ti-malison": 3,
    
    "banshee": 4, "black-pudding": 4, "bone-naga": 4, "chuul": 4, "couatl": 4, "elephant": 4,
    "ettin": 4, "flameskull": 4, "ghost": 4, "gnoll-fang-of-yeenoghu": 4, "helmed-horror": 4,
    "incubus": 4, "lamia": 4, "lizard-king": 4, "orc-war-chief": 4, "red-slaad": 4,
    "shadow-dragon": 4, "succubus": 4, "wereboar": 4, "weretiger": 4,
    
    "air-elemental": 5, "barbed-devil": 5, "barlgura": 5, "beholder-zombie": 5, "bulette": 5,
    "cambion": 5, "drow-elite-warrior": 5, "earth-elemental": 5, "fire-elemental": 5,
    "flesh-golem": 5, "gorgon": 5, "half-red-dragon-veteran": 5, "hill-giant": 5,
    "mezzoloth": 5, "night-hag": 5, "otyugh": 5, "red-slaad": 5, "revenant": 5,
    "roper": 5, "sahuagin-baron": 5, "salamander": 5, "shambling-mound": 5, "triceratops": 5,
    "troll": 5, "umber-hulk": 5, "unicorn": 5, "vampire-spawn": 5, "water-elemental": 5,
    "werebear": 5, "wraith": 5, "xorn": 5, "young-remorhaz": 5, "yuan-ti-abomination": 5,
}

def parse_cr_range(cr_str):
    """Parse CR input like '5' or '1-5' into min/max values"""
    if '-' in cr_str:
        parts = cr_str.split('-')
        if len(parts) == 2:
            try:
                return float(parts[0]), float(parts[1])
            except ValueError:
                error_output(f"Invalid CR range: {cr_str}")
    else:
        try:
            cr = float(cr_str)
            return cr, cr
        except ValueError:
            error_output(f"Invalid CR value: {cr_str}")

def filter_monsters_instant(monsters, args):
    """Apply filters using pre-built CR table"""
    results = []
    unknown_cr_monsters = []
    
    for monster in monsters:
        # Name search first (fastest)
        if args.search:
            if args.search.lower() not in monster["name"].lower():
                continue
        
        # CR filter using pre-built table
        if args.cr:
            cr_range = parse_cr_range(args.cr)
            if cr_range is None:
                continue
            cr_min, cr_max = cr_range
            
            # Check if we have this monster's CR
            monster_cr = MONSTER_CR_TABLE.get(monster['index'])
            
            if monster_cr is None:
                # We don't have this monster's CR cached
                # Add to unknown list for potential fetching
                unknown_cr_monsters.append(monster)
                continue
            
            if not (cr_min <= monster_cr <= cr_max):
                continue
            
            # Add CR to output
            monster["cr"] = monster_cr
        
        results.append(monster)
    
    # If we're filtering by CR and found unknown monsters, fetch their details
    if args.cr and unknown_cr_monsters and len(unknown_cr_monsters) < 20:
        # Only fetch if there are few unknowns
        for monster in unknown_cr_monsters:
            details = fetch(f"/monsters/{monster['index']}")
            if "error" not in details:
                monster_cr = details.get("challenge_rating", 0)
                try:
                    monster_cr = float(monster_cr)
                    cr_range = parse_cr_range(args.cr)
                    if cr_range is not None:
                        cr_min, cr_max = cr_range
                        if cr_min <= monster_cr <= cr_max:
                            monster["cr"] = monster_cr
                            results.append(monster)
                except (ValueError, TypeError):
                    pass
    
    return results

def main():
    parser = argparse.ArgumentParser(description='List and search D&D monsters (instant CR filtering)')
    parser.add_argument('--cr', help='Filter by CR (e.g., "5" or "1-5")')
    parser.add_argument('--search', help='Search by name')
    parser.add_argument('--limit', type=int, default=50, help='Max results (default: 50)')
    
    args = parser.parse_args()
    
    # Fetch all monsters
    data = fetch("/monsters")
    
    if "error" in data:
        error_output(f"Failed to fetch monsters: {data.get('message', 'Unknown error')}")
    
    monsters = data.get("results", [])
    
    # Apply filters
    if args.cr or args.search:
        monsters = filter_monsters_instant(monsters, args)
    
    # Apply limit
    if args.limit and len(monsters) > args.limit:
        monsters = monsters[:args.limit]
    
    # Format output
    output({
        "count": len(monsters),
        "total": data.get("count", 0),
        "results": monsters
    })

if __name__ == "__main__":
    main()