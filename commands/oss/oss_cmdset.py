from evennia import CmdSet
from commands.oss.oss_commands import (
    CmdShowHierarchy,
    CmdOssSetSector,
    CmdOssSetNeighborhood,
    CmdOssSetSite,
    CmdOssSetCurrentRoom,
    CmdOssSetDistrict,
    CmdSetResolve,
    CmdSetInfrastructure,
    CmdSetOrder,
    CmdInitializeHierarchy
)

class OSSCmdSet(CmdSet):
    """
    This CmdSet groups all the OSS (Open Source Simulation) commands together.
    """
    key = "OSS Commands"
    priority = 1

    def at_cmdset_creation(self):
        """
        Called once at creation. Populates the CmdSet with commands.
        """
        self.add(CmdShowHierarchy())
        self.add(CmdOssSetSector())
        self.add(CmdOssSetNeighborhood())
        self.add(CmdOssSetSite())
        self.add(CmdOssSetCurrentRoom())
        self.add(CmdOssSetDistrict())
        self.add(CmdSetResolve())
        self.add(CmdSetInfrastructure())
        self.add(CmdSetOrder())
        self.add(CmdInitializeHierarchy())