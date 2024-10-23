from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils import utils

class CmdLook(MuxCommand):
    """
    look at location or object

    Usage:
      look
      look <obj>
      look *<account>

    Observes your location or objects in your vicinity.
    """
    key = "look"
    aliases = ["l", "ls"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        args = self.args.strip()
        location = caller.location

        if not args:
            # If no arguments, look at the location
            if location:
                caller.msg(location.return_appearance(caller))
            else:
                caller.msg("You have no location to look at!")
            return

        # Look for a particular object
        look_at_obj = caller.search(args, location=location, use_nicks=True, quiet=True)

        if not look_at_obj:
            # If the object is not found, check if it's a character in a different state
            possible_chars = [obj for obj in location.contents 
                              if obj.has_account and obj.key.lower() == args.lower()]
            
            if possible_chars and possible_chars[0].db.in_umbra != caller.db.in_umbra:
                caller.msg(f"Could not find '{args}'.")
            else:
                caller.msg(f"You don't see '{args}' here.")
            return

        # If it's a list, return the first object only
        if utils.inherits_from(look_at_obj, list):
            look_at_obj = look_at_obj[0]

        # Check if the found object is in the same Umbra state
        if hasattr(look_at_obj, 'has_account') and look_at_obj.has_account:
            if look_at_obj.db.in_umbra != caller.db.in_umbra:
                caller.msg(f"Could not find '{args}'.")
                return

        # Show the object's appearance
        caller.msg(look_at_obj.return_appearance(caller))