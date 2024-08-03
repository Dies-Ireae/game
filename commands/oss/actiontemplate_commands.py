# commands/actiontemplate_commands.py

from evennia.commands.command import Command


class CmdCreateActionTemplate(Command):
    """
    Create a new action template.

    Usage:
      +createactiontemplate <name> = <downtime_cost>, <requires_target>, <description>

    Example:
      +createactiontemplate Attack = 4, True, Attacking an enemy asset.
    """

    key = "+createactiontemplate"
    locks = "cmd:all()"
    help_category = "ActionTemplates"

    def func(self):
        from world.wod20th.models import ActionTemplate
        try:
            name, details = self.args.split("=", 1)
            downtime_cost, requires_target, description = [item.strip() for item in details.split(",", 2)]
            action_template, created = ActionTemplate.objects.get_or_create(
                name=name.strip(),
                defaults={
                    'downtime_cost': int(downtime_cost),
                    'requires_target': requires_target.lower() in ['true', 'yes', '1'],
                    'description': description
                }
            )
            if created:
                self.caller.msg(f"Action Template '{action_template.name}' created successfully.")
            else:
                self.caller.msg(f"Action Template '{action_template.name}' already exists.")
        except ValueError:
            self.caller.msg("Invalid input. Please ensure downtime_cost is a number and requires_target is a boolean.")
        except Exception as e:
            self.caller.msg(f"Error creating action template: {e}")

class CmdReadActionTemplate(Command):
    """
    View details of an action template.

    Usage:
      +viewactiontemplate <name>

    Example:
      +viewactiontemplate Attack
    """

    key = "+viewactiontemplate"
    locks = "cmd:all()"
    help_category = "ActionTemplates"

    def func(self):
        from world.wod20th.models import ActionTemplate
        try:
            name = self.args.strip()
            template = ActionTemplate.objects.get(name__iexact=name)
            self.caller.msg(
                f"Action Template: {template.name}\n"
                f"Downtime Cost: {template.downtime_cost}\n"
                f"Requires Target: {template.requires_target}\n"
                f"Description: {template.description}"
            )
        except ActionTemplate.DoesNotExist:
            self.caller.msg("Action Template not found.")

class CmdUpdateActionTemplate(Command):
    """
    Update an action template.

    Usage:
      +updateactiontemplate <name> = <field>, <value>

    Example:
      +updateactiontemplate Attack = downtime_cost, 5
    """

    key = "+updateactiontemplate"
    locks = "cmd:all()"
    help_category = "ActionTemplates"

    def func(self):
        from world.wod20th.models import ActionTemplate
        try:
            name, updates = self.args.split("=", 1)
            field, value = [item.strip() for item in updates.split(",", 1)]
            template = ActionTemplate.objects.get(name__iexact=name.strip())

            if field == 'downtime_cost':
                value = int(value)
            elif field == 'requires_target':
                value = value.lower() in ['true', 'yes', '1']

            setattr(template, field, value)
            template.save()
            self.caller.msg(f"Action Template '{template.name}' updated successfully.")
        except ActionTemplate.DoesNotExist:
            self.caller.msg("Action Template not found.")
        except ValueError:
            self.caller.msg("Invalid input. Ensure that downtime_cost is a number and requires_target is a boolean.")
        except Exception as e:
            self.caller.msg(f"Error updating action template: {e}")

class CmdDeleteActionTemplate(Command):
    """
    Delete an action template.

    Usage:
      +deleteactiontemplate <name>

    Example:
      +deleteactiontemplate Attack
    """

    key = "+deleteactiontemplate"
    locks = "cmd:all()"
    help_category = "ActionTemplates"

    def func(self):
        from world.wod20th.models import ActionTemplate
        try:
            name = self.args.strip()
            template = ActionTemplate.objects.get(name__iexact=name)
            template.delete()
            self.caller.msg(f"Action Template '{template.name}' deleted successfully.")
        except ActionTemplate.DoesNotExist:
            self.caller.msg("Action Template not found.")
