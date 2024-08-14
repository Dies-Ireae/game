from evennia.utils.evmenu import EvMenu
from evennia.utils import create
from world.oss.models import District, Sector, Neighborhood, Site
from evennia.objects.models import ObjectDB

# Menu for creating Districts
def start_menu_district(caller):
    text = "Welcome to the District Creation Menu. What would you like to do?"
    options = [
        {"desc": "Create a new District", "goto": "create_district"},
        {"desc": "Create District from Current Room", "goto": "create_district_from_room"},
        {"desc": "Cancel", "goto": "menu_cancel"},
    ]
    return text, options

def create_district(caller):
    text = "Please enter the name of the new District:"
    options = {"key": "_default", "goto": "set_district_name"}
    return text, options

def set_district_name(caller, raw_string):
    district_name = raw_string.strip()
    district = District.objects.create(name=district_name)
    caller.msg(f"District '{district_name}' created successfully!")
    return "start_menu_district"

def create_district_from_room(caller):
    room = caller.location
    district = District.objects.create(name=room.key, room=room)
    district.save()
    caller.msg(f"District '{room.key}' created successfully from the current room!")
    return "start_menu_district"

# Menu for creating Sectors
def start_menu_sector(caller):
    text = "Welcome to the Sector Creation Menu. What would you like to do?"
    options = [
        {"desc": "Create a new Sector", "goto": "create_sector"},
        {"desc": "Create Sector from Current Room", "goto": "create_sector_from_room"},
        {"desc": "Add Current Room to District as Sector", "goto": "add_room_to_district_as_sector"},
        {"desc": "Cancel", "goto": "menu_cancel"},
    ]
    return text, options

def create_sector(caller):
    text = "Please enter the name of the new Sector:"
    options = {"key": "_default", "goto": "set_sector_name"}
    return text, options

def set_sector_name(caller, raw_string):
    sector_name = raw_string.strip()
    districts = District.objects.all()  # List available districts for selection
    text = f"Please select the District this Sector belongs to:\n"
    for i, district in enumerate(districts):
        text += f"{i + 1}. {district.name}\n"
    options = [{"key": str(i + 1), "goto": ("assign_district", {"sector_name": sector_name, "district_index": i})} for i in range(len(districts))]
    return text, options

def assign_district(caller, raw_string, **kwargs):
    sector_name = kwargs["sector_name"]
    district_index = int(kwargs["district_index"])
    district = District.objects.all()[district_index]
    sector = Sector.objects.create(name=sector_name, district=district)
    caller.msg(f"Sector '{sector_name}' created successfully within District '{district.name}'!")
    return "start_menu_sector"

def create_sector_from_room(caller):
    room = caller.location
    districts = District.objects.all()  # List available districts for selection
    text = f"Please select the District this Sector belongs to:\n"
    for i, district in enumerate(districts):
        text += f"{i + 1}. {district.name}\n"
    options = [{"key": str(i + 1), "goto": ("assign_district_from_room", {"room": room, "district_index": i})} for i in range(len(districts))]
    return text, options

def assign_district_from_room(caller, raw_string, **kwargs):
    room = kwargs["room"]
    district_index = int(kwargs["district_index"])
    district = District.objects.all()[district_index]
    sector = Sector.objects.create(name=room.key, district=district, room=room)
    sector.save()
    caller.msg(f"Sector '{room.key}' created successfully from the current room within District '{district.name}'!")
    return "start_menu_sector"

def add_room_to_district_as_sector(caller):
    room = caller.location
    districts = District.objects.all()
    text = f"Please select the District to add your current Room as a Sector:\n"
    for i, district in enumerate(districts):
        text += f"{i + 1}. {district.name}\n"
    options = [{"key": str(i + 1), "goto": ("link_room_to_district_as_sector", {"room": room, "district_index": i})} for i in range(len(districts))]
    return text, options

def link_room_to_district_as_sector(caller, raw_string, **kwargs):
    room = kwargs["room"]
    district_index = int(kwargs["district_index"])
    district = District.objects.all()[district_index]
    sector = Sector.objects.create(name=room.key, district=district, room=room)
    sector.save()
    caller.msg(f"Room '{room.key}' linked to District '{district.name}' as a Sector.")
    return "start_menu_sector"

