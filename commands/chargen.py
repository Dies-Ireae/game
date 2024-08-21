# commands/CmdCharGen.py

from evennia import Command
from evennia.utils.evmenu import EvMenu
from world.wod20th.models import Stat
from typeclasses.characters import Character

class CmdCharGen(Command):
    """
    Start the character generation process.

    Usage:
      chargen
    """

    key = "chargen"
    locks = "cmd:all()"
    help_category = "Character Generation"

    def func(self):
        # Initialize chargen data if it doesn't exist
        if not self.caller.db.chargen:
            self.caller.db.chargen = {}
        
        EvMenu(self.caller, "commands.chargen", startnode="node_start", cmd_on_exit=self.finish_chargen)

    def finish_chargen(self, caller, menu):
        """
        Called when character generation is complete.
        """
        caller.msg("Character generation complete!")
        # Additional logic to finalize character creation
        _apply_chargen_data(caller)

    def at_post_cmd(self):
        """
        This hook is called after the command has finished executing 
        (after self.func()).
        """
        if hasattr(self.caller, "ndb._menutree"):
            self.caller.msg("|wUse 'look' to see the character creation menu again.")
            self.caller.msg("Use 'quit' to exit character creation.")

def _apply_chargen_data(self, caller):
        """Apply all chargen data to the character."""
        chargen_data = caller.db.chargen
        
        # Apply basic information
        caller.db.concept = chargen_data.get('concept', '')
        caller.db.nature = chargen_data.get('nature', '')
        caller.db.demeanor = chargen_data.get('demeanor', '')
        caller.db.clan = chargen_data.get('clan', '')

        # Apply attributes
        for category, attributes in chargen_data.get('attributes', {}).items():
            for attr, value in attributes.items():
                caller.set_stat(category, 'attribute', attr, value)

        # Apply abilities
        for category, abilities in chargen_data.get('abilities', {}).items():
            for ability, value in abilities.items():
                caller.set_stat(category, 'ability', ability, value)

        # Apply disciplines
        for discipline, value in chargen_data.get('disciplines', {}).items():
            caller.set_stat('powers', 'discipline', discipline, value)

        # Apply backgrounds
        for background, value in chargen_data.get('backgrounds', {}).items():
            caller.set_stat('backgrounds', 'background', background, value)

        # Clear chargen data
        caller.attributes.remove('chargen')

# Menu nodes

def node_start(caller):
    text = "Welcome to character generation! Let's create your World of Darkness character."
    options = (
        {"key": "1", "desc": "Choose your character concept", "goto": "node_concept"},
        {"key": "2", "desc": "Select your character's nature and demeanor", "goto": "node_nature_demeanor"},
        {"key": "3", "desc": "Choose your character's clan", "goto": "node_clan"},
        {"key": "4", "desc": "Assign Attributes", "goto": "node_attributes"},
        {"key": "5", "desc": "Assign Abilities", "goto": "node_abilities"},
        {"key": "6", "desc": "Choose Disciplines", "goto": "node_disciplines"},
        {"key": "7", "desc": "Select Backgrounds", "goto": "node_backgrounds"},
        {"key": "8", "desc": "Review and Finish", "goto": "node_review"},
    )
    return text, options

def node_concept(caller):
    if "concept" not in caller.db.chargen:
        caller.db.chargen["concept"] = ""
    
    text = "What is your character concept? This is a brief description of who your character is."
    options = (
        {"key": "_default", "goto": _set_concept},
    )
    return text, options

def _set_concept(caller, raw_string):
    concept = raw_string.strip()
    caller.db.chargen["concept"] = concept
    caller.msg(f"Character concept set to: {concept}")
    return "node_start"

def node_nature_demeanor(caller):
    text = "Choose your character's Nature and Demeanor. Nature is your character's true self, while Demeanor is the face they show to the world."
    options = (
        {"key": "1", "desc": "Set Nature", "goto": "set_nature"},
        {"key": "2", "desc": "Set Demeanor", "goto": "set_demeanor"},
        {"key": "3", "desc": "Return to main menu", "goto": "node_start"},
    )
    return text, options

