#!/usr/bin/env python3
"""
Color utilities for DM display output.
Strategic ANSI colors for HP, damage, dice, and key moments.

Usage:
    uv run python lib/colors.py hp_bar 18 24
    uv run python lib/colors.py damage 5
    uv run python lib/colors.py heal 3
    uv run python lib/colors.py dice 17 5 22 hit
"""

# ANSI Color Codes
class Colors:
    # Reset
    RESET = "\033[0m"

    # Standard colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"

    # Bold variants
    BOLD = "\033[1m"
    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_CYAN = "\033[1;36m"

    # Dim for secondary info
    DIM = "\033[2m"


def hp_color(current: int, max_hp: int) -> str:
    """Return the appropriate color code based on HP percentage."""
    if max_hp <= 0:
        return Colors.RED

    percent = current / max_hp

    if percent > 0.5:
        return Colors.GREEN
    elif percent > 0.25:
        return Colors.YELLOW
    else:
        return Colors.RED


def hp_bar(current: int, max_hp: int, width: int = 12) -> str:
    """
    Generate a colored HP bar.

    Returns: ████████░░░░ 18/24

    Colors:
    - Green (>50% HP)
    - Yellow (25-50% HP)
    - Red (<25% HP)
    """
    if max_hp <= 0:
        return f"{Colors.RED}░░░░░░░░░░░░ 0/0{Colors.RESET}"

    # Clamp current HP
    current = max(0, min(current, max_hp))

    # Calculate filled blocks
    percent = current / max_hp
    filled = round(percent * width)
    empty = width - filled

    # Get color based on HP state
    color = hp_color(current, max_hp)

    # Build bar
    bar = "█" * filled + "░" * empty

    return f"{color}{bar} {current}/{max_hp}{Colors.RESET}"


def damage(amount: int) -> str:
    """Format damage in red bold."""
    return f"{Colors.BOLD_RED}-{amount} HP{Colors.RESET}"


def heal(amount: int) -> str:
    """Format healing in green bold."""
    return f"{Colors.BOLD_GREEN}+{amount} HP{Colors.RESET}"


def dice_result(roll: int, modifier: int = 0, total: int = None,
                success: str = None, target: int = None) -> str:
    """
    Format a dice result with colors.

    Args:
        roll: The raw die result
        modifier: Any modifier applied
        total: The final total (calculated if not provided)
        success: "hit", "miss", "success", "failure", "crit", "fumble"
        target: The DC or AC to beat (for display)

    Returns:
        Colored dice result string
    """
    if total is None:
        total = roll + modifier

    # Build the roll display
    if modifier != 0:
        mod_str = f"{modifier:+d}"
        roll_display = f"{Colors.CYAN}{roll} {mod_str} = {total}{Colors.RESET}"
    else:
        roll_display = f"{Colors.CYAN}{roll}{Colors.RESET}"

    # Add target comparison if provided
    if target is not None:
        roll_display += f" vs {target}"

    # Add success/failure indicator
    if success:
        success_lower = success.lower()
        if success_lower in ("hit", "success"):
            indicator = f"{Colors.BOLD_GREEN}HIT!{Colors.RESET}" if success_lower == "hit" else f"{Colors.BOLD_GREEN}SUCCESS!{Colors.RESET}"
        elif success_lower in ("miss", "failure"):
            indicator = f"{Colors.BOLD_RED}MISS!{Colors.RESET}" if success_lower == "miss" else f"{Colors.BOLD_RED}FAILURE!{Colors.RESET}"
        elif success_lower == "crit":
            indicator = f"{Colors.BOLD_GREEN}CRITICAL HIT!{Colors.RESET}"
        elif success_lower == "fumble":
            indicator = f"{Colors.BOLD_RED}CRITICAL MISS!{Colors.RESET}"
        else:
            indicator = success

        roll_display += f" — {indicator}"

    return roll_display


