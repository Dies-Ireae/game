from evennia import Command, CmdSet
from evennia.utils.evmenu import EvMenu
from evennia.utils.utils import crop
from evennia.utils.evtable import EvTable
from commands.oss.builder_menus import builder_menutree
from commands.oss.event_menus import start_event_menu
from world.oss.models import District, Sector, Neighborhood

class CmdCreateDistrict(Command):
    """
    Start the District creation menu.
    """
    key = "create_district"
    aliases = ["createdistrict"]
    locks = "cmd:perm(Builders)"
    help_category = "OSS"

    def func(self):
        EvMenu(self.caller, builder_menutree, startnode="start_menu_district")

# Command to start the Sector creation menu
class CmdCreateSector(Command):
    """
    Start the Sector creation menu.
    """
    key = "create_sector"
    aliases = ["createsector"]
    locks = "cmd:perm(Builders)"
    help_category = "OSS"

    def func(self):
        EvMenu(self.caller, builder_menutree, startnode="start_menu_sector")

# Command to start the Neighborhood creation menu
class CmdCreateNeighborhood(Command):
    """
    Start the Neighborhood creation menu.
    """
    key = "create_neighborhood"
    aliases = ["createneighborhood"]
    locks = "cmd:perm(Builders)"
    help_category = "OSS"

    def func(self):
        EvMenu(self.caller, builder_menutree, startnode="start_menu_neighborhood")

# Command to start the Site creation menu
class CmdCreateSite(Command):
    """
    Start the Site creation menu.
    """
    key = "create_site"
    aliases = ["createsite"]
    locks = "cmd:perm(Builders)"
    help_category = "OSS"

    def func(self):
        EvMenu(self.caller, builder_menutree, startnode="start_menu_site")

class CmdCreateEvent(Command):
    """
    Starts the menu for creating a new event.
    
    Usage:
      createevent

    This command will initiate the event creation process.
    """
    key = "createevent"
    aliases = ["newevent"]
    locks = "cmd:all()"
    help_category = "Event Management"

    def func(self):
        """
        This is the main body of the command.
        """
        EvMenu(self.caller, start_event_menu)

class CmdEditEvent(Command):
    """
    Starts the menu for editing an existing event.
    
    Usage:
      editevent <event name>

    This command will initiate the event editing process.
    """
    key = "editevent"
    aliases = ["modifyevent"]
    locks = "cmd:all()"
    help_category = "Event Management"

    def func(self):
        """
        This is the main body of the command.
        """
        if not self.args:
            self.caller.msg("Please specify the name of the event you want to edit.")
            return

        event_name = self.args.strip()
        event = Event.objects.filter(name__iexact=event_name).first()

        if not event:
            self.caller.msg(f"No event found with the name '{event_name}'. Please check the name and try again.")
            return

        self.caller.msg(f"Editing event '{event.name}'...")
        EvMenu(self.caller, start_event_menu, {"event": event})

class CmdShowHierarchy(Command):
    """
    Display Districts, Sectors, and Neighborhoods in a tree format.
    
    Usage:
        showhierarchy
    """
    key = "showhierarchy"
    locks = "cmd:perm(Builders)"
    help_category = "OSS"

    def func(self):
        # Fetch all districts
        districts = District.objects.all()
        
        if not districts.exists():
            self.caller.msg("No Districts found.")
            return
        
        tree = []

        for district in districts:
            tree.append(f"District: {district.name}")
            sectors = district.sectors.all()
            if sectors.exists():
                for sector in sectors:
                    tree.append(f"  Sector: {sector.name}")
                    neighborhoods = sector.neighborhoods.all()
                    if neighborhoods.exists():
                        for neighborhood in neighborhoods:
                            tree.append(f"    Neighborhood: {neighborhood.name}")
                    else:
                        tree.append("    No Neighborhoods found.")
            else:
                tree.append("  No Sectors found.")

        # Join the tree into a single string to display
        tree_display = "\n".join(tree)
        self.caller.msg(tree_display)