def set_nature(caller):
    if "nature" not in caller.db.chargen:
        caller.db.chargen["nature"] = ""
    
    text = "What is your character's Nature?"
    options = (
        {"key": "_default", "goto": _set_nature},
    )
    return text, options

def _set_nature(caller, raw_string):
    nature = raw_string.strip()
    caller.db.chargen["nature"] = nature
    caller.msg(f"Nature set to: {nature}")
    return "node_nature_demeanor"

def set_demeanor(caller):
    if "demeanor" not in caller.db.chargen:
        caller.db.chargen["demeanor"] = ""
    
    text = "What is your character's Demeanor?"
    options = (
        {"key": "_default", "goto": _set_demeanor},
    )
    return text, options

def _set_demeanor(caller, raw_string):
    demeanor = raw_string.strip()
    caller.db.chargen["demeanor"] = demeanor
    caller.msg(f"Demeanor set to: {demeanor}")
    return "node_nature_demeanor"

def node_clan(caller):
    text = "Choose your character's clan:"
    clans = Stat.objects.filter(category="identity", stat_type="lineage", name="Clan")
    options = [{"key": str(i+1), "desc": clan, "goto": (_set_clan, {"clan": clan})} 
               for i, clan in enumerate(clans[0].values)]
    options.append({"key": "0", "desc": "Return to main menu", "goto": "node_start"})
    return text, options

def _set_clan(caller, raw_string, **kwargs):
    clan = kwargs.get("clan")
    caller.db.chargen["clan"] = clan
    caller.msg(f"Clan set to: {clan}")
    return "node_start"

def node_attributes(caller):
    if "attributes" not in caller.db.chargen:
        caller.db.chargen["attributes"] = {
            "physical": {"Strength": 1, "Dexterity": 1, "Stamina": 1},
            "social": {"Charisma": 1, "Manipulation": 1, "Appearance": 1},
            "mental": {"Perception": 1, "Intelligence": 1, "Wits": 1}
        }
    
    if "attribute_priority" not in caller.db.chargen:
        caller.db.chargen["attribute_priority"] = None
    
    text = "Assign your character's Attributes. Choose the priority order for Physical, Social, and Mental attributes:\n"
    text += "Primary (7 points), Secondary (5 points), and Tertiary (3 points).\n"
    text += f"Current priority: {caller.db.chargen['attribute_priority'] or 'Not set'}\n"
    
    options = [
        {"key": "1", "desc": "PMS (Physical, Mental, Social)", "goto": (_set_attribute_priority, {"priority": "PMS"})},
        {"key": "2", "desc": "PSM (Physical, Social, Mental)", "goto": (_set_attribute_priority, {"priority": "PSM"})},
        {"key": "3", "desc": "SMP (Social, Mental, Physical)", "goto": (_set_attribute_priority, {"priority": "SMP"})},
        {"key": "4", "desc": "SPM (Social, Physical, Mental)", "goto": (_set_attribute_priority, {"priority": "SPM"})},
        {"key": "5", "desc": "MPS (Mental, Physical, Social)", "goto": (_set_attribute_priority, {"priority": "MPS"})},
        {"key": "6", "desc": "MSP (Mental, Social, Physical)", "goto": (_set_attribute_priority, {"priority": "MSP"})},
        {"key": "7", "desc": "Assign Points", "goto": "assign_attribute_points"},
        {"key": "0", "desc": "Return to main menu", "goto": "node_start"},
    ]
    return text, options

def set_primary_attributes(caller):
    return _set_attribute_priority(caller, "primary")

def set_secondary_attributes(caller):
    return _set_attribute_priority(caller, "secondary")

def set_tertiary_attributes(caller):
    return _set_attribute_priority(caller, "tertiary")

def _set_attribute_priority(caller, raw_string, **kwargs):
    priority = kwargs.get('priority')
    if priority:
        caller.db.chargen["attribute_priority"] = priority
        caller.msg(f"Attribute priority set to: {priority}")
    else:
        caller.msg("Error: No priority specified.")
    return "node_attributes"

def _assign_priority(caller, raw_string, priority, category):
    caller.db.chargen["attribute_priority"][priority] = category
    caller.msg(f"{category.capitalize()} set as {priority} attribute category.")
    return "node_attributes"

