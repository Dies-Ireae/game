from evennia.commands.default.muxcommand import MuxCommand

class CmdFaeDesc(MuxCommand):
    """
    Set the fae description for yourself or the room.

    Usage:
      @faedesc me=<description>
      @faedesc here=<description>

    This command sets the fae description that Changelings and Kinain
    can see when using the +flook command.
    """

    key = "@faedesc"
    locks = "cmd:all()"
    help_category = "Building"

    def func(self):
        """Execute command."""
        caller = self.caller

        if not self.args or "=" not in self.args:
            caller.msg("Usage: @faedesc me=<description> or @faedesc here=<description>")
            return

        target, description = self.args.split("=", 1)
        target = target.strip().lower()
        description = description.strip()

        if target == "me":
            if hasattr(caller, 'set_fae_description'):
                caller.set_fae_description(description)
                caller.msg("You set your fae description.")
            else:
                caller.msg("You can't set a fae description for yourself.")
        elif target == "here":
            location = caller.location
            if not location:
                caller.msg("You are nowhere.")
                return
            if hasattr(location, 'set_fae_description'):
                location.set_fae_description(description)
                caller.msg("You set the fae description of the room.")
            else:
                caller.msg("You can't set a fae description for this location.")
        else:
            caller.msg("You can only set fae descriptions for 'me' or 'here'.")