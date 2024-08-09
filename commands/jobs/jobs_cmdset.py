# jobsystem_cmdset.py

from evennia import CmdSet
from commands.jobs.jobs_commands import (
    CmdCreateJob, CmdAddParticipant, CmdClaimJob,
    CmdApproveJob, CmdRejectJob, CmdListJobs, CmdAttachObject,
    CmdRemoveObject, CmdCreateJobTemplate, CmdEditJobTemplate,
    CmdDeleteJobTemplate, CmdListQueues, CmdDeleteQueue, CmdEditQueue, CmdCreateQueue,
    CmdReassignJob, CmdViewQueueJobs, CmdViewJob
)

class JobSystemCmdSet(CmdSet):
    """
    Command set for job system-related commands.
    """
    key = "JobSystemCmdSet"
    priority = 1

    def at_cmdset_creation(self):
        """
        Populates the command set.
        """
        self.add(CmdCreateJob())
        self.add(CmdAddParticipant())
        self.add(CmdClaimJob())
        self.add(CmdApproveJob())
        self.add(CmdRejectJob())
        self.add(CmdListJobs())
        self.add(CmdAttachObject())
        self.add(CmdRemoveObject())
        self.add(CmdCreateJobTemplate())
        self.add(CmdEditJobTemplate())
        self.add(CmdDeleteJobTemplate())
        self.add(CmdListQueues())
        self.add(CmdDeleteQueue())
        self.add(CmdEditQueue())
        self.add(CmdCreateQueue())
        self.add(CmdReassignJob())
        self.add(CmdViewQueueJobs())
        self.add(CmdViewJob())
        