def assign_attribute_points(caller):
    priority = caller.db.chargen["attribute_priority"]
    if not priority:
        caller.msg("You must set attribute priorities before assigning points.")
        return "node_attributes"
    
    categories = {
        'P': 'physical',
        'S': 'social',
        'M': 'mental'
    }
    
    points = {'P': 7, 'S': 5, 'M': 3}
    
    # Determine which category we're currently assigning
    for cat in priority:
        category = categories[cat]
        total_points = points[cat] + 3  # Adding 3 because each attribute starts at 1
        if sum(caller.db.chargen['attributes'][category].values()) < total_points:
            break
    else:
        # If we've completed all categories, move to the next step
        caller.msg("You've completed assigning all attribute points.")
        return "node_abilities"  # Move to abilities after completing attributes
    
    text = f"Assign points to {category.capitalize()} attributes. You have {points[cat]} points to spend.\n"
    text += "Format: <attribute> <value> (e.g., 'strength 3' or 'charisma 4')\n"
    
    for attr, value in caller.db.chargen['attributes'][category].items():
        text += f"{attr}: {value}\n"
    
    options = [
        {"key": "_default", "goto": (_process_attribute_input, {"category": category, "points": points[cat], "priority": priority})},
        {"key": "0", "desc": "Return to attributes menu", "goto": "node_attributes"}
    ]
    
    return text, options

def _assign_attributes(caller, category, points):
    attributes = caller.db.chargen['attributes'][category]
    total_points = points + 3  # Adding 3 because each attribute starts at 1
    used_points = sum(attributes.values())
    remaining_points = total_points - used_points

    text = f"Assign points to {category.capitalize()} attributes. You have {remaining_points} points left.\n"
    text += "Format: <attribute> <value> (e.g., 'str 3' or 'dex 4')\n"
    for attr, value in attributes.items():
        text += f"{attr}: {value}\n"

    options = [
        {"key": "_default", "goto": (_process_attribute_input, {"category": category, "points": points})}
    ]
    options.append({"key": "0", "desc": "Return to attributes menu", "goto": "node_attributes"})

    return text, options

def _process_attribute_input(caller, raw_string, **kwargs):
    category = kwargs.get('category')
    points = kwargs.get('points')
    priority = kwargs.get('priority')
    
    try:
        attr, value = raw_string.split()
        attr = attr.capitalize()
        value = int(value)

        if attr not in caller.db.chargen['attributes'][category]:
            caller.msg(f"Invalid attribute: {attr}. Please use a valid attribute name.")
            return "assign_attribute_points"

        current_value = caller.db.chargen['attributes'][category][attr]
        total_points = points + 3  # Adding 3 because each attribute starts at 1
        used_points = sum(caller.db.chargen['attributes'][category].values())
        remaining_points = total_points - used_points + current_value  # Add back the current value

        if value < 1 or value > 5:
            caller.msg("Attribute value must be between 1 and 5.")
        elif value - current_value > remaining_points:
            caller.msg(f"Not enough points. You have {remaining_points} points available.")
        else:
            caller.db.chargen['attributes'][category][attr] = value
            caller.msg(f"{attr} set to {value}")

        # Check if we've spent all points for this category
        if sum(caller.db.chargen['attributes'][category].values()) == total_points:
            # Move to the next category or finish if all are done
            categories = {'P': 'physical', 'S': 'social', 'M': 'mental'}
            current_index = priority.index(next(key for key, value in categories.items() if value == category))
            if current_index < len(priority) - 1:
                next_category = categories[priority[current_index + 1]]
                caller.msg(f"You've completed assigning {category} attributes. Moving to {next_category} attributes.")
            else:
                caller.msg("You've completed assigning all attribute points.")
                return "node_abilities"  # Move to abilities after completing attributes

    except ValueError:
        caller.msg("Invalid input. Format should be: <attribute> <value> (e.g., 'strength 3' or 'charisma 4')")

    return "assign_attribute_points"