# Menu for creating Neighborhoods
def start_menu_neighborhood(caller):
    text = "Welcome to the Neighborhood Creation Menu. What would you like to do?"
    options = [
        {"desc": "Create a new Neighborhood", "goto": "create_neighborhood"},
        {"desc": "Create Neighborhood from Current Room", "goto": "create_neighborhood_from_room"},
        {"desc": "Add Current Room to Sector as Neighborhood", "goto": "add_room_to_sector_as_neighborhood"},
        {"desc": "Cancel", "goto": "menu_cancel"},
    ]
    return text, options

def create_neighborhood(caller):
    text = "Please enter the name of the new Neighborhood:"
    options = {"key": "_default", "goto": "set_neighborhood_name"}
    return text, options

def set_neighborhood_name(caller, raw_string):
    neighborhood_name = raw_string.strip()
    sectors = Sector.objects.all()  # List available sectors for selection
    text = f"Please select the Sector this Neighborhood belongs to:\n"
    for i, sector in enumerate(sectors):
        text += f"{i + 1}. {sector.name}\n"
    options = [{"key": str(i + 1), "goto": ("assign_sector", {"neighborhood_name": neighborhood_name, "sector_index": i})} for i in range(len(sectors))]
    return text, options

def assign_sector(caller, raw_string, **kwargs):
    neighborhood_name = kwargs["neighborhood_name"]
    sector_index = int(kwargs["sector_index"])
    sector = Sector.objects.all()[sector_index]
    neighborhood = Neighborhood.objects.create(name=neighborhood_name, sector=sector)
    caller.msg(f"Neighborhood '{neighborhood_name}' created successfully within Sector '{sector.name}'!")
    return "start_menu_neighborhood"

def create_neighborhood_from_room(caller):
    room = caller.location
    sectors = Sector.objects.all()  # List available sectors for selection
    text = f"Please select the Sector this Neighborhood belongs to:\n"
    for i, sector in enumerate(sectors):
        text += f"{i + 1}. {sector.name}\n"
    options = [{"key": str(i + 1), "goto": ("assign_sector_from_room", {"room": room, "sector_index": i})} for i in range(len(sectors))]
    return text, options

def assign_sector_from_room(caller, raw_string, **kwargs):
    room = kwargs["room"]
    sector_index = int(kwargs["sector_index"])
    sector = Sector.objects.all()[sector_index]
    neighborhood = Neighborhood.objects.create(name=room.key, sector=sector, room=room)
    neighborhood.save()
    caller.msg(f"Neighborhood '{room.key}' created successfully from the current room within Sector '{sector.name}'!")
    return "start_menu_neighborhood"

def add_room_to_sector_as_neighborhood(caller):
    room = caller.location
    sectors = Sector.objects.all()
    text = f"Please select the Sector to add your current Room as a Neighborhood:\n"
    for i, sector in enumerate(sectors):
        text += f"{i + 1}. {sector.name}\n"
    options = [{"key": str(i + 1), "goto": ("link_room_to_sector_as_neighborhood", {"room": room, "sector_index": i})} for i in range(len(sectors))]
    return text, options

def link_room_to_sector_as_neighborhood(caller, raw_string, **kwargs):
    room = kwargs["room"]
    sector_index = int(kwargs["sector_index"])
    sector = Sector.objects.all()[sector_index]
    neighborhood = Neighborhood.objects.create(name=room.key, sector=sector, room=room)
    neighborhood.save()
    caller.msg(f"Room '{room.key}' linked to Sector '{sector.name}' as a Neighborhood.")
    return "start_menu_neighborhood"

def start_menu_site(caller):
    text = "Welcome to the Site Creation Menu. What would you like to do?"
    options = [
        {"desc": "Create a new Site", "goto": "create_site"},
        {"desc": "Create Site from Current Room", "goto": "create_site_from_room"},
        {"desc": "Add Current Room to Neighborhood as Site", "goto": "add_room_to_neighborhood_as_site"},
        {"desc": "Cancel", "goto": "menu_cancel"},
    ]
    return text, options

def create_site(caller):
    text = "Please enter the name of the new Site:"
    options = {"key": "_default", "goto": "set_site_name"}
    return text, options

def set_site_name(caller, raw_string):
    site_name = raw_string.strip()
    neighborhoods = Neighborhood.objects.all()  # List available neighborhoods for selection
    text = f"Please select the Neighborhood this Site belongs to:\n"
    for i, neighborhood in enumerate(neighborhoods):
        text += f"{i + 1}. {neighborhood.name}\n"
    options = [{"key": str(i + 1), "goto": ("assign_neighborhood", {"site_name": site_name, "neighborhood_index": i})} for i in range(len(neighborhoods))]
    return text, options

