"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property and overrides some hooks
    and methods to represent the exits.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects child classes like this.

    """

    def at_object_creation(self):
        super().at_object_creation()
        
        # If aliases are set, use the first one as the exit's key
        if self.aliases.all():
            first_alias = self.aliases.all()[0]
            self.key = first_alias
            
            # Remove the first alias from the aliases list
            self.aliases.remove(first_alias)

    def set_aliases(self, aliases):
        """
        Custom method to set aliases and update the exit's key.
        """
        if aliases:
            # Set the first alias as the exit's key
            self.key = aliases[0]
            
            # Add the remaining aliases
            for alias in aliases[1:]:
                self.aliases.add(alias)
        else:
            # If no aliases are provided, you might want to set a default key
            self.key = "Exit"

    pass
