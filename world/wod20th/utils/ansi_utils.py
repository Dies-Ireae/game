# utils/ansi_utils.py
import textwrap
from evennia.utils.ansi import strip_raw_ansi, ANSIString

def wrap_ansi(text, width):
    """
    Wraps a string to the specified width, preserving ANSI codes.

    Args:
        text (str): The text to wrap.
        width (int): The width to wrap the text to.

    Returns:
        str: The wrapped text.
    """
    text = ANSIString(text)
    raw_text = strip_raw_ansi(text)
    wrapped_lines = textwrap.wrap(raw_text, width=width)

    current_index = 0
    wrapped_text = ""
    for line in wrapped_lines:
        visible_length = len(line)
        ansi_part = text[current_index:current_index + visible_length]
        current_index += visible_length
        wrapped_text += str(ansi_part) + "\n"

    return wrapped_text.strip()