def _modify_attribute(caller, raw_string, **kwargs):
    category = kwargs.get('category')
    attribute = kwargs.get('attribute')
    points = kwargs.get('points')
    
    if not all([category, attribute, points]):
        caller.msg("Error: Missing information for attribute modification.")
        return "node_attributes"
    
    caller.msg(f"Current value of {attribute}: {caller.db.chargen['attributes'][category][attribute]}")
    caller.msg(f"Enter new value for {attribute} (1-5):")
    
    # Return None to wait for user input, then process it with _set_attribute
    return None, {"node": (_set_attribute, {"category": category, "attribute": attribute, "points": points})}

def _set_attribute(caller, raw_string, **kwargs):
    category = kwargs.get('category')
    attribute = kwargs.get('attribute')
    points = kwargs.get('points')
    
    if not all([category, attribute, points]):
        caller.msg("Error: Missing information for setting attribute.")
        return "node_attributes"
    
    try:
        value = int(raw_string)
        if 1 <= value <= 5:
            current = caller.db.chargen['attributes'][category][attribute]
            total = sum(caller.db.chargen['attributes'][category].values())
            if total - current + value <= points:
                caller.db.chargen['attributes'][category][attribute] = value
                caller.msg(f"{attribute} set to {value}")
            else:
                caller.msg("Not enough points available.")
        else:
            caller.msg("Value must be between 1 and 5.")
    except ValueError:
        caller.msg("Please enter a number.")
    
    # Return to the attribute assignment menu
    return _assign_attributes(caller, category, points)

def _get_remaining_points(caller, category, priority):
    total_points = {"primary": 7, "secondary": 5, "tertiary": 3}[priority]
    used_points = sum(caller.db.chargen['attributes'][category].values())
    return total_points - used_points + 3  # +3 because each attribute starts at 1

def node_abilities(caller):
    text = "Choose the priority for your character's Abilities. You will have:\n"
    text += "Primary: 13 points\n"
    text += "Secondary: 9 points\n"
    text += "Tertiary: 5 points\n"
    
    options = [
        {"key": "1", "desc": "TSK (Talents, Skills, Knowledges)", "goto": (_set_ability_priority, {"priority": "TSK"})},
        {"key": "2", "desc": "TKS (Talents, Knowledges, Skills)", "goto": (_set_ability_priority, {"priority": "TKS"})},
        {"key": "3", "desc": "STK (Skills, Talents, Knowledges)", "goto": (_set_ability_priority, {"priority": "STK"})},
        {"key": "4", "desc": "SKT (Skills, Knowledges, Talents)", "goto": (_set_ability_priority, {"priority": "SKT"})},
        {"key": "5", "desc": "KTS (Knowledges, Talents, Skills)", "goto": (_set_ability_priority, {"priority": "KTS"})},
        {"key": "6", "desc": "KST (Knowledges, Skills, Talents)", "goto": (_set_ability_priority, {"priority": "KST"})},
        {"key": "0", "desc": "Return to main menu", "goto": "node_start"},
    ]
    return text, options

def _set_ability_priority(caller, raw_string, **kwargs):
    priority = kwargs.get('priority')
    if priority:
        caller.db.chargen["ability_priority"] = priority
        caller.msg(f"Ability priority set to: {priority}")
    else:
        caller.msg("Error: No priority specified.")
    return "assign_abilities"

def assign_abilities(caller):
    if "abilities" not in caller.db.chargen:
        caller.db.chargen["abilities"] = {
            "talents": {},
            "skills": {},
            "knowledges": {}
        }
    
    priority = caller.db.chargen.get("ability_priority")
    if not priority:
        caller.msg("You must set ability priorities before assigning points.")
        return "node_abilities"
    
    points = {"primary": 13, "secondary": 9, "tertiary": 5}
    categories = {"T": "talents", "S": "skills", "K": "knowledges"}
    
    # Determine which category we're currently assigning
    for i, cat in enumerate(priority):
        category = categories[cat]
        current_points = points[["primary", "secondary", "tertiary"][i]]
        if sum(caller.db.chargen['abilities'][category].values()) < current_points:
            break
    else:
        # If we've completed all categories, move to the next step
        caller.msg("You've completed assigning all ability points.")
        return "node_disciplines"  # Or whatever the next step in your chargen process is
    
    text = f"Assign points to {category.capitalize()}. You have {current_points} points to spend.\n"
    text += "Format: <ability> <value> (e.g., 'alertness 3' or 'brawl 2')\n"
    
    abilities = Stat.objects.filter(category="abilities", stat_type=category[:-1])  # Remove 's' from end
    for ability in abilities:
        value = caller.db.chargen['abilities'][category].get(ability.name, 0)
        text += f"{ability.name}: {value}\n"
    
    options = [
        {"key": "_default", "goto": (_process_ability_input, {"category": category, "points": current_points, "priority": priority})}
    ]
    options.append({"key": "0", "desc": "Return to abilities menu", "goto": "node_abilities"})
    
    return text, options

