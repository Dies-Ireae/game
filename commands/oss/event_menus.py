from evennia.utils.evmenu import EvMenu
from evennia.utils import create
from world.oss.models import OSSEvent, Outcome, Task, Neighborhood, Site

# Start Menu for Creating or Editing an Event
def start_event_menu(caller, event=None):
    if event:
        text = f"Editing Event '{event.name}'. What would you like to do?"
    else:
        text = "Welcome to the Event Creation Menu. Let's create a new event."
    
    options = [
        {"desc": "Set Event Name", "goto": ("set_event_name", {"event": event})},
        {"desc": "Select Neighborhoods", "goto": ("select_neighborhoods", {"event": event})},
        {"desc": "Select Sites", "goto": ("select_sites", {"event": event})},
        {"desc": "Manage Outcomes", "goto": ("manage_outcomes", {"event": event})},
        {"desc": "Finish", "goto": "menu_finish"},
        {"desc": "Cancel", "goto": "menu_cancel"},
    ]
    if event:
        options.insert(0, {"desc": f"Current Event: {event.name}", "goto": "no_op"})
    return text, options

def no_op(caller):
    return "start_event_menu"

def set_event_name(caller, raw_string, **kwargs):
    event = kwargs.get("event")
    if event:
        event.name = raw_string.strip()
        event.save()
        caller.msg(f"Event renamed to '{event.name}' successfully!")
    else:
        event_name = raw_string.strip()
        event = create.create_object(Event, key=event_name)
        caller.msg(f"Event '{event_name}' created successfully!")
    
    return "start_event_menu", {"event": event}

def select_neighborhoods(caller, raw_string, **kwargs):
    event = kwargs.get("event")
    neighborhoods = Neighborhood.objects.all()
    text = f"Select the Neighborhoods involved in this Event:\n"
    for i, neighborhood in enumerate(neighborhoods):
        text += f"{i + 1}. {neighborhood.name} {'[Selected]' if event and neighborhood in event.neighborhoods.all() else ''}\n"
    options = [{"key": str(i + 1), "goto": ("toggle_neighborhood", {"event": event, "neighborhood_index": i})} for i in range(len(neighborhoods))]
    options.append({"desc": "Back", "goto": "start_event_menu", "args": {"event": event}})
    return text, options

def toggle_neighborhood(caller, raw_string, **kwargs):
    event = kwargs.get("event")
    neighborhood_index = int(kwargs["neighborhood_index"])
    neighborhood = Neighborhood.objects.all()[neighborhood_index]
    if neighborhood in event.neighborhoods.all():
        event.neighborhoods.remove(neighborhood)
        caller.msg(f"Neighborhood '{neighborhood.name}' removed from Event.")
    else:
        event.neighborhoods.add(neighborhood)
        caller.msg(f"Neighborhood '{neighborhood.name}' added to Event.")
    event.save()
    return "select_neighborhoods", {"event": event}

def select_sites(caller, raw_string, **kwargs):
    event = kwargs.get("event")
    sites = Site.objects.all()
    text = f"Select the Sites involved in this Event:\n"
    for i, site in enumerate(sites):
        text += f"{i + 1}. {site.name} {'[Selected]' if event and site in event.sites.all() else ''}\n"
    options = [{"key": str(i + 1), "goto": ("toggle_site", {"event": event, "site_index": i})} for i in range(len(sites))]
    options.append({"desc": "Back", "goto": "start_event_menu", "args": {"event": event}})
    return text, options

def toggle_site(caller, raw_string, **kwargs):
    event = kwargs.get("event")
    site_index = int(kwargs["site_index"])
    site = Site.objects.all()[site_index]
    if site in event.sites.all():
        event.sites.remove(site)
        caller.msg(f"Site '{site.name}' removed from Event.")
    else:
        event.sites.add(site)
        caller.msg(f"Site '{site.name}' added to Event.")
    event.save()
    return "select_sites", {"event": event}

def manage_outcomes(caller, raw_string, **kwargs):
    event = kwargs.get("event")
    outcomes = event.outcomes.all() if event else []
    text = f"Manage Outcomes for Event '{event.name}':\n"
    for i, outcome in enumerate(outcomes):
        text += f"{i + 1}. {outcome.name}\n"
    options = [
        {"desc": "Add New Outcome", "goto": ("create_outcome", {"event": event})},
        {"desc": "Edit Outcome", "goto": ("edit_outcome", {"event": event})} if outcomes else None,
        {"desc": "Back", "goto": ("start_event_menu", {"event": event})},
    ]
    return text, options