def assign_neighborhood(caller, raw_string, **kwargs):
    site_name = kwargs["site_name"]
    neighborhood_index = int(kwargs["neighborhood_index"])
    neighborhood = Neighborhood.objects.all()[neighborhood_index]
    site = Site.objects.create(name=site_name, neighborhood=neighborhood)
    caller.msg(f"Site '{site_name}' created successfully within Neighborhood '{neighborhood.name}'!")
    return "start_menu_site"

def create_site_from_room(caller):
    room = caller.location
    neighborhoods = Neighborhood.objects.all()  # List available neighborhoods for selection
    text = f"Please select the Neighborhood this Site belongs to:\n"
    for i, neighborhood in enumerate(neighborhoods):
        text += f"{i + 1}. {neighborhood.name}\n"
    options = [{"key": str(i + 1), "goto": ("assign_neighborhood_from_room", {"room": room, "neighborhood_index": i})} for i in range(len(neighborhoods))]
    return text, options

def assign_neighborhood_from_room(caller, raw_string, **kwargs):
    room = kwargs["room"]
    neighborhood_index = int(kwargs["neighborhood_index"])
    neighborhood = Neighborhood.objects.all()[neighborhood_index]
    site = Site.objects.create(name=room.key, neighborhood=neighborhood, room=room)
    site.save()
    caller.msg(f"Site '{room.key}' created successfully from the current room within Neighborhood '{neighborhood.name}'!")
    return "start_menu_site"

def add_room_to_neighborhood_as_site(caller):
    room = caller.location
    neighborhoods = Neighborhood.objects.all()
    text = f"Please select the Neighborhood to add your current Room as a Site:\n"
    for i, neighborhood in enumerate(neighborhoods):
        text += f"{i + 1}. {neighborhood.name}\n"
    options = [{"key": str(i + 1), "goto": ("link_room_to_neighborhood_as_site", {"room": room, "neighborhood_index": i})} for i in range(len(neighborhoods))]
    return text, options

def link_room_to_neighborhood_as_site(caller, raw_string, **kwargs):
    room = kwargs["room"]
    neighborhood_index = int(kwargs["neighborhood_index"])
    neighborhood = Neighborhood.objects.all()[neighborhood_index]
    site = Site.objects.create(name=room.key, neighborhood=neighborhood, room=room)
    site.save()
    caller.msg(f"Room '{room.key}' linked to Neighborhood '{neighborhood.name}' as a Site.")
    return "start_menu_site"

# Common cancel function
def menu_cancel(caller):
    caller.msg("Operation canceled.")
    return

builder_menutree = {
    "start_menu_district": start_menu_district,
    "create_district": create_district,
    "set_district_name": set_district_name,
    "create_district_from_room": create_district_from_room,
    "start_menu_sector": start_menu_sector,
    "create_sector": create_sector,
    "set_sector_name": set_sector_name,
    "assign_district": assign_district,
    "create_sector_from_room": create_sector_from_room,
    "assign_district_from_room": assign_district_from_room,
    "add_room_to_district_as_sector": add_room_to_district_as_sector,
    "link_room_to_district_as_sector": link_room_to_district_as_sector,
    "start_menu_neighborhood": start_menu_neighborhood,
    "create_neighborhood": create_neighborhood,
    "set_neighborhood_name": set_neighborhood_name,
    "assign_sector": assign_sector,
    "create_neighborhood_from_room": create_neighborhood_from_room,
    "assign_sector_from_room": assign_sector_from_room,
    "add_room_to_sector_as_neighborhood": add_room_to_sector_as_neighborhood,
    "link_room_to_sector_as_neighborhood": link_room_to_sector_as_neighborhood,
    "start_menu_site": start_menu_site,
    "create_site": create_site,
    "set_site_name": set_site_name,
    "assign_neighborhood": assign_neighborhood,
    "create_site_from_room": create_site_from_room,
    "assign_neighborhood_from_room": assign_neighborhood_from_room,
    "add_room_to_neighborhood_as_site": add_room_to_neighborhood_as_site,
    "link_room_to_neighborhood_as_site": link_room_to_neighborhood_as_site,
    "menu_cancel": menu_cancel,
}

def start_district_menu(caller):
    EvMenu(caller, menutree=menutree, startnode="start_menu_district")