def _process_ability_input(caller, raw_string, **kwargs):
    category = kwargs.get('category')
    points = kwargs.get('points')
    priority = kwargs.get('priority')
    
    try:
        ability, value = raw_string.rsplit(None, 1)
        ability = ability.lower()  # Convert to lowercase for case-insensitive matching
        value = int(value)

        # Fetch abilities from Stat model
        abilities = Stat.objects.filter(category="abilities", stat_type=category[:-1])
        ability_map = {ab.name.lower(): ab.name for ab in abilities}

        if ability not in ability_map:
            caller.msg(f"Unknown ability: {ability}. Valid abilities are: {', '.join(ability_map.values())}")
            return "assign_abilities"

        # Use the correctly cased ability name
        ability = ability_map[ability]

        current = caller.db.chargen['abilities'][category].get(ability, 0)
        used_points = sum(caller.db.chargen['abilities'][category].values())
        remaining_points = points - used_points + current  # Add back the current value
        
        if value < 0 or value > 5:
            caller.msg("Ability value must be between 0 and 5.")
        elif value - current > remaining_points:
            caller.msg(f"Not enough points. You have {remaining_points} points available.")
        else:
            caller.db.chargen['abilities'][category][ability] = value
            caller.msg(f"{ability} set to {value}")
        
        # Check if we've spent all points for this category
        if sum(caller.db.chargen['abilities'][category].values()) == points:
            categories = {"T": "talents", "S": "skills", "K": "knowledges"}
            current_category = next((key for key, value in categories.items() if value == category), None)
            if current_category:
                current_index = priority.index(current_category)
                if current_index < len(priority) - 1:
                    next_category = categories[priority[current_index + 1]]
                    caller.msg(f"You've completed assigning {category}. Moving to {next_category}.")
                    return "assign_abilities"
                else:
                    caller.msg("You've completed assigning all ability points.")
                    return "node_disciplines"  # Or whatever the next step in your chargen process is
            else:
                caller.msg("Error: Unknown category.")
                return "node_abilities"
    except ValueError as e:
        caller.msg(str(e))
        caller.msg("Please enter an ability name and a value (e.g., 'alertness 3' or 'brawl 2').")
    
    return "assign_abilities"

def get_clan_disciplines(clan):
    clan_disciplines = {
        "Lasombra": ["Obtenebration", "Dominate", "Potence"],
        "Ventrue": ["Fortitude", "Potence", "Presence"],
        "Toreador": ["Presence", "Celerity", "Auspex"],
        "Tzimisce": ["Animalism", "Auspex", "Vicissitude"],
        "Kiasyd": ["Mytherceria", "Obtenebrate", "Auspex"],
        "Tremere": ["Auspex", "Dominate", "Thaumaturgy"],
        "Salubri": ["Auspex", "Fortitude", "Valeren"],
        #Fill More Later
    }
    return clan_disciplines.get(clan, [])

def node_disciplines(caller):
    if "disciplines" not in caller.db.chargen:
        caller.db.chargen["disciplines"] = {}
    
    clan = caller.db.chargen.get("clan")
    clan_disciplines = get_clan_disciplines(clan)
    
    text = f"Choose your character's Disciplines. You have 3 points to distribute.\n"
    text += f"As a {clan}, you have access to: {', '.join(clan_disciplines)}\n"
    text += "Format: <discipline> <value> (e.g., 'obtenebration 2' or 'dominate 1')\n"
    
    for discipline in clan_disciplines:
        value = caller.db.chargen['disciplines'].get(discipline, 0)
        text += f"{discipline}: {value}\n"
    
    options = [
        {"key": "_default", "goto": (_assign_discipline_points, {"clan_disciplines": clan_disciplines})}
    ]
    options.append({"key": "0", "desc": "Return to main menu", "goto": "node_start"})
    
    return text, options


