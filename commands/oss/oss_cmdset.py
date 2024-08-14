from evennia import CmdSet
from commands.oss.oss_commands import CmdCreateDistrict, CmdCreateSector, CmdCreateNeighborhood, CmdCreateSite, CmdCreateEvent, CmdEditEvent, CmdShowHierarchy

class OSSCmdSet(CmdSet):
    """
    Command set containing building-related commands specifically for
    off-screen systems (OSS).
    """
    key = "OssCmdSet"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdCreateDistrict())
        self.add(CmdCreateSector())
        self.add(CmdCreateNeighborhood())
        self.add(CmdCreateSite())
        self.add(CmdCreateEvent())
        self.add(CmdEditEvent())
        self.add(CmdShowHierarchy())
