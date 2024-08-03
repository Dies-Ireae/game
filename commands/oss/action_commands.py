# commands/action_commands.py

from evennia.commands.command import Command


class CmdTakeAction(Command):
    """
    Take an action using an action template.

    Usage:
      +takeaction <template_name> = <target_asset_name>, <downtime_spent>

    Example:
      +takeaction Attack = Gold Mine, 4
    """

    key = "+takeaction"
    locks = "cmd:all()"
    help_category = "Actions"

    def func(self):
        from world.wod20th.models import Action, ActionTemplate, Asset
        try:
            template_name, details = self.args.split("=", 1)
            target_asset_name, downtime_spent = [item.strip() for item in details.split(",", 1)]
            template = ActionTemplate.objects.get(name__iexact=template_name.strip())

            # Convert downtime_spent to integer and validate
            downtime_spent = int(downtime_spent)
            if downtime_spent <= 0:
                self.caller.msg("Downtime spent must be a positive number.")
                return

            # Check if target is required or not
            target_asset = None
            if template.requires_target:
                target_asset = Asset.objects.get(name__iexact=target_asset_name.strip())
            elif target_asset_name:
                self.caller.msg("This action does not require a target.")
                return

            if self.caller.db.downtime_hours < downtime_spent:
                self.caller.msg("You do not have enough downtime hours for this action.")
                return

            # Create the action
            action = Action.objects.create(
                template=template,
                character=self.caller,
                target_asset=target_asset,
                downtime_spent=downtime_spent
            )
            action.perform_action()
            self.caller.msg(f"Action '{template.name}' taken against {target_asset.name if target_asset else 'N/A'}.")
        except ActionTemplate.DoesNotExist:
            self.caller.msg("Action Template not found.")
        except Asset.DoesNotExist:
            self.caller.msg("Target Asset not found.")
        except ValueError:
            self.caller.msg("Invalid input. Please check your parameters.")
        except Exception as e:
            self.caller.msg(f"Error taking action: {e}")
