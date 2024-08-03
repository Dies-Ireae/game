from evennia import Command as MuxCommand


class CmdShortDesc(MuxCommand):
    """
    shortdesc <text>

    Usage:
      shortdesc <text>

    create a short description for your character
    """
    key = "shortdesc"
    help_category = "General"

    def func(self):
        "Implement the command"
        caller = self.caller
        if not self.args:
            # remove the shortdesc
            caller.db.shortdesc = ""
            caller.msg("Short description removed.")
            return
        
        caller.db.shortdesc = self.args.strip()
        caller.msg("Short description set to '|w%s|n'." % self.args.strip())