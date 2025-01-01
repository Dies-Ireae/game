from commands.communication import AdminCommand
from evennia.utils import logger
from evennia.commands.default.general import CmdLook


class CmdApprove(AdminCommand):
    """
    Approve a player's character.

    Usage:
      approve <character_name>

    This command approves a player's character, removing the 'unapproved' tag
    and adding the 'approved' tag. This allows the player to start playing.
    """
    key = "approve"
    aliases = ["+approve"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: approve <character_name>")
            return

        # Use global search for admin commands
        target = self.caller.search(self.args, global_search=True)
        if not target:
            return

        # Check both tag and attribute for approval status
        is_approved = target.tags.has("approved", category="approval") and target.db.approved
        if is_approved:
            self.caller.msg(f"{target.name} is already approved.")
            return

        # Set both the tag and the attribute
        target.db.approved = True
        target.tags.remove("unapproved", category="approval")
        target.tags.add("approved", category="approval")
        
        logger.log_info(f"{target.name} has been approved by {self.caller.name}")

        self.caller.msg(f"You have approved {target.name}.")
        target.msg("Your character has been approved. You may now begin playing.")

class CmdUnapprove(AdminCommand):
    """
    Set a character's status to unapproved.

    Usage:
      unapprove <character_name>

    This command removes the 'approved' tag from a character and adds the 'unapproved' tag.
    This effectively reverts the character to an unapproved state, allowing them to use
    chargen commands again.
    """
    key = "unapprove"
    aliases = ["+unapprove"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: unapprove <character_name>")
            return

        # Use global search for admin commands
        target = self.caller.search(self.args, global_search=True)
        if not target:
            return

        # Check both tag and attribute for approval status
        is_approved = target.tags.has("approved", category="approval") or target.db.approved
        if not is_approved:
            self.caller.msg(f"{target.name} is already unapproved.")
            return

        # Remove approved status and add unapproved tag
        target.db.approved = False
        target.tags.remove("approved", category="approval")
        target.tags.add("unapproved", category="approval")
        
        logger.log_info(f"{target.name} has been unapproved by {self.caller.name}")

        self.caller.msg(f"You have unapproved {target.name}.")
        target.msg("Your character has been unapproved. You may now use chargen commands again.")

class CmdMassUnapprove(AdminCommand):
    """
    Set all connected characters to unapproved status.

    Usage:
      +massunapprove
      +massunapprove/confirm

    This command will list all characters that will be affected when run
    without the /confirm switch. Use /confirm to actually make the changes.
    """

    key = "+massunapprove"
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        """Execute command."""
        caller = self.caller
        confirm = "confirm" in self.switches

        # Get all connected characters
        from evennia.server.sessionhandler import SESSIONS
        connected_chars = [session.get_puppet() for session in SESSIONS.get_sessions() 
                         if session.get_puppet()]
        
        if not connected_chars:
            caller.msg("No connected characters found.")
            return

        if not confirm:
            # Just show what would be affected
            msg = "The following characters would be set to unapproved:\n"
            for char in connected_chars:
                msg += f"- {char.name} (currently {'approved' if char.db.approved else 'unapproved'})\n"
            msg += "\nUse +massunapprove/confirm to execute the changes."
            caller.msg(msg)
            return

        # Actually make the changes
        count = 0
        for char in connected_chars:
            if char.db.approved:
                char.db.approved = False
                char.tags.add("unapproved", category="approval")
                if char.tags.has("approved", category="approval"):
                    char.tags.remove("approved", category="approval")
                char.msg("Your character has been set to unapproved status.")
                count += 1
                logger.log_info(f"{char.name} has been mass-unapproved by {caller.name}")

        caller.msg(f"Successfully set {count} character(s) to unapproved status.")

class CmdAdminLook(CmdLook, AdminCommand):
    """
    look at location or object

    Usage:
      look
      look <obj>
      look *<character>  (Admin only - global search)
      look [in|at|inside] <obj>

    Observes your location, an object, or a character globally with '*'.
    The 'in' preposition lets you look inside containers.
    """

    key = "look"
    aliases = ["l", "ls"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Handle the looking."""
        caller = self.caller
        args = self.args.strip()
        
        # Handle global search for admin using *character format
        if args.startswith('*') and caller.check_permstring("Admin"):
            # Remove the * and any leading/trailing spaces
            target_name = args[1:].strip()
            # Perform global search
            target = caller.search(target_name, global_search=True)
            if not target:
                return
            # Show the target's description
            self.msg(target.return_appearance(caller))
            return
            
        # If not using * prefix, use the default look behavior
        super().func()