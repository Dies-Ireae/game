from evennia import default_cmds
import re

class PoseBreakMixin:
    """
    A mixin to add pose breaks before commands.
    """
    def send_pose_break(self, exclude=None):
        caller = self.caller
        pose_break = f"\n|y{'=' * 30}> |w{caller.name}|n |y<{'=' * 30}|n"
        
        # Filter receivers based on Umbra state
        filtered_receivers = [
            obj for obj in caller.location.contents
            if obj.has_account and obj.db.in_umbra == caller.db.in_umbra
        ]
        
        for receiver in filtered_receivers:
            if receiver != caller and (not exclude or receiver not in exclude):
                receiver.msg(pose_break)
        
        # Always send the pose break to the caller
        caller.msg(pose_break)

    def msg_contents(self, message, exclude=None, from_obj=None, **kwargs):
        """
        Custom msg_contents that adds a pose break before the message.
        """
        # Add the pose break
        self.send_pose_break(exclude=exclude)

        # Call the original msg_contents (pose/emit/say)
        super().msg_contents(message, exclude=exclude, from_obj=from_obj, **kwargs)

class CmdPose(PoseBreakMixin, default_cmds.MuxCommand):
    """
    Pose an action to the room, with support for mixed content and language tags.
    Usage:
      :pose text
      ;pose text
      pose text

    Use "~text" for language-tagged speech.
    
    Example:
      :waves and says "~Hello!" in French, then "Hello" in English.
      ;grins and whispers, "~We meet again!"
      pose This is a regular pose with "~tagged speech" and "untagged speech".
    """

    key = "pose"
    aliases = [";", ":"]
    locks = "cmd:all()"
    arg_regex = None

    def parse(self):
        """
        Custom parsing to handle different pose prefixes.
        """
        super().parse()
        
        if self.cmdstring == ":":
            # Add a space after colon if not present
            self.args = " " + self.args.lstrip()
        elif self.cmdstring == ";":
            # Remove space after semicolon if present
            self.args = self.args.lstrip()

    def process_special_characters(self, message):
        """
        Process %r and %t in the message, replacing them with appropriate ANSI codes.
        """
        message = message.replace('%r', '|/').replace('%t', '|-')
        return message

    def func(self):
        "Perform the pose"
        caller = self.caller
        if not self.args:
            caller.msg("Pose what?")
            return

        # Send pose break before processing the message
        self.send_pose_break()

        # Process special characters in the message
        processed_args = self.process_special_characters(self.args)

        # Determine the name to use
        poser_name = caller.attributes.get('gradient_name', default=caller.key)

        # Get the character's speaking language
        speaking_language = caller.get_speaking_language()

        # Filter receivers based on Umbra state
        filtered_receivers = [
            obj for obj in caller.location.contents
            if obj.has_account and obj.db.in_umbra == caller.db.in_umbra
        ]

        # Construct the pose message
        pose_message = f"{poser_name} {processed_args}"

        # Send the pose to filtered receivers
        for receiver in filtered_receivers:
            receiver.msg(pose_message)

