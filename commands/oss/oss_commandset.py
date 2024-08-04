# mygame/commands/oss/oss_commandset.py

from evennia.commands.cmdset import CmdSet
from commands.oss.asset_commands import (
    CmdSearchAssets, CmdReadAsset, CmdUpdateAsset, CmdDeleteAsset,
    CmdCreateAsset, CmdTransferAsset, CmdAssets
)
from commands.oss.action_commands import (
    CmdCreateActionTemplate, CmdReadActionTemplate, CmdUpdateActionTemplate,
    CmdDeleteActionTemplate, CmdSearchActionTemplates, CmdListActionTemplates, CmdTakeAction, CmdRefreshDowntime, CmdListDowntime
)

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
        self.add(CmdCreateAsset())
        self.add(CmdAssets())
        self.add(CmdTransferAsset())
        self.add(CmdSearchAssets())
        self.add(CmdReadAsset())
        self.add(CmdUpdateAsset())
        self.add(CmdDeleteAsset())

        # ActionTemplate commands
        self.add(CmdCreateActionTemplate())
        self.add(CmdReadActionTemplate())
        self.add(CmdUpdateActionTemplate())
        self.add(CmdDeleteActionTemplate())
        self.add(CmdSearchActionTemplates())
        self.add(CmdListActionTemplates())

        # Action-taking command
        self.add(CmdTakeAction())

        # OSS Global Commands
        self.add(CmdRefreshDowntime())
        self.add(CmdListDowntime())