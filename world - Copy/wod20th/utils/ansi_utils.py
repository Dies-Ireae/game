import textwrap
from evennia.utils.ansi import strip_raw_ansi, ANSIString

def wrap_ansi(text, width, left_padding=0, right_padding=0):
    """
    Wraps a string to the specified width, preserving ANSI codes, with optional left and right padding.

    Args:
        text (str): The text to wrap.
        width (int): The width to wrap the text to, including padding.
        left_padding (int): The amount of padding to add to the left side.
        right_padding (int): The amount of padding to add to the right side.

    Returns:
        str: The wrapped text with padding.
    """
    if left_padding + right_padding >= width:
        raise ValueError("Combined padding is too large for the given width.")

    # Convert to ANSIString to handle color codes
    ansi_text = ANSIString(text)
    
    # Get clean text for wrapping calculations
    clean_text = ansi_text.clean()
    
    # Calculate actual display width
    wrap_width = width - left_padding - right_padding

    # Split into words while preserving color codes
    words = []
    current_word = ""
    current_codes = ""
    
    for i, char in enumerate(str(ansi_text)):
        if char == '|' and i + 1 < len(str(ansi_text)):
            current_codes += char + str(ansi_text)[i + 1]
            continue
        elif char == ' ':
            if current_word:
                words.append(current_codes + current_word)
                current_word = ""
                current_codes = ""
            else:
                words.append(' ')
        else:
            current_word += char
    
    if current_word:
        words.append(current_codes + current_word)

    # Build wrapped lines
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_clean = ANSIString(word).clean()
        word_length = len(word_clean)
        
        if current_length + word_length <= wrap_width:
            current_line.append(word)
            current_length += word_length + (1 if current_length > 0 else 0)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = word_length

    if current_line:
        lines.append(" ".join(current_line))

    # Add padding
    padded_lines = [
        " " * left_padding + line + " " * right_padding
        for line in lines
    ]

    return "\n".join(padded_lines)
