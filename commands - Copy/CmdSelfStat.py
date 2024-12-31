from evennia import default_cmds
from world.wod20th.models import Stat, SHIFTER_IDENTITY_STATS, SHIFTER_RENOWN, calculate_willpower, calculate_road
from evennia.utils import search
import re

class CmdSelfStat(default_cmds.MuxCommand):
    """
    Usage:
      +selfstat <stat>[(<instance>)]/<category>=[+-]<value>
      +selfstat <stat>[(<instance>)]/<category>=

    Examples:
      +selfstat Strength/Physical=+1
      +selfstat Firearms/Skill=-1
      +selfstat Status(Ventrue)/Social=
    """

    key = "+selfstat"
    aliases = ["selfstat"]
    locks = "cmd:all()"  # All players can use this command
    help_category = "Character"

    def parse(self):
        """Parse the command arguments."""
        args = self.args.strip()
        
        if not args or '=' not in args:
            self.stat_name = None
            self.instance = None
            self.value = None
            return
        
        # Split on the first equals sign
        stat_part, value_part = args.split('=', 1)
        
        # Check if there's an instance (something in parentheses)
        if '(' in stat_part and ')' in stat_part:
            self.stat_name, instance_part = stat_part.split('(', 1)
            self.instance = instance_part.split(')', 1)[0]
        else:
            self.stat_name = stat_part
            self.instance = None
        
        # Clean up the stat name
        self.stat_name = self.stat_name.strip()
        
        # Handle the value part
        value_part = value_part.strip()
        if not value_part:  # If value is empty, this is a removal request
            self.value = ''  # Use empty string to indicate removal
        else:
            try:
                self.value = int(value_part)
            except ValueError:
                self.value = value_part

    def func(self):
        """Execute the command."""
        if not self.stat_name:
            self.caller.msg("Usage: +selfstat StatName=Value or +selfstat StatName(Instance)=Value")
            return

        # Get the stat definition
        stat = Stat.objects.filter(name__iexact=self.stat_name).first()
        if not stat:
            # If exact match fails, try a case-insensitive contains search
            matching_stats = Stat.objects.filter(name__icontains=self.stat_name)
            if matching_stats.count() > 1:
                stat_names = [s.name for s in matching_stats]
                self.caller.msg(f"Multiple stats match '{self.stat_name}': {', '.join(stat_names)}. Please be more specific.")
                return
            stat = matching_stats.first()
            if not stat:
                self.caller.msg(f"Stat '{self.stat_name}' not found.")
                return

        # Use the canonical name from the database
        self.stat_name = stat.name
        
        # Handle instances for background stats
        if stat.instanced:
            if not self.instance:
                self.caller.msg(f"The stat '{self.stat_name}' requires an instance. Use the format: {self.stat_name}(instance)")
                return
            full_stat_name = f"{self.stat_name}({self.instance})"
        else:
            if self.instance:
                self.caller.msg(f"The stat '{self.stat_name}' does not support instances.")
                return
            full_stat_name = self.stat_name

        # Handle stat removal (empty value) - Move this before validation
        if self.value == '':
            if stat.category in self.caller.db.stats and stat.stat_type in self.caller.db.stats[stat.category]:
                if full_stat_name in self.caller.db.stats[stat.category][stat.stat_type]:
                    del self.caller.db.stats[stat.category][stat.stat_type][full_stat_name]
                    self.caller.msg(f"|gRemoved stat '{full_stat_name}'.|n")
                    return
                else:
                    self.caller.msg(f"|rStat '{full_stat_name}' not found.|n")
                    return

        # Check if this is a dual-type stat (pools, renown, etc)
        dual_stat_types = ['dual', 'renown', 'pool']  # Add renown to dual stat types
        
        if stat.stat_type in dual_stat_types:
            if isinstance(stat.values, dict):
                # For dual stats, validate against the 'perm' values list
                if 'perm' in stat.values and self.value not in stat.values['perm']:
                    try:
                        self.value = int(self.value)  # Convert to int for comparison
                        if self.value not in stat.values['perm']:
                            self.caller.msg(f"|rValue '{self.value}' is not valid for permanent {full_stat_name}. Valid values are: {stat.values['perm']}|n")
                            return
                    except ValueError:
                        self.caller.msg(f"|rValue '{self.value}' is not valid for permanent {full_stat_name}. Valid values are: {stat.values['perm']}|n")
                        return
                
                # Set both permanent and temporary values
                self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=False)
                self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=True)
                self.caller.msg(f"|gUpdated {full_stat_name} to {self.value} (both permanent and temporary).|n")
                return

        # Check if the character passes the stat's lock_string
        try:
            if stat.lockstring and not self.caller.locks.check_lockstring(self.caller, stat.lockstring):
                self.caller.msg(f"|rYou do not have permission to modify the stat '{full_stat_name}'.|n")
                return
        except AttributeError:
            pass

        # Validate the new value against the stat's valid values
        valid_values = stat.values
        if stat.stat_type == 'dual':
            # For dual stats, we need to set both permanent and temporary values
            if isinstance(stat.values, dict):
                # Validate against permanent value range
                if 'perm' in stat.values and self.value not in stat.values['perm']:
                    self.caller.msg(f"|rValue '{self.value}' is not valid for permanent {full_stat_name}. Valid values are: {stat.values['perm']}|n")
                    return
                
                # Set both permanent and temporary values
                self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=False)
                self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=True)
                self.caller.msg(f"|gUpdated {full_stat_name} to {self.value} (both permanent and temporary).|n")
                return

        if stat.stat_type == 'knowledge':
            # Set both permanent and temporary values
            self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=False)
            # Also set the temporary value if it's not already set
            if not self.caller.get_stat(stat.category, stat.stat_type, full_stat_name, temp=True):
                self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=True)
            self.caller.msg(f"|gUpdated {full_stat_name} to {self.value} (both permanent and temporary).|n")
            return

        if valid_values and self.value not in valid_values and valid_values != []:
            self.caller.msg(f"|rValue '{self.value}' is not valid for stat '{full_stat_name}'. Valid values are: {valid_values}|n")
            return

        # Convert value to integer for virtues
        if full_stat_name in ['Courage', 'Self-Control', 'Conscience', 'Conviction', 'Instinct']:
            try:
                self.value = int(self.value)
            except ValueError:
                self.caller.msg(f"|rInvalid value for {full_stat_name}. Please provide an integer.|n")
                return

        # During character generation (when character is not approved), 
        # or for specific stat types, always set temp value equal to permanent value
        if not self.caller.db.approved or stat.stat_type in ['knowledge', 'attribute', 'ability', 'talent', 'skill']:
            # Set both permanent and temporary values
            self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=False)
            self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=True)
            self.caller.msg(f"|gUpdated {full_stat_name} to {self.value} (both permanent and temporary).|n")
            return
        elif stat.stat_type == 'dual':
            # For dual stats, we need to set both permanent and temporary values
            if isinstance(stat.values, dict):
                # Validate against permanent value range
                if 'perm' in stat.values and self.value not in stat.values['perm']:
                    self.caller.msg(f"|rValue '{self.value}' is not valid for permanent {full_stat_name}. Valid values are: {stat.values['perm']}|n")
                    return
                
                # Set both permanent and temporary values
                self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=False)
                self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=True)
                self.caller.msg(f"|gUpdated {full_stat_name} to {self.value} (both permanent and temporary).|n")
                return

        # Update the stat
        self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=False)
        
        # During character generation (when character is not approved), 
        # always set temp value equal to permanent value
        if not self.caller.db.approved:
            self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=True)
            self.caller.msg(f"|gUpdated {full_stat_name} to {self.value} (both permanent and temporary).|n")
        # If already approved, only update temp for pools and dual stats
        elif stat.category == 'pools' or stat.stat_type == 'dual':
            self.caller.set_stat(stat.category, stat.stat_type, full_stat_name, self.value, temp=True)
            self.caller.msg(f"|gUpdated {full_stat_name} to {self.value} (both permanent and temporary).|n")
        else:
            self.caller.msg(f"|gUpdated {full_stat_name} to {self.value}.|n")

        # After setting a stat, recalculate Willpower and Road
        if full_stat_name in ['Courage', 'Self-Control', 'Conscience', 'Conviction', 'Instinct']:
            new_willpower = calculate_willpower(self.caller)
            self.caller.set_stat('pools', 'dual', 'Willpower', new_willpower, temp=False)
            self.caller.set_stat('pools', 'dual', 'Willpower', new_willpower, temp=True)
            self.caller.msg(f"|gRecalculated Willpower to {new_willpower}.|n")

            new_road = calculate_road(self.caller)
            self.caller.set_stat('pools', 'moral', 'Road', new_road, temp=False)
            self.caller.msg(f"|gRecalculated Road to {new_road}.|n")