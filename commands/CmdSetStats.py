from evennia import Command as BaseCommand
from evennia import default_cmds
from world.wod20th.models import Stat
from evennia.utils.ansi import ANSIString

class CmdStats(default_cmds.MuxCommand):
    """
    Staff-only command to modify character stats.

    Usage:
      +stats <character>/<stat>=[+-]<value>
      +stats me/<stat>=[+-]<value>
      +stats <character>=reset
      +stats me=reset

    Example:
      +stats Bob/strength=+2
      +stats Alice/firearms=-1
      +stats John/status=Active
      +stats John/status=
      +stats Bob/strength=5
      +stats Alice/firearms=Expert
      +stats me/strength=+2
      +stats me=reset
    """

    key = "+stats"
    locks = "cmd:perm(Builder)"  # Only Builders and above can use this command
    arg_regex = r"\s|$"

    def parse(self):
        """
        Parse the arguments.
        """
        try:
            self.character_name, self.stat_name_value = self.args.split('/', 1)
            if '=' in self.stat_name_value:
                self.stat_name, self.value_change = self.stat_name_value.split('=', 1)
            else:
                self.stat_name = self.stat_name_value
                self.value_change = None
        except ValueError:
            self.character_name = self.stat_name_value = self.stat_name = self.value_change = None

    def func(self):
        """Implement the command"""

        if not self.character_name:
            self.caller.msg("|rUsage: +stats <character>/<stat>=[+-]<value>|n")
            return

        if self.character_name.lower() == 'me':
            character = self.caller
        else:
            character = self.caller.search(self.character_name)

        if not character:
            self.caller.msg(f"|rCharacter '{self.character_name}' not found.|n")
            return

        # Handle the reset command
        if self.stat_name and self.stat_name.lower() == 'reset':
            character.db.stats = {}
            self.caller.msg(f"|gReset all stats for {character.name}.|n")
            character.msg(f"|y{self.caller.name}|n |greset all your stats.|n")
            return

        if not self.stat_name:
            self.caller.msg("|rUsage: +stats <character>/<stat>=[+-]<value>|n")
            return

        # Fetch the stat definition from the database with partial matching
        matching_stats = Stat.objects.filter(name__icontains=self.stat_name)
        if not matching_stats:
            self.caller.msg(f"|rNo stats matching '{self.stat_name}' found in the database.|n")
            return

        if len(matching_stats) > 1:
            self.caller.msg(f"|rMultiple stats matching '{self.stat_name}' found: {[stat.name for stat in matching_stats]}. Please be more specific.|n")
            return

        stat = matching_stats.first()
        full_stat_name = stat.name

        # Determine if the stat should be removed
        if self.value_change == '':
            # Remove the stat
            current_stats = character.db.stats.get(stat.category, {}).get(stat.stat_type, {})
            if full_stat_name in current_stats:
                del current_stats[full_stat_name]
                character.db.stats[stat.category][stat.stat_type] = current_stats
                self.caller.msg(f"|gRemoved stat '{full_stat_name}' from {character.name}.|n")
                character.msg(f"|y{self.caller.name}|n |rremoved your stat|n '|y{full_stat_name}|n'.")
            else:
                self.caller.msg(f"|rStat '{full_stat_name}' not found on {character.name}.|n")
            return

        # Determine if the stat value should be treated as a number or a string
        try:
            value_change = int(self.value_change)
            is_number = True
        except (ValueError, TypeError):
            value_change = self.value_change
            is_number = False

        # Check if the stat exists for the character and get the current value
        if not hasattr(character.db, "stats"):
            character.db.stats = {}

        current_value = character.get_stat(stat.category, stat.stat_type, full_stat_name)
        if current_value is None:
            # Initialize the stat if it doesn't exist
            current_value = 0 if is_number else ''

        if self.value_change and (self.value_change.startswith('+') or self.value_change.startswith('-')):
            if is_number:
                new_value = current_value + value_change
            else:
                self.caller.msg(f"|rIncrement/decrement values must be integers.|n")
                return
        else:
            new_value = value_change

        # Validate the new value against the stat's valid values
        valid_values = stat.values
        if valid_values and new_value not in valid_values:
            self.caller.msg(f"|rValue '{new_value}' is not valid for stat '{full_stat_name}'. Valid values are: {valid_values}|n")
            return

        # Update the stat
        character.set_stat(stat.category, stat.stat_type, full_stat_name, new_value)
        # Also set the temporary value
        character.set_stat(stat.category, stat.stat_type, full_stat_name, new_value, temp=True)

        self.caller.msg(f"|gUpdated {character.name}'s {full_stat_name} to {new_value}.|n")
        character.msg(f"|y{self.caller.name}|n |gupdated your|n '|y{full_stat_name}|n' |gto {new_value}.|n")
