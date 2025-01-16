"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia import DefaultExit
from evennia.utils import logger
from evennia.commands.cmdset import CmdSet
from evennia.commands.command import Command

class ExitCommand(Command):
    """
    Command class for an exit.
    """
    def __init__(self, key=None, aliases=None, destination=None, **kwargs):
        super().__init__(**kwargs)
        self.key = key.lower() if key else ""
        self.aliases = [alias.lower() for alias in aliases] if aliases else []
        self.destination = destination
        self.locks = "cmd:all()"
        self.auto_help = False
    
    def func(self):
        """
        Move caller to destination.
        """
        # First check if we can even see the exit
        if not self.obj.access(self.caller, "view"):
            self.caller.msg("You cannot go that way.")
            return
            
        # Debug output
        self.caller.msg(f"DEBUG: Attempting to traverse {self.obj.key}")
        self.caller.msg(f"DEBUG: Current locks: {self.obj.locks}")
        
        # Check if we can traverse
        if not self.obj.access(self.caller, "traverse"):
            self.caller.msg(f"You cannot go that way.")
            return
            
        # All good - try to traverse
        self.obj.at_traverse(self.caller, self.obj.destination)
    
    def access(self, accessing_obj, access_type="cmd", default=True):
        """
        Override access check to include view lock.
        """
        if access_type == "cmd":
            return self.obj.access(accessing_obj, "view")
        return super().access(accessing_obj, access_type, default)

class ExitCmdSet(CmdSet):
    """
    Cmdset for exits.
    """
    key = "ExitCmdSet"
    priority = 101
    duplicates = False
    
    def at_cmdset_creation(self):
        """
        Called when the cmdset is created.
        """
        self.add(ExitCommand)

class Exit(DefaultExit):
    """
    Custom exit class for Dies Irae.
    """
    
    def at_object_creation(self):
        """
        Called when exit is first created.
        """
        super().at_object_creation()
        self.at_cmdset_creation()
        
    def at_cmdset_creation(self):
        """
        Called when cmdset is first created.
        """
        cmdset = ExitCmdSet()
        cmdset.key = f"ExitCmdSet_{self.key}"
        cmdset.priority = 101
        cmdset.duplicates = False
        cmdset.obj = self
        
        cmd = ExitCommand(
            key=self.name,
            aliases=self.aliases.all(),
            destination=self.destination,
            obj=self
        )
        cmdset.add(cmd)
        self.cmdset.add(cmdset, permanent=True)
    
    def return_appearance(self, looker, **kwargs):
        """
        This formats how the exit appears in listings.
        Only show if the looker passes the view lock.
        """
        if not self.access(looker, "view"):
            return ""
        return super().return_appearance(looker, **kwargs)
        
    def get_display_name(self, looker, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.
        Only show if the looker passes the view lock.
        """
        if not self.access(looker, "view"):
            return ""
        return super().get_display_name(looker, **kwargs)
    
    def get_aliases(self, looker, **kwargs):
        """
        Returns the aliases for this specific looker.
        Only show if the looker passes the view lock.
        """
        if not self.access(looker, "view"):
            return []
        return super().get_aliases(looker, **kwargs)
    
    def format_appearance(self, looker, **kwargs):
        """
        Format the appearance of the exit.
        Only show if the looker passes the view lock.
        """
        if not self.access(looker, "view"):
            return ""
        return super().format_appearance(looker, **kwargs)
    
    def get_extra_info(self, looker, **kwargs):
        """
        Returns the exit's extra info (like <O>).
        Only show if the looker passes the view lock.
        """
        if not self.access(looker, "view"):
            return ""
            
        # Get the first letter of the name if no aliases
        if not self.aliases.all():
            if not self.name:
                return "<>"
            return f"<{self.name[0].upper()}>"
            
        # Get the first alias
        alias = self.aliases.all()[0]
        if not alias:
            return "<>"
        return f"<{alias.upper()}>"
    
    def at_look(self, looker, **kwargs):
        """
        Called when this object is looked at.
        Only show if the looker passes the view lock.
        """
        if not self.access(looker, "view"):
            return ""
        return super().at_look(looker, **kwargs)
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        Called when an object wants to traverse this exit.
        """
        # Add more detailed debug output
        if hasattr(traversing_object, 'msg'):
            traversing_object.msg(f"DEBUG: Attempting to traverse {self.key}")
            traversing_object.msg(f"DEBUG: Current locks: {self.locks}")
            
            # Get all available lock functions from the handler
            from evennia.locks import lockfuncs
            from world.wod20th.locks import LOCK_FUNCS
            
            traversing_object.msg(f"DEBUG: Built-in lock functions: {[func for func in dir(lockfuncs) if not func.startswith('_')]}")
            traversing_object.msg(f"DEBUG: Custom WoD lock functions: {list(LOCK_FUNCS.keys())}")
            traversing_object.msg(f"DEBUG: Lock types: {self.locks.all()}")
            
            # Test the lock directly
            result = self.access(traversing_object, "traverse")
            traversing_object.msg(f"DEBUG: Traverse access check result: {result}")
            
            # If it failed, let's see why
            if not result:
                # Get the actual lock string
                lock_str = self.locks.get("traverse")
                traversing_object.msg(f"DEBUG: Traverse lock string: {lock_str}")
                
                # Test each component
                if hasattr(traversing_object, 'character'):
                    char = traversing_object.character
                else:
                    char = traversing_object
                    
                from world.wod20th.locks import has_mage_faction
                direct_test = has_mage_faction(char, None, "Traditions")
                traversing_object.msg(f"DEBUG: Direct function test: {direct_test}")
        
        # Check if object has permission to pass
        if not self.access(traversing_object, "traverse"):
            if hasattr(traversing_object, 'msg'):
                traversing_object.msg(f"You cannot traverse {self.key}.")
            return False
        
        # Call parent's at_traverse
        return super().at_traverse(traversing_object, target_location, **kwargs)
    
    def at_failed_traverse(self, traversing_object, **kwargs):
        """
        Called when traversal fails.
        """
        if hasattr(traversing_object, 'msg'):
            traversing_object.msg(f"You cannot traverse {self.key}.")
            traversing_object.msg("DEBUG: Traverse failed - insufficient permissions.")
        return False
    
    def get_cmd_signatures(self, caller):
        """
        Returns a list of command signatures available to the caller.
        Hide commands if caller can't view the exit.
        """
        if not self.access(caller, "view"):
            return []
        return super().get_cmd_signatures(caller)
    
    def at_before_get(self, looker, **kwargs):
        """
        Called before get/search attempts.
        Only allow if the looker passes the view lock.
        """
        if not self.access(looker, "view"):
            return False
        return True
    
    def matches(self, searchdata, exact=False, global_search=False, caller=None, **kwargs):
        """
        Match if searcher passes view check.
        """
        if caller and not self.access(caller, "view"):
            return 0.0
        return super().matches(searchdata, exact, global_search, caller, **kwargs)
    
    def search(self, searchdata, caller=None, **kwargs):
        """
        Search only if caller passes view check.
        """
        if caller and not self.access(caller, "view"):
            return None
        return super().search(searchdata, caller=caller, **kwargs)