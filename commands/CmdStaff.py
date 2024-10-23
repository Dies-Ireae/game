from evennia import default_cmds
from evennia.accounts.accounts import AccountDB
from evennia.utils.ansi import ANSIString
from evennia.utils import ansi

class CmdStaff(default_cmds.MuxCommand):
    """
    List and manage staff members.

    Usage:
      +staff
      +staff/position <account> = <position>
      +staff/add <account>
      +staff/remove <account>

    Switches:
      /position - Set the position of a staff member
      /add      - Add an account to the storyteller role
      /remove   - Remove an account from the storyteller role

    Examples:
      +staff
      +staff/position Wizard = Head Admin
      +staff/add NewStoryteller
      +staff/remove FormerStoryteller
    """

    key = "+staff"
    aliases = ["staff"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if not self.args and not self.switches:
            # Display staff list
            self.list_staff()
        elif "position" in self.switches:
            # Set staff position (admin only)
            if self.caller.check_permstring("Admin"):
                self.set_position()
            else:
                self.caller.msg("You don't have permission to set staff positions.")
        elif "add" in self.switches:
            # Add storyteller (admin only)
            if self.caller.check_permstring("Admin"):
                self.add_storyteller()
            else:
                self.caller.msg("You don't have permission to add storytellers.")
        elif "remove" in self.switches:
            # Remove storyteller (admin only)
            if self.caller.check_permstring("Admin"):
                self.remove_storyteller()
            else:
                self.caller.msg("You don't have permission to remove storytellers.")
        else:
            self.caller.msg("Invalid switch. See help +staff for usage.")

    def list_staff(self):
        all_accounts = AccountDB.objects.all()
        staff = []
        player_storytellers = []

        for account in all_accounts:
            is_superuser = account.is_superuser
            is_developer = account.check_permstring("developer")
            is_admin = account.check_permstring("admin")
            is_storyteller = account.tags.get("storyteller", category="role") is not None
            
            character = account.db._playable_characters[0] if account.db._playable_characters else None
            if character:
                char_is_storyteller = character.tags.get("storyteller", category="role") is not None
                char_is_developer = character.check_permstring("developer")
                char_is_admin = character.check_permstring("admin")
            else:
                char_is_storyteller = char_is_developer = char_is_admin = False
            
            if is_superuser or is_developer or is_admin or char_is_developer or char_is_admin:
                staff.append((account, character))
            elif is_storyteller or char_is_storyteller:
                player_storytellers.append((account, character))

        if not staff and not player_storytellers:
            self.caller.msg("No staff members or storytellers found.")
            return

        string = self.format_header("Dies Irae Staff", width=78)
        string += self.format_columns(["Name", "Position", "Status"], color="|w")
        string += "|r=|n" * 78 + "\n"

        for account, character in staff:
            if character and character.attributes.has("gradient_name"):
                raw_name = character.attributes.get("gradient_name")
                name = ANSIString((raw_name))
            else:
                name = account.key.strip()

            position = self.get_position(account, character)
            status = "|gOnline|n" if account.is_connected else "|rOffline|n"

            string += self.format_staff_row(name, position, status)

        if staff and player_storytellers:
            string += "|r=|n" * 78 + "\n"

        for account, character in player_storytellers:
            name = account.key.strip()
            # Check for custom position
            account_position = account.db.position
            character_position = character.db.position if character else None
            custom_position = account_position or character_position

            if custom_position:
                position = custom_position
            else:
                position = "Storyteller"
            status = "|gOnline|n" if account.is_connected else "|rOffline|n"

            string += self.format_staff_row(name, position, status)

        string += self.format_footer(width=78)

        self.caller.msg(string)

    def format_header(self, text, width=78):
        return f"|r{'=' * 5}< |w{text}|r >{'=' * (width - len(text) - 9)}|n\n"

    def format_footer(self, width=78):
        return f"|r{'=' * width}|n\n"

    def format_columns(self, columns, color="|w"):
        return "".join([f"{color}{col:<25}|n" for col in columns]) + "\n"

    def format_staff_row(self, name, position, status):
        name_col = ANSIString(name).ljust(25)
        position_col = ANSIString(position).ljust(25)
        status_col = ANSIString(status)
        return f"{name_col}{position_col}{status_col}\n"

    def get_position(self, account, character):
        # First, check for custom position on the character
        if character and character.db.position:
            return character.db.position
        
        # Then, check for custom position on the account
        if account.db.position:
            return account.db.position
        
        # If no custom position, fall back to permission-based positions
        if account.is_superuser:
            return "Superuser"
        elif account.check_permstring("developer") or (character and character.check_permstring("developer")):
            return "Developer"
        elif account.check_permstring("admin") or (character and character.check_permstring("admin")):
            return "Admin"
        elif account.tags.get("storyteller", category="role") or (character and character.tags.get("storyteller", category="role")):
            return "Storyteller"
        else:
            return "Staff"

    def set_position(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: +staff/position <account> = <position>")
            return
        
        account_name, position = self.args.split("=", 1)
        account_name = account_name.strip()
        position = position.strip()

        account = self.caller.search(account_name, global_search=True)
        if not account:
            return

        account.db.position = position
        self.caller.msg(f"Set {account.key}'s position to: {position}")
        self.list_staff()  # Show updated staff list

    def add_storyteller(self):
        if not self.args:
            self.caller.msg("Usage: +staff/add <account>")
            return

        account = self.caller.search(self.args, global_search=True)
        if not account:
            return

        if account.tags.get("storyteller", category="role"):
            self.caller.msg(f"{account.key} is already a storyteller.")
        else:
            account.tags.add("storyteller", category="role")
            self.caller.msg(f"Added {account.key} as a storyteller.")
            self.list_staff()  # Only show updated staff list if a change was made

        # Debug information
        self.caller.msg(f"Debug: Account tags for {account.key}: {account.tags.all()}")
        self.caller.msg(f"Debug: Is storyteller? {account.tags.get('storyteller', category='role')}")
        self.caller.msg(f"Debug: All staff-related permissions: {account.permissions.all()}")

    def remove_storyteller(self):
        if not self.args:
            self.caller.msg("Usage: +staff/remove <account>")
            return

        account = self.caller.search(self.args, global_search=True)
        if not account:
            return

        if not account.tags.get("storyteller", category="role"):
            self.caller.msg(f"{account.key} is not a storyteller.")
        else:
            account.tags.remove("storyteller", category="role")
            self.caller.msg(f"Removed {account.key} from storyteller role.")
        
        self.list_staff()  # Show updated staff list

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
