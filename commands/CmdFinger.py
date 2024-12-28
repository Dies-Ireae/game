from evennia.commands.default.muxcommand import MuxCommand
from world.wod20th.models import Stat, CATEGORIES, SHIFTER_IDENTITY_STATS, SHIFTER_RENOWN, CLAN, MAGE_FACTION, MAGE_SPHERES, \
    TRADITION, TRADITION_SUBFACTION, CONVENTION, METHODOLOGIES, NEPHANDI_FACTION, SEEMING, KITH, SEELIE_LEGACIES, \
    UNSEELIE_LEGACIES, ARTS, REALMS, calculate_willpower, calculate_road
from world.wod20th.utils.ansi_utils import wrap_ansi
from world.wod20th.utils.formatting import header, format_idle_time, get_idle_time, footer, divider, english_list

class CmdFinger(MuxCommand):
    """
    Settable details about a character and their player's roleplay preferences

    Possible settable fields:
      rumors         - Common knowledge about your character
      hangouts       - Where people can find your character
      rp preferences - Themes you like or want to avoid
      ic job         - Where your character works
      online times   - Days/times you can be found available for RP
      quotes         - Funtime quotes
      notes          - Other information not fitting to other fields about character

    Usage:
      +finger
      +finger/show <stat>/<category>
      +finger/hide <stat>/<category>
      +finger/set <field>=<value>
      +finger <character>

    Switches:
      /set      - Set a field on your finger profile
      /show     - Show a stat from your sheet
      /hide     - Hide a stat from your sheet

    Examples:
      +finger                       - View your own finger profile for your current character
      +finger/show appearance       - Display your appearance stat on your finger
    """
    key = "finger"
    aliases = []
    help_category = "Chargen & Character Info"
    long_fields = ["rumors", "hangouts", "rp preferences", "ic job", "online times", "quotes", "notes"]

    def func(self):
        character = self.caller.search(self.caller.key)
        if not self.args and not self.switches:
            self.show_finger(character)
        elif "show" in self.switches:
            matched_stat = Stat.objects.filter(name__iexact=self.args.strip())
            if not matched_stat.exists():
                return self.caller.msg(f"Unable to find a stat matching '{self.args.strip()}'.")
            character_stats = character.db.stats or {}
            if matched_stat[0].category not in character_stats or matched_stat[0].stat_type not in character_stats[matched_stat[0].category]:
                return self.caller.msg(f"Unable to find a stat matching '{self.args.strip()}' on your sheet.")
            self.add_shown_stat(character, matched_stat[0])
            self.caller.msg(f"Your +finger will now show the value of '{matched_stat[0].name}'.")
        elif "hide" in self.switches:
            matched_stat = Stat.objects.filter(name__iexact=self.args.strip())
            if not matched_stat.exists():
                return self.caller.msg(f"Unable to find a stat matching '{self.args.strip()}'.")
            if matched_stat[0].category not in character.db.dossier['shown_stats'] or matched_stat[0].name not in character.db.dossier['shown_stats'][matched_stat[0].category]:
                return self.caller.msg(f"You are not currently showing '{matched_stat[0].name}' on your +finger.")
            self.remove_shown_stat(character, matched_stat[0])
            self.caller.msg(f"Your +finger is no longer showing your '{matched_stat[0].name}'.")
        elif "set" in self.switches:
            try:
                key, value = self.split_key_value(self.args)
                if key not in self.long_fields:
                    return self.caller.msg(f"Unrecognized field '{key}', fields must be one of: {english_list(self.long_fields, 'none', ' or ')}.")
                if not value:
                    del character.db.dossier[key]
                    return self.caller.msg(f"Successfully deleted field {key} from your +finger.")
                character.db.dossier[key] = value
                self.caller.msg(f"Successfully set +finger {key} to: {value}")
            except ValueError as e:
                self.caller.msg(e)
            
    def split_key_value(self, input_string):
        try:
            # Split the string on '='
            key, value = input_string.split('=', 1)  # Split at the first '='
            key = key.strip()
            value = value.strip()
            return key, value
        except ValueError:
            # Handle cases where '=' is missing or improperly formatted
            raise ValueError("Input must be in the format 'key=value'.")
    
    def add_shown_stat(self, character, stat):
        """
        Adds a stat to the specified category in shown_stats.
        Creates the category if it doesn't exist.
        """
        if stat.category not in character.db.dossier['shown_stats']:
            character.db.dossier['shown_stats'][stat.category] = []
        if stat not in character.db.dossier['shown_stats'][stat.category]:
            character.db.dossier['shown_stats'][stat.category].append(stat.name)\

    def remove_shown_stat(self, character, stat):
        """
        Removes a stat from the specified category in shown_stats.
        Automatically removes the category if it becomes empty.
        """
        if stat.category not in character.db.dossier['shown_stats']:
            return
        if stat.name not in character.db.dossier['shown_stats'][stat.category]:
            return
        character.db.dossier['shown_stats'][stat.category].remove(stat.name)
        # Automatically delete the category if it becomes empty
        if not character.db.dossier['shown_stats'][stat.category]:
            del character.db.dossier['shown_stats'][stat.category]

    def show_finger(self, character):
        def format_stat(stat, value, filler=".", width=38):
            # Special case for 'Traditions Subfaction'
            display_stat = 'Subfaction' if stat == 'Traditions Subfaction' else stat
            
            stat_str = f" {display_stat}"
            value_str = f"{value}"
            dots = filler * (width - len(stat_str) - len(value_str) - 1)
            return f"|w{stat_str}|n{dots}{value_str}"
        dossier = character.get_dossier()
        
        string = header(f"{character.name}'s +finger")
        string += format_stat("Full Name:", "Meowdy", " ")
        string += "  " + format_stat("Idle:", f"|g{format_idle_time(get_idle_time(character))}|n", " ", 42) + "\r\n"
        string += format_stat("Status:", "|gApproved|n" if character.tags.has("approved") else "|rNot Approved|n", " ", 42) + "\r\n"
        if any(key in dossier for key in self.long_fields):
            string += divider("Info") + "\r\n"
            for key in self.long_fields:
                if key not in dossier:
                    continue
                string += f" |w{key.capitalize().ljust(20)}:|n {wrap_ansi(dossier[key], width=56)}\r\n"
        character_stats = character.db.stats or {}
        for category, stats in dossier['shown_stats'].items():
            string += divider(category.capitalize()) + "\r\n"
            for stat in stats:
                stat_obj = Stat.objects.filter(name__iexact=stat, category__iexact=category)[0]
                if category not in character_stats or stat_obj.stat_type not in character_stats[category]:
                    continue
                string += format_stat(stat_obj.name, character_stats[category][stat_obj.stat_type][stat_obj.name]['perm']) + "\r\n"
        string += footer()
        self.caller.msg(string)