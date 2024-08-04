# typeclasses/rooms.py
from evennia import DefaultRoom
from evennia.utils.ansi import ANSIString
from world.wod20th.utils.ansi_utils import wrap_ansi

class RoomParent(DefaultRoom):

    def return_appearance(self, looker, **kwargs):
        if not looker:
            return ""

        name = self.get_display_name(looker, **kwargs)
        desc = self.db.desc

        # Header with room name
        # if the looker is a builder, show the dbref
        if looker.check_permstring("builders"):
            string = ANSIString.center(ANSIString(f"|y {name}({self.dbref})|n "), width=78, fillchar=ANSIString("|b=|n")) + "\n"
        else:
            string = ANSIString.center(ANSIString(f"|y {name} |n"), width=78, fillchar=ANSIString("|b=|n")) + "\n"
        
        # Optional: add custom room description here if available
        if desc:
            string += wrap_ansi(desc, 78) + "\n"

        # List all characters in the room
        characters = [obj for obj in self.contents if obj.has_account]
        if characters:
            string += ANSIString.center(ANSIString("|y Characters |n"), width=78, fillchar=ANSIString("|b=|n")) + "\n"
            for character in characters:
                idle_time = self.idle_time_display(character.idle_time)
                # if the looker is the character itself the idle time is 0s.
                if character == looker:
                    idle_time = self.idle_time_display(0)


                # Check for short description
                shortdesc = character.db.shortdesc
                if shortdesc:
                    shortdesc_str = f"{shortdesc}"
                else:
                    shortdesc_str = ANSIString("|h|xType '|n+shortdesc <desc>|h|x' to set a short description.|n")

                # Calculate the total length and truncate if necessary and end with elipses.
                # only replace the last three characters if the string is longer than 50 characters
                if len(shortdesc_str) > 52:
                    shortdesc_str = shortdesc_str[:52]
                    shortdesc_str = shortdesc_str[:-3] + "..."
                else:
                    shortdesc_str = shortdesc_str.ljust(52, ' ')
                
                string += f" {character.get_display_name(looker).ljust(20)} {idle_time.rjust(5)} |n{shortdesc_str}\n"

        # List all exits
        exits = [ex for ex in self.contents if ex.destination]
        if exits:
            string += "\n|wExits|n\n"
            for exit in exits:
                string += f"  {exit.get_display_name(looker)} - leads to {exit.destination.get_display_name(looker)}\n"

        # List all objects in the room
        objects = [obj for obj in self.contents if not obj.has_account and not obj.destination]
        if objects:
            string += "\n|wObjects|n\n"
            for obj in objects:
                string += f"  {obj.get_display_name(looker)}\n"

        string += ANSIString("|b" + "="*78 + "|n")

        return string

    def idle_time_display(self, idle_time):
        """
        Formats the idle time display.
        """
        idle_time = int(idle_time)  # Convert to int
        if idle_time < 60:
            time_str = f"{idle_time}s"
        elif idle_time < 3600:
            time_str = f"{idle_time // 60}m"
        else:
            time_str = f"{idle_time // 3600}h"

        # Color code based on idle time intervals
        if idle_time < 900:  # less than 15 minutes
            color = "|g"  # green
        elif idle_time < 1800:  # 15-30 minutes
            color = "|y"  # yellow
        elif idle_time < 2700:  # 30-45 minutes
            color = "|o"  # orange
        elif idle_time < 3600:
            color = "|r"  # red
        else:
            color = "|h|x"
        

        return f"{color}{time_str}|n"
