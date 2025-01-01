from evennia import default_cmds
from evennia.server.sessionhandler import SESSIONS
from evennia.utils.ansi import ANSIString
from world.wod20th.utils.formatting import header, footer
import time

class CmdWhere(default_cmds.MuxCommand):
    """
    Displays a list of online players and their locations.

    Usage:
        +where

    Shows all online players, their idle time, current location, and Umbra status.
    Unfindable characters and those in unfindable rooms are listed separately.
    """

    key = "+where"
    aliases = ["where"]
    locks = "cmd:all()"
    help_category = "General"

    def format_idle_time(self, idle_seconds):
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

    def get_idle_time(self, character):
        """
        Get the idle time for a character.
        """
        if not character.sessions.count():
            return 0
        sessions = character.sessions.all()
        if sessions:
            return time.time() - max(session.cmd_last_visible for session in sessions)
        return 0

    def func(self):
        """
        Get all connected accounts/players.
        """
        caller = self.caller
        session_list = SESSIONS.get_sessions()
        session_list = sorted(session_list, key=lambda o: o.account.key if o.account else "")
        hide_sessions = False

        string = header("Characters", width=78)

        if session_list:
            table = []
            for session in session_list:
                if not session.logged_in:
                    continue
                puppet = session.get_puppet()
                if not puppet:
                    continue

                if puppet.db.unfindable and not caller.check_permstring("builders"):
                    continue

                # Get the short description, or a default message if none exists
                short_desc = puppet.db.short_desc or "Type '+shortdesc <desc>' to set a short description."

                # Get idle time
                idle = session.cmd_last_visible
                if idle:
                    idle_time = time.time() - idle
                    if idle_time >= 3600:
                        idle_fmt = "%.1fh" % (idle_time / 3600)
                    elif idle_time >= 60:
                        idle_fmt = "%.1fm" % (idle_time / 60)
                    else:
                        idle_fmt = "%ss" % idle_time
                else:

                    unfindable.append({
                        'name': character.get_display_name(self.caller),
                        'idle': idle_time,
                        'is_builder': account.check_permstring("Builder"),
                    })
            else:
                unfindable.append({
                    'name': account.get_display_name(self.caller),
                    'idle': "N/A",
                    'is_builder': account.check_permstring("Builder"),
                })

        players.sort(key=lambda x: x['location'].lower())
        unfindable.sort(key=lambda x: x['name'].lower())

        output = ""
        output += header("+where", width=78, bcolor="|r", fillchar="|r-|n")
        output += ANSIString(" |wPLAYER|n").ljust(30) + ANSIString("|wIDLE|n").rjust(5) + "    " + ANSIString("|wLOCATION|n\n")
        output += "|r-|n" * 78 + "\n"

        for p in players:
            name = p['name'].ljust(28)
            idle = p['idle'].rjust(5) + "   "
            location = p['location']
            output += f" {name} {idle} {location}\n"

        output += "|r-|n" * 78 + "\n"

        if unfindable:
            output += " Unfindable Characters:\n"
            line = ""
            count = 0
            for p in unfindable:
                name = p['name']
                idle = p['idle']
                entry = f"{name} {idle}".ljust(18)
                line += entry
                count += 1
                if count % 4 == 0:
                    output += line.rstrip() + "\n"
                    line = ""
            if line:
                output += line.rstrip() + "\n"

        total_players = len(players) + len(unfindable)
        if len(unfindable) > 0:
            output += "|r-|n" * 78 + "\n"

        output += f"                          There are |y{total_players}|n players online.\n"
        output += "|r=|n" * 78 + "\n"

        self.caller.msg(output)
        
                    idle_fmt = ""

                # Format each line with adjusted column widths
                # Name column reduced to 15 characters, idle time 4 characters
                name_part = puppet.name[:15].ljust(15)
                idle_part = idle_fmt.rjust(4)
                # Remaining space (minus spacing) goes to description
                desc_width = 78 - 15 - 4 - 3  # Total - name - idle - spacing
                short_desc = short_desc[:desc_width]

                table.append(f" {name_part} {idle_part} {short_desc}")

            string += "\n".join(table)
        else:
            string += " No characters found."

        string += footer(width=78)
        caller.msg(string)

