from random import randint
from typing import List, Tuple

def roll_dice(dice_pool: int, difficulty: int) -> Tuple[List[int], int, int]:
    """
    Roll dice for World of Darkness 20th Anniversary Edition.

    Args:
    dice_pool (int): The number of dice to roll.
    difficulty (int): The difficulty of the roll.

    Returns:
    Tuple[List[int], int, int]: A tuple containing:
        - List of individual die results
        - Number of successes
        - Number of ones (potential botches)
    """
    rolls = [randint(1, 10) for _ in range(max(0, dice_pool))]
    successes = sum(1 for roll in rolls if roll >= difficulty)
    ones = sum(1 for roll in rolls if roll == 1)
    successes = successes - ones
    
    return rolls, successes, ones

def interpret_roll_results(successes, ones, rolls=None, diff=6):
    """Interpret the results of a dice roll."""
    # Format success count with color
    if successes == 0:
        success_string = f"|y{successes}|n"
    elif successes > 0:
        success_string = f"|g{successes}|n"
    else:
        success_string = f"|r{successes}|n"

    msg = f"|w(|n{success_string}|w)|n"
    
    # Add Success/Successes text
    if successes == -1 and ones > 0:
        msg += f"|r Botch!|n"
    else:
        msg += "|y Successes|n" if successes != 1 else "|y Success|n"
    
    # Format dice results with color
    if rolls:
        msg += " |w(|n"
        colored_rolls = []
        for roll in sorted(rolls, reverse=True):
            if roll == 1:
                colored_rolls.append(f"|r{roll}|n")
            elif roll >= diff:
                colored_rolls.append(f"|g{roll}|n")
            else:
                colored_rolls.append(f"|y{roll}|n")
        msg += " ".join(colored_rolls)
        msg += "|w)|n"
    
    return msg