def _assign_discipline_points(caller, raw_string, **kwargs):
    clan_disciplines = kwargs.get('clan_disciplines', [])
    
    try:
        discipline, value = raw_string.rsplit(None, 1)
        discipline = discipline.capitalize()
        value = int(value)

        if discipline not in clan_disciplines:
            caller.msg(f"Invalid discipline: {discipline}. Your clan disciplines are: {', '.join(clan_disciplines)}")
            return "node_disciplines"

        current = caller.db.chargen['disciplines'].get(discipline, 0)
        used_points = sum(caller.db.chargen['disciplines'].values())
        remaining_points = 3 - used_points + current  # Add back the current value
        
        if value < 0 or value > 5:
            caller.msg("Discipline value must be between 0 and 5.")
        elif value - current > remaining_points:
            caller.msg(f"Not enough points. You have {remaining_points} points available.")
        else:
            caller.db.chargen['disciplines'][discipline] = value
            caller.msg(f"{discipline} set to {value}")
        
        # Check if we've spent all points
        if sum(caller.db.chargen['disciplines'].values()) == 3:
            caller.msg("You've completed assigning all discipline points.")
            return "node_backgrounds"  # Move to the next step
    except ValueError as e:
        caller.msg(str(e))
        caller.msg("Please enter a discipline name and a value (e.g., 'obtenebration 2' or 'dominate 1').")
    
    return "node_disciplines"

def node_backgrounds(caller):
    if "backgrounds" not in caller.db.chargen:
        caller.db.chargen["backgrounds"] = {}
    
    text = "Choose your character's Backgrounds. You have 5 points to distribute.\n"
    text += "Format: <background> <value> (e.g., 'allies 2' or 'resources 3')\n"
    
    backgrounds = Stat.objects.filter(category="backgrounds", stat_type="background")
    for background in backgrounds:
        value = caller.db.chargen['backgrounds'].get(background.name, 0)
        text += f"{background.name}: {value}\n"
    
    options = [
        {"key": "_default", "goto": (_process_background_input, {"backgrounds": [b.name for b in backgrounds]})}
    ]
    options.append({"key": "0", "desc": "Return to main menu", "goto": "node_start"})
    
    return text, options

def _process_background_input(caller, raw_string, **kwargs):
    backgrounds = kwargs.get('backgrounds', [])
    
    try:
        background, value = raw_string.rsplit(None, 1)
        background = background.capitalize()
        value = int(value)

        if background not in backgrounds:
            caller.msg(f"Invalid background: {background}. Valid backgrounds are: {', '.join(backgrounds)}")
            return "node_backgrounds"

        current = caller.db.chargen['backgrounds'].get(background, 0)
        used_points = sum(caller.db.chargen['backgrounds'].values())
        remaining_points = 5 - used_points + current  # Add back the current value
        
        if value < 0 or value > 5:
            caller.msg("Background value must be between 0 and 5.")
        elif value - current > remaining_points:
            caller.msg(f"Not enough points. You have {remaining_points} points available.")
        else:
            caller.db.chargen['backgrounds'][background] = value
            caller.msg(f"{background} set to {value}")
        
        # Check if we've spent all points
        if sum(caller.db.chargen['backgrounds'].values()) == 5:
            caller.msg("You've completed assigning all background points.")
            return "node_review"  # Move to the review step
    except ValueError as e:
        caller.msg(str(e))
        caller.msg("Please enter a background name and a value (e.g., 'allies 2' or 'resources 3').")
    
    return "node_backgrounds"