def format_roll_result(notation: str, rolls: list, total: int,
                       is_crit: bool = False, is_fumble: bool = False) -> str:
    """
    Format a full dice roll result with colors (for use by dice.py).

    Args:
        notation: The dice notation (e.g., "1d20+5")
        rolls: List of individual die results
        total: Final total after modifiers
        is_crit: True if natural 20
        is_fumble: True if natural 1
    """
    rolls_str = '+'.join(str(r) for r in rolls)

    # Base roll in cyan
    base = f"🎲 {notation}: {Colors.CYAN}[{rolls_str}]{Colors.RESET}"

    # Add total
    base += f" = {Colors.CYAN}{total}{Colors.RESET}"

    # Add crit/fumble indicators
    if is_crit:
        base += f" ⚔️ {Colors.BOLD_GREEN}CRITICAL HIT!{Colors.RESET}"
    elif is_fumble:
        base += f" 💀 {Colors.BOLD_RED}CRITICAL MISS!{Colors.RESET}"

    return base


def success(text: str = "SUCCESS") -> str:
    """Format success text in green bold."""
    return f"{Colors.BOLD_GREEN}{text}{Colors.RESET}"


def failure(text: str = "FAILURE") -> str:
    """Format failure text in red bold."""
    return f"{Colors.BOLD_RED}{text}{Colors.RESET}"


def main():
    """CLI interface for color utilities."""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  colors.py hp_bar <current> <max>     - Show HP bar")
        print("  colors.py damage <amount>            - Show damage")
        print("  colors.py heal <amount>              - Show healing")
        print("  colors.py dice <roll> <mod> <total> [result]  - Show dice result")
        print("")
        print("Examples:")
        print("  colors.py hp_bar 18 24")
        print("  colors.py damage 5")
        print("  colors.py heal 3")
        print("  colors.py dice 17 5 22 hit")
        sys.exit(0)

    command = sys.argv[1]

    if command == "hp_bar":
        if len(sys.argv) < 4:
            print("Usage: colors.py hp_bar <current> <max>")
            sys.exit(1)
        current = int(sys.argv[2])
        max_hp = int(sys.argv[3])
        print(hp_bar(current, max_hp))

    elif command == "damage":
        if len(sys.argv) < 3:
            print("Usage: colors.py damage <amount>")
            sys.exit(1)
        amount = int(sys.argv[2])
        print(damage(amount))

    elif command == "heal":
        if len(sys.argv) < 3:
            print("Usage: colors.py heal <amount>")
            sys.exit(1)
        amount = int(sys.argv[2])
        print(heal(amount))

    elif command == "dice":
        if len(sys.argv) < 5:
            print("Usage: colors.py dice <roll> <mod> <total> [result]")
            sys.exit(1)
        roll_val = int(sys.argv[2])
        mod = int(sys.argv[3])
        total_val = int(sys.argv[4])
        result = sys.argv[5] if len(sys.argv) > 5 else None
        print(dice_result(roll_val, mod, total_val, result))

    elif command == "demo":
        # Demo all color outputs
        print("\n=== HP Bars ===")
        print(f"Healthy (75%):  {hp_bar(18, 24)}")
        print(f"Wounded (45%):  {hp_bar(11, 24)}")
        print(f"Critical (20%): {hp_bar(5, 24)}")

        print("\n=== Combat ===")
        print(f"Damage taken: {damage(5)}")
        print(f"Healing: {heal(8)}")

        print("\n=== Dice Results ===")
        print(f"Attack roll: {dice_result(17, 5, 22, 'hit', 15)}")
        print(f"Save roll: {dice_result(8, 2, 10, 'failure', 14)}")
        print(f"Critical: {dice_result(20, 5, 25, 'crit')}")
        print(f"Fumble: {dice_result(1, 5, 6, 'fumble')}")

        print("\n=== Status ===")
        print(f"Check result: {success('SUCCESS!')}")
        print(f"Check result: {failure('FAILURE!')}")
        print()

    else:
        print(f"Unknown command: {command}")
        print("Use 'colors.py' with no args for help")
        sys.exit(1)


if __name__ == "__main__":
    main()
