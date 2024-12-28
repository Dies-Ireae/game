from evennia.utils.ansi import ANSIString
import time

def format_stat(stat, value, width=25, default=None, tempvalue=None, allow_zero=False):
    """Format a stat for display with proper spacing and temporary values."""
    if stat == "Appearance":
        print(f"Formatting Appearance: value={value}, tempvalue={tempvalue}, allow_zero={allow_zero}")
    
    if default is not None and (value is None or (not allow_zero and value == 0) or value == ""):
        value = default

    stat_str = f" {stat}"
    
    if stat == "Paradox":
        # For Paradox, only show the temporary value
        value_str = str(tempvalue)
    elif stat == "Arete":
        # For Arete, don't show temporary value
        value_str = str(value)
    elif tempvalue is not None and str(value).strip() != str(tempvalue).strip():
        if not allow_zero and tempvalue == 0:
            tempvalue = 1
        # For other stats, show both permanent and temporary values if they differ
        value_str = f"{value}({tempvalue})"
    else:
        value_str = str(value)

    # Truncate the stat name if it's too long
    max_stat_length = width - len(value_str) - 4  # 4 for the dots and spaces
    if len(stat_str) > max_stat_length:
        stat_str = stat_str[:max_stat_length-3] + "..." 

    dots = "." * (width - len(stat_str) - len(value_str) - 1)
    return f"{stat_str}{dots}{value_str}"

def header(title, width=78,  color="|y", fillchar=ANSIString("|b-|n"), bcolor="|b"):
    return ANSIString.center(ANSIString(f"{bcolor}<|n {color} {title} |n{bcolor}>|n"), width=width, fillchar=ANSIString(fillchar)) + "\n"

def footer(width=78, fillchar=ANSIString("|b-|n")):
    return ANSIString(fillchar) * width + "\n"

def divider(title, width=78, fillchar="-", color="|r", text_color="|n"):
    """
    Create a divider with a title.

    Args:
        title (str): The title to display in the divider.
        width (int): The total width of the divider.
        fillchar (str): The character to use for filling.
        color (str): The color code for the divider line.
        text_color (str): The color code for the title text.

    Returns:
        ANSIString: The formatted divider.
    """
    if isinstance(fillchar, ANSIString):
        fillchar = fillchar[0]
    else:
        fillchar = fillchar[0]

    colored_fillchar = f"{color}{fillchar}"
    
    if title:
        # Calculate the width of the title text without color codes
        title_width = len(ANSIString(title).clean())
        
        # Calculate padding on each side of the title
        padding = (width - title_width - 2) // 2  # -2 for spaces around the title
        
        # Create the divider with title
        left_part = colored_fillchar * padding
        right_part = colored_fillchar * (width - padding - title_width - 2)
        inner_content = f"{left_part} {text_color}{title}|n {right_part}"
    else:
        # If no title, just create a line of fillchars
        inner_content = colored_fillchar * width

    # Remove any trailing whitespace and add the color terminator
    return ANSIString(f"{inner_content.rstrip()}|n")

def format_idle_time(idle_seconds):
        """
        Formats the idle time into human-readable format.
        """
        if idle_seconds < 60:
            return f"{int(idle_seconds)}s"
        elif idle_seconds < 3600:
            return f"{int(idle_seconds / 60)}m"
        elif idle_seconds < 86400:
            return f"{int(idle_seconds / 3600)}h"
        elif idle_seconds < 604800:
            return f"{int(idle_seconds / 86400)}d"
        else:
            return f"{int(idle_seconds / 604800)}w"

def get_idle_time(character):
    """
    Get the idle time for a character.
    """
    if not character.sessions.count():
        return 0
    sessions = character.sessions.all()
    if sessions:
        return time.time() - max(session.cmd_last_visible for session in sessions)
    return 0

def english_list(items, none_str="None", join_str=" and ", comma_str=", "):
    if not items:
        return none_str  # Return an empty string for an empty list
    if len(items) == 1:
        return items[0]  # Return the single item
    if len(items) == 2:
        return join_str.join(items)  # Join with "and" for two items
    # Join all but the last item with commas, and append the last item with "and"
    return comma_str.join(items[:-1]) + comma_str.strip() + join_str + items[-1]