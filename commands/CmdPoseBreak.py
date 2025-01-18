from evennia import default_cmds

class CmdPoseBreak(default_cmds.MuxCommand):
    """
    Toggle pose breaks on/off.

    Usage:
      +posebreak
      +posebreak/on
      +posebreak/off

    Toggles whether you see pose breaks between poses.
    The default is on. Use /on or /off to explicitly set the state,
    or use without a switch to toggle.
    """

    key = "+posebreak"
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        """Execute command"""
        caller = self.caller
        
        # Get current state, default to True if not set
        current_state = caller.db.show_pose_breaks
        if current_state is None:
            current_state = True
            caller.db.show_pose_breaks = True

        if "on" in self.switches:
            caller.db.show_pose_breaks = True
            caller.msg("Pose breaks turned on.")
        elif "off" in self.switches:
            caller.db.show_pose_breaks = False
            caller.msg("Pose breaks turned off.")
        else:
            # Toggle current state
            caller.db.show_pose_breaks = not current_state
            state = "on" if caller.db.show_pose_breaks else "off"
            caller.msg(f"Pose breaks turned {state}.")