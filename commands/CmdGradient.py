from evennia import Command
from evennia.utils import ansi
import re

class CmdGradientName(Command):
    """
    Apply a gradient color to your name

    Usage:
      gradientname <start_color> <end_color>

    This command applies a gradient color effect to your name,
    transitioning from the start color to the end color.
    You can use named colors or hex color codes (#RRGGBB).

    Examples:
      gradientname crimson gold
      gradientname #FF0000 #0000FF
      gradientname red #00FF00
    """

    key = "gradientname"
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    # Color map (unchanged from previous version)
    COLOR_MAP = {
        "black": (0, 0, 0),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "yellow": (255, 255, 0),
        "blue": (0, 0, 255),
        "magenta": (255, 0, 255),
        "cyan": (0, 255, 255),
        "white": (255, 255, 255),
        "gray": (128, 128, 128),
        "maroon": (128, 0, 0),
        "olive": (128, 128, 0),
        "navy": (0, 0, 128),
        "purple": (128, 0, 128),
        "teal": (0, 128, 128),
        "silver": (192, 192, 192),
        "lime": (0, 255, 0),
        "aqua": (0, 255, 255),
        "fuchsia": (255, 0, 255),
        "orange": (255, 165, 0),
        "pink": (255, 192, 203),
        "gold": (255, 215, 0),
        "crimson": (220, 20, 60),
        "violet": (238, 130, 238),
        "indigo": (75, 0, 130),
        "turquoise": (64, 224, 208),
        "coral": (255, 127, 80),
        "salmon": (250, 128, 114),
        "skyblue": (135, 206, 235),
        "khaki": (240, 230, 140),
        "plum": (221, 160, 221),
    }

    def func(self):
        if not self.args:
            self.caller.msg("Usage: gradientname <start_color> <end_color>")
            return

        try:
            start_color, end_color = self.args.split()[:2]
        except ValueError:
            self.caller.msg("Please provide both start and end colors.")
            return

        start_rgb = self.parse_color(start_color)
        end_rgb = self.parse_color(end_color)

        if start_rgb is None or end_rgb is None:
            self.caller.msg("Invalid color(s). Use named colors or hex codes (#RRGGBB).")
            return

        name = self.caller.key
        gradient_name = self.create_gradient(name, start_rgb, end_rgb)
        
        self.caller.db.gradient_name = gradient_name
        self.caller.msg(f"Your name now appears as: {gradient_name}")

    def parse_color(self, color):
        if color.startswith('#'):
            # Parse hex color code
            match = re.match(r'^#([0-9A-Fa-f]{6})$', color)
            if match:
                hex_color = match.group(1)
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        elif color in self.COLOR_MAP:
            # Use named color
            return self.COLOR_MAP[color]
        return None

    def create_gradient(self, text, start_rgb, end_rgb):
        gradient = []
        for i, char in enumerate(text):
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / (len(text) - 1))
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / (len(text) - 1))
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / (len(text) - 1))
            
            ansi_code = self.rgb_to_ansi(r, g, b)
            gradient.append(f"\033[38;5;{ansi_code}m{char}\033[0m")

        return "".join(gradient)

    def rgb_to_ansi(self, r, g, b):
        # Convert RGB to the closest ANSI 256 color code
        return 16 + (36 * (r // 51)) + (6 * (g // 51)) + (b // 51)

# Add this to your commands module or a new module