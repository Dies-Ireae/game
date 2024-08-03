# mygame/commands/oss/oss_commandset.py

from evennia.commands.cmdset import CmdSet
from commands.oss.asset_commands import CmdSearchAssets, CmdReadAsset, CmdUpdateAsset, CmdDeleteAsset
from commands.oss.actiontemplate_commands import CmdCreateActionTemplate, CmdReadActionTemplate, CmdUpdateActionTemplate, CmdDeleteActionTemplate
from commands.oss.action_commands import CmdTakeAction

class OssCmdSet(CmdSet):
    """
    This groups the commands related to the off-screen system (OSS).
    """
    key = "OssCmdSet"

    def at_cmdset_creation(self):
        """
        Populates the CmdSet with commands.
        """
        # Asset commands
        self.add(CmdSearchAssets())
        self.add(CmdReadAsset())
        self.add(CmdUpdateAsset())
        self.add(CmdDeleteAsset())

        # ActionTemplate commands
        self.add(CmdCreateActionTemplate())
        self.add(CmdReadActionTemplate())
        self.add(CmdUpdateActionTemplate())
        self.add(CmdDeleteActionTemplate())

        # Action commands
        self.add(CmdTakeAction())

