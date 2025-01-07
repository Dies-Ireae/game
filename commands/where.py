from evennia import default_cmds
from evennia.server.sessionhandler import SESSIONS
from evennia.utils.ansi import ANSIString
from world.wod20th.utils.formatting import header, footer, divider
from evennia.utils.evtable import EvTable
from collections import defaultdict
import time

class CmdWhere(default_cmds.MuxCommand):
    """
    Displays a list of online players and their locations.

    Usage:
        +where

    Shows all online players organized by location area, with idle times.
    Unfindable characters and those in unfindable rooms are hidden from non-staff.
    """

    key = "+where"
    aliases = ["where"]
    locks = "cmd:all()"
    help_category = "General"

    def format_idle_time(self, idle_seconds):
        """Format idle time into a compact string."""
        if not idle_seconds:
            return "0s"
        if idle_seconds < 60:
            return f"{int(idle_seconds)}s"
        elif idle_seconds < 3600:
            return f"{int(idle_seconds/60)}m"
        elif idle_seconds < 86400:
            return f"{int(idle_seconds/3600)}h"
        elif idle_seconds < 604800:
            return f"{int(idle_seconds/86400)}d"
        else:
            return f"{int(idle_seconds/604800)}w"

    def get_idle_time(self, session):
        """Get idle time in seconds."""
        if not session:
            return 0
        return time.time() - session.cmd_last_visible

    def get_area_name(self, location):
        """Extract area name from location."""
        if not location:
            return "Unknown"
            
        # First try to get the area from the room's attributes
        area = location.db.area
        if area:
            return area
            
        # If no area is set, try to get it from the room's zone
        if hasattr(location, 'zone') and location.zone:
            return location.zone
            
        # If it's Limbo, return Limbo
        if location.key == "Limbo":
            return "Limbo"
            
        # If no area/zone is set, use the room's key or name
        if hasattr(location, 'key'):
            return location.key.split(' - ')[0]  # Take first part before any dash
            
        # Last resort
        return "Unknown"

    def func(self):
        """Implement the command"""
        caller = self.caller
        session_list = SESSIONS.get_sessions()
        is_staff = caller.check_permstring("builders")
        
        # Group characters by area
        areas = defaultdict(list)
        unfindable_chars = []  # New list for unfindable characters
        
        # Build the output
        string = header("Player Locations", width=78) + "\n"
        string += "|wPlayer                 Type   Idle  Location|n\n"
        string += "|r" + "-" * 78 + "|n\n"

        # Sort sessions by account name
        session_list = sorted(session_list, key=lambda o: o.account.key if o.account else "")

        # Collect character information
        for session in session_list:
            if not session.logged_in:
                continue
            
            puppet = session.get_puppet()
            if not puppet:
                continue

            # Handle unfindable characters for everyone
            if puppet.db.unfindable:
                # Add LFRP coloring and staff indicator for unfindable chars
                name = puppet.name
                if puppet.db.lfrp:
                    name = f"|y{name}|n"
                name_suffix = "*" if puppet.check_permstring("builders") else ""
                
                unfindable_chars.append((
                    f"{name}{name_suffix}",
                    puppet.db.char_type if puppet.db.char_type else "",
                    self.format_idle_time(self.get_idle_time(session)),
                    puppet.location.get_display_name(caller) if is_staff else "Unknown"
                ))
                continue

            location = puppet.location
            if not location or (location.db.unfindable and not is_staff):
                continue

            area = self.get_area_name(location)
            char_type = puppet.db.char_type if puppet.db.char_type else ""
            idle_time = self.format_idle_time(self.get_idle_time(session))
            
            # Add LFRP coloring
            name = puppet.name
            if puppet.db.lfrp:
                name = f"|y{name}|n"
            
            # Add AFK and staff indicators
            name_prefix = "^" if puppet.db.afk else " "
            name_suffix = "*" if puppet.check_permstring("builders") else ""
            
            # Add character to appropriate area
            areas[area].append((
                f"{name_prefix}{name}{name_suffix}",
                char_type,
                idle_time,
                location.get_display_name(caller)
            ))

        # characters by area
        for area in sorted(areas.keys()):
            if areas[area]:  # Only show areas with characters in them
                string += "\n"  # Empty line for spacing
                string += f"|c---< {area} >{'-' * (70 - len(area))}|n\n"
                for name, char_type, idle, loc in sorted(areas[area]):
                    string += f"{name:<20} {char_type:<6} {idle:<5} {loc}\n"

        # unfindable characters section
        if unfindable_chars:
            string += f"\n|c---< Unfindable Characters >{'-' * (70 - len('Unfindable Characters'))}|n\n"
            for name, char_type, idle, loc in sorted(unfindable_chars):
                if is_staff:
                    string += f" {name:<20} {char_type:<6} {idle:<5} {loc}\n"
                else:
                    string += f" {name:<20} {char_type:<6} {idle:<5} Unknown\n"

        # legend
        string += "\n|r" + "-" * 78 + "|n"  # Add a separator line
        string += "\n|yLegend: ^ = AFK, * = Staff, |yYellow|n = Looking for RP|n"
        string += "\n|r" + "-" * 78 + "|n\n"  # Add another separator line

        string += footer(width=78)
        caller.msg(string)
