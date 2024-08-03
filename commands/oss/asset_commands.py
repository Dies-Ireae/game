# commands/asset_commands.py

from evennia.commands.command import Command


class CmdSearchAssets(Command):
    """
    Search for assets to target.

    Usage:
      +searchassets <query>

    Example:
      +searchassets Gold Mine
    """

    key = "+searchassets"
    locks = "cmd:all()"
    help_category = "Assets"

    def func(self):
        from world.wod20th.models import Asset
        query = self.args.strip().lower()
        results = Asset.objects.filter(name__icontains=query)
        if results.exists():
            message = "Found the following assets:\n"
            for asset in results:
                message += f"{asset.id}. {asset.name} (Type: {asset.get_asset_type_display()})\n"
            self.caller.msg(message)
        else:
            self.caller.msg("No assets found matching your query.")

class CmdReadAsset(Command):
    """
    View details of an asset.

    Usage:
      +viewasset <asset_name>

    Example:
      +viewasset Gold Mine
    """

    key = "+viewasset"
    locks = "cmd:all()"
    help_category = "Assets"

    def func(self):
        from world.wod20th.models import Asset
        try:
            asset_name = self.args.strip()
            asset = Asset.objects.get(name__iexact=asset_name)
            self.caller.msg(
                f"Asset: {asset.name}\n"
                f"Type: {asset.get_asset_type_display()}\n"
                f"Value: {asset.value}\n"
                f"Description: {asset.description}\n"
                f"Owner: {asset.owner}\n"
                f"Status: {asset.status}\n"
                f"Traits: {asset.traits}"
            )
        except Asset.DoesNotExist:
            self.caller.msg("Asset not found.")

class CmdUpdateAsset(Command):
    """
    Update an asset.

    Usage:
      +updateasset <asset_name> = <field>, <value>

    Example:
      +updateasset Gold Mine = value, 10
    """

    key = "+updateasset"
    locks = "cmd:all()"
    help_category = "Assets"

    def func(self):
        from world.wod20th.models import Asset
        try:
            asset_name, updates = self.args.split("=", 1)
            field, value = [item.strip() for item in updates.split(",", 1)]
            asset = Asset.objects.get(name__iexact=asset_name.strip())

            # Handle specific field types
            if field == 'value':
                value = int(value)

            setattr(asset, field, value)
            asset.save()
            self.caller.msg(f"Asset '{asset.name}' updated successfully.")
        except Asset.DoesNotExist:
            self.caller.msg("Asset not found.")
        except ValueError:
            self.caller.msg("Invalid value type. Please ensure you are entering the correct data type.")
        except Exception as e:
            self.caller.msg(f"Error updating asset: {e}")

class CmdDeleteAsset(Command):
    """
    Delete an asset.

    Usage:
      +deleteasset <asset_name>

    Example:
      +deleteasset Gold Mine
    """

    key = "+deleteasset"
    locks = "cmd:all()"
    help_category = "Assets"

    def func(self):
        from world.wod20th.models import Asset
        try:
            asset_name = self.args.strip()
            asset = Asset.objects.get(name__iexact=asset_name)
            asset.delete()
            self.caller.msg(f"Asset '{asset.name}' deleted successfully.")
        except Asset.DoesNotExist:
            self.caller.msg("Asset not found.")