def _assign_background_points(caller, raw_string, background):
    try:
        points = int(raw_string)
        current = caller.db.chargen['backgrounds'].get(background, 0)
        remaining = 5 - sum(caller.db.chargen['backgrounds'].values())
        
        if points < 0 or points > remaining + current:
            caller.msg("Invalid number of points.")
        else:
            caller.db.chargen['backgrounds'][background] = points
            caller.msg(f"{background} set to {points}")
    except ValueError:
        caller.msg("Please enter a number.")
    
    return "node_backgrounds"

def node_review(caller):
    text = "Review your character:\n\n"
    text += f"Concept: {caller.db.chargen.get('concept', 'Not set')}\n"
    text += f"Nature: {caller.db.chargen.get('nature', 'Not set')}\n"
    text += f"Demeanor: {caller.db.chargen.get('demeanor', 'Not set')}\n"
    text += f"Clan: {caller.db.chargen.get('clan', 'Not set')}\n\n"

    text += "Attributes:\n"
    for category in ['physical', 'social', 'mental']:
        text += f"  {category.capitalize()}:\n"
        for attr, value in caller.db.chargen.get('attributes', {}).get(category, {}).items():
            text += f"    {attr}: {value}\n"

    text += "\nAbilities:\n"
    for category in ['talents', 'skills', 'knowledges']:
        text += f"  {category.capitalize()}:\n"
        for ability, value in caller.db.chargen.get('abilities', {}).get(category, {}).items():
            text += f"    {ability}: {value}\n"

    text += "\nDisciplines:\n"
    for discipline, value in caller.db.chargen.get('disciplines', {}).items():
        text += f"  {discipline}: {value}\n"

    text += "\nBackgrounds:\n"
    for background, value in caller.db.chargen.get('backgrounds', {}).items():
        text += f"  {background}: {value}\n"

    text += "\nAre you satisfied with your character?"

    options = (
        {"key": "1", "desc": "Yes, complete character creation", "goto": "node_finish"},
        {"key": "2", "desc": "No, I want to make changes", "goto": "node_start"},
    )

    return text, options

def node_finish(caller):
    text = "Congratulations! Your character has been created. You can now enter the game world."
    caller.msg(text)
    
    # Apply all the chargen data to the character
    _apply_chargen_data(caller)
    
    # You might want to perform additional actions here, such as:
    # - Moving the character to a starting location
    # - Announcing the new character to the game
    # - Granting initial equipment or resources
    
    return None

def finish_chargen(self, caller, menu):
    """
    Called when character generation is complete.
    """
    caller.msg("Character generation complete!")
    # Additional logic to finalize character creation
    _apply_chargen_data(caller)

def _apply_chargen_data(caller):
    """Apply all chargen data to the character."""
    chargen_data = caller.db.chargen
    
    if not chargen_data:
        caller.msg("Error: No character generation data found.")
        return

    # Apply basic information
    caller.db.concept = chargen_data.get('concept', '')
    caller.db.nature = chargen_data.get('nature', '')
    caller.db.demeanor = chargen_data.get('demeanor', '')
    caller.db.clan = chargen_data.get('clan', '')

    # Apply attributes
    for category, attributes in chargen_data.get('attributes', {}).items():
        for attr, value in attributes.items():
            caller.set_stat(category, 'attribute', attr, value)

    # Apply abilities
    for category, abilities in chargen_data.get('abilities', {}).items():
        for ability, value in abilities.items():
            caller.set_stat(category, 'ability', ability, value)

    # Apply disciplines
    for discipline, value in chargen_data.get('disciplines', {}).items():
        caller.set_stat('powers', 'discipline', discipline, value)

    # Apply backgrounds
    for background, value in chargen_data.get('backgrounds', {}).items():
        caller.set_stat('backgrounds', 'background', background, value)

    # Clear chargen data
    caller.attributes.remove('chargen')

    # Set character as approved (you might want to change this if you have a manual approval process)
    caller.db.approved = True

    caller.msg("Your character has been fully created and is ready to play!")

# Add this function to your main CmdCharGen class
def at_post_cmd(self):
    """
    This hook is called after the command has finished executing 
    (after self.func()).
    """
    if hasattr(self.caller, "ndb._menutree"):
        self.caller.msg("|wUse 'look' to see the character creation menu again.")
        self.caller.msg("Use 'quit' to exit character creation.")