def create_outcome(caller, raw_string, **kwargs):
    event = kwargs.get("event")
    text = "Please enter the name of the new Outcome:"
    options = {"key": "_default", "goto": ("set_outcome_name", {"event": event})}
    return text, options

def set_outcome_name(caller, raw_string, **kwargs):
    event = kwargs.get("event")
    outcome_name = raw_string.strip()
    outcome = create.create_object(Outcome, key=outcome_name)
    event.outcomes.add(outcome)
    event.save()
    caller.msg(f"Outcome '{outcome_name}' created successfully and added to Event '{event.name}'!")
    return "edit_outcome", {"outcome": outcome, "event": event}

def edit_outcome(caller, raw_string, **kwargs):
    event = kwargs.get("event")
    outcome_index = int(raw_string.strip()) - 1
    outcome = event.outcomes.all()[outcome_index]
    return "outcome_menu", {"outcome": outcome, "event": event}

def outcome_menu(caller, raw_string, **kwargs):
    outcome = kwargs.get("outcome")
    event = kwargs.get("event")
    text = f"Editing Outcome '{outcome.name}':"
    options = [
        {"desc": "Set Outcome Description", "goto": ("set_outcome_description", {"outcome": outcome, "event": event})},
        {"desc": "Add Effects", "goto": ("add_effects", {"outcome": outcome, "event": event})},
        {"desc": "Add Tasks", "goto": ("add_tasks", {"outcome": outcome, "event": event})},
        {"desc": "Back", "goto": ("manage_outcomes", {"event": event})},
    ]
    return text, options

def set_outcome_description(caller, raw_string, **kwargs):
    outcome = kwargs.get("outcome")
    outcome.description = raw_string.strip()
    outcome.save()
    caller.msg(f"Description set for Outcome '{outcome.name}'.")
    return "outcome_menu", {"outcome": outcome, "event": kwargs.get("event")}

def add_effects(caller, raw_string, **kwargs):
    outcome = kwargs.get("outcome")
    effects = Outcome.list_effects()
    text = f"Select Effects to add to Outcome '{outcome.name}':\n"
    for i, effect in enumerate(effects):
        text += f"{i + 1}. {effect} {'[Added]' if effect in outcome.effects else ''}\n"
    options = [{"key": str(i + 1), "goto": ("toggle_effect", {"outcome": outcome, "effect": effect})} for i, effect in enumerate(effects)]
    return text, options

def toggle_effect(caller, raw_string, **kwargs):
    outcome = kwargs.get("outcome")
    effect = kwargs.get("effect")
    if effect in outcome.effects:
        outcome.remove_effect(effect)
        caller.msg(f"Effect '{effect}' removed from Outcome '{outcome.name}'.")
    else:
        outcome.add_effect(effect)
        caller.msg(f"Effect '{effect}' added to Outcome '{outcome.name}'.")
    outcome.save()
    return "add_effects", {"outcome": outcome, "event": kwargs.get("event")}

def add_tasks(caller, raw_string, **kwargs):
    outcome = kwargs.get("outcome")
    tasks = Task.objects.all()
    text = f"Select Tasks to add to Outcome '{outcome.name}':\n"
    for i, task in enumerate(tasks):
        text += f"{i + 1}. {task.name} {'[Added]' if task in outcome.tasks.all() else ''}\n"
    options = [{"key": str(i + 1), "goto": ("toggle_task", {"outcome": outcome, "task_index": i})} for i in range(len(tasks))]
    return text, options

def toggle_task(caller, raw_string, **kwargs):
    outcome = kwargs.get("outcome")
    task_index = int(kwargs["task_index"])
    task = Task.objects.all()[task_index]
    if task in outcome.tasks.all():
        outcome.tasks.remove(task)
        caller.msg(f"Task '{task.name}' removed from Outcome '{outcome.name}'.")
    else:
        outcome.tasks.add(task)
        caller.msg(f"Task '{task.name}' added to Outcome '{outcome.name}'.")
    outcome.save()
    return "add_tasks", {"outcome": outcome, "event": kwargs.get("event")}

def menu_finish(caller, raw_string=None, **kwargs):
    event = kwargs.get("event")
    if event:
        caller.msg(f"Event '{event.name}' has been successfully completed.")
    else:
        caller.msg("No event was created.")
    return

def menu_cancel(caller):
    caller.msg("Operation canceled.")
    return