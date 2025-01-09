from evennia import default_cmds
from evennia.utils import ansi
from commands.CmdPose import PoseBreakMixin
from evennia.utils.search import search_object
import re

class EmitBaseMixin:
    """Mixin class for shared emit functionality"""
    
    def process_special_characters(self, message):
        """
        Process %r and %t in the message, replacing them with appropriate ANSI codes.
        """
        message = message.replace('%r', '|/').replace('%t', '|-')
        return message

class CmdPemit(EmitBaseMixin, PoseBreakMixin, default_cmds.MuxCommand):
    """
    pemit - Send a private emit to specific player(s).

    Usage:
      pemit <player(s)>=<message>
      pemit/language <player(s)>=<message>

    Switches:
      /language - Use this to emit a message in your character's set language.

    Examples:
      pemit Bob=You feel a chill run down your spine.
      pemit Bob,Alice=A strange sensation washes over you.
      pemit/language Bob="~Je suis là!" whispers in your ear in French.

    This command sends a message only to the specified player(s).
    Other players in the room will not see the message.
    Use quotes with a leading tilde (~) for speech in your set language.
    """

    key = "pemit"
    aliases = ["@pemit"]
    locks = "cmd:perm(all)"
    help_category = "Storytelling"

    def func(self):
        """Execute the pemit command"""
        caller = self.caller

        if not self.args or "=" not in self.args:
            caller.msg("Usage: pemit <player(s)>=<message>")
            return

        targets, message = self.args.split("=", 1)
        targets = [target.strip() for target in targets.split(",")]
        message = message.strip()

        if not message or not targets:
            caller.msg("You must specify both target(s) and a message.")
            return

        # Process special characters in the message
        processed_message = self.process_special_characters(message)

        # Find all target players globally
        found_targets = []
        for target_name in targets:
            target = caller.search(target_name, global_search=True)
            if target:
                found_targets.append(target)

        if not found_targets:
            return

        # Send pose break before the message if enabled
        self.send_pose_break(exclude=found_targets)  # Exclude targets from room pose break

        # Check if the language switch is used
        use_language = 'language' in self.switches

        if use_language:
            # Handle language-specific emit
            speaking_language = caller.get_speaking_language()
            for target in found_targets:
                if speaking_language and speaking_language in target.get_languages():
                    target.msg(processed_message)
                else:
                    # Send garbled version if they don't know the language
                    target.msg(self.garble_language(processed_message))
        else:
            # Send the message to all target players
            for target in found_targets:
                target.msg(processed_message)

        # Confirm to the caller
        target_names = ", ".join(target.get_display_name(caller) for target in found_targets)
        caller.msg(f"You pemit to {target_names}: {processed_message}")

    def garble_language(self, message):
        """Create a 'garbled' version of the message for those who don't know the language"""
        # This is a simple implementation - you might want to make this more sophisticated
        return "You hear words in a language you don't understand."

class CmdRemit(EmitBaseMixin, PoseBreakMixin, default_cmds.MuxCommand):
    """
    remit - Send a message to another room.

    Usage:
      remit <room>=<message>
      remit/language <room>=<message>

    Switches:
      /language - Use this to emit a message in your character's set language.

    Examples:
      remit #123=A cool breeze blows through the room.
      remit Hotel California="~Bonjour, mes amis!" A voice calls out in French.
      remit/language Garden=The entire message is in the set language.

    This command allows you to emit a message to a room you're not currently in.
    You must have the appropriate permissions to emit to the target room.
    Use quotes with a leading tilde (~) for speech in your set language.
    """

    key = "remit"
    aliases = ["@remit"]
    locks = "cmd:perm(all)"
    help_category = "Storytelling"

    def func(self):
        """Execute the remit command"""
        caller = self.caller

        if not self.args or "=" not in self.args:
            caller.msg("Usage: remit <room>=<message>")
            return

        room, message = self.args.split("=", 1)
        room = room.strip()
        message = message.strip()

        if not message:
            caller.msg("What do you want to emit?")
            return

        # Handle dbref format (#2)
        if room.startswith("#"):
            try:
                dbref = int(room[1:])
                target = search_object(f"#{dbref}")
                if target:
                    target = target[0]
            except ValueError:
                target = None
        else:
            # Search by name globally
            target = search_object(room)
            if target:
                # If multiple matches, try to find an exact match first
                exact_matches = [obj for obj in target if obj.key.lower() == room.lower()]
                if exact_matches:
                    target = exact_matches[0]
                else:
                    target = target[0]
            else:
                target = None

        if not target:
            caller.msg(f"Could not find room '{room}'.")
            return

        # Verify it's a room - check both base Room and any custom room typeclasses
        if not (target.is_typeclass("evennia.objects.objects.DefaultRoom") or 
                target.is_typeclass("typeclasses.rooms.Room") or
                hasattr(target, "destination")):  # Check if it has room-like properties
            caller.msg("You can only remit to rooms.")
            return

        # Process special characters in the message
        processed_message = self.process_special_characters(message)

        # Send pose break before the message if enabled
        # Note: We send pose break to the target room's occupants
        if target and not (hasattr(target, 'db') and target.db.roomtype == 'OOC Area'):
            original_location = self.caller.location
            self.caller.location = target  # Temporarily move caller for pose break
            self.send_pose_break()
            self.caller.location = original_location  # Restore original location

        # Check if the language switch is used
        use_language = 'language' in self.switches

        if use_language:
            # Handle language-specific emit
            speaking_language = caller.get_speaking_language()
            processed_message = self.process_special_characters(message)
            message = processed_message.strip()

            def process_speech(match):
                content = match.group(1)
                if content.startswith('~'):
                    content = content[1:]  # Remove the tilde
                    _, msg_understand, msg_not_understand, _ = caller.prepare_say(content, language_only=True)
                    return f'"{msg_understand}"', f'"{msg_not_understand}"'
                else:
                    return f'"{content}"', f'"{content}"'

            # Process the message
            parts_understand = []
            parts_not_understand = []
            last_end = 0
            for match in re.finditer(r'"(.*?)"', message):
                parts_understand.append(message[last_end:match.start()])
                parts_not_understand.append(message[last_end:match.start()])
                
                understand, not_understand = process_speech(match)
                parts_understand.append(understand)
                parts_not_understand.append(not_understand)
                
                last_end = match.end()
            parts_understand.append(message[last_end:])
            parts_not_understand.append(message[last_end:])

            emit_understand = "".join(parts_understand)
            emit_not_understand = "".join(parts_not_understand)

            # Send language-specific emits to the room
            for obj in target.contents:
                if hasattr(obj, 'get_languages'):
                    if speaking_language and speaking_language in obj.get_languages():
                        obj.msg(emit_understand)
                    else:
                        obj.msg(emit_not_understand)
                else:
                    obj.msg(emit_understand)
        else:
            # Send the message to everyone in the target room
            target.msg_contents(processed_message)

        # Confirm to the caller with room name and dbref
        caller.msg(f"You remit to {target.get_display_name(caller)} (#{target.id}): {processed_message}")

class CmdEmit(EmitBaseMixin, PoseBreakMixin, default_cmds.MuxCommand):
    """
    emit - Send a message to the room without your name attached.

    Usage:
      emit <message>
      emit/language <message>

    Switches:
      /language - Use this to emit a message in your character's set language.

    Examples:
      emit A cool breeze blows through the room.
      emit "~Bonjour, mes amis!" A voice calls out in French.
      emit/language The entire message is in the set language.

    Use quotes with a leading tilde (~) for speech in your set language.
    This will be understood only by those who know the language.
    """

    key = "emit"
    aliases = ["\\\\", "@emit"]
    locks = "cmd:all()"
    help_category = "Storytelling"

    def func(self):
        """Execute the @emit command"""
        caller = self.caller

        if not self.args:
            caller.msg("Usage: @emit <message>")
            return

        # Check if the room is an OOC Area
        if hasattr(caller.location, 'db') and caller.location.db.roomtype == 'OOC Area':
            # Process special characters in the message
            processed_args = self.process_special_characters(self.args)
            
            # Send message without pose break in OOC Area
            for obj in caller.location.contents:
                if obj.has_account:
                    obj.msg(processed_args)
            return

        # Process special characters in the message
        processed_args = self.process_special_characters(self.args)

        # Filter receivers based on Umbra state
        filtered_receivers = [
            obj for obj in caller.location.contents
            if obj.has_account and obj.db.in_umbra == caller.db.in_umbra
        ]

        # Send pose break before the message if enabled
        self.send_pose_break()

        # Check if the language switch is used
        use_language = 'language' in self.switches

        if use_language:
            # Handle language-specific emit
            speaking_language = caller.get_speaking_language()
            message = processed_args.strip()

            def process_speech(match):
                content = match.group(1)
                if content.startswith('~'):
                    content = content[1:]  # Remove the tilde
                    _, msg_understand, msg_not_understand, _ = caller.prepare_say(content, language_only=True)
                    return f'"{msg_understand}"', f'"{msg_not_understand}"'
                else:
                    return f'"{content}"', f'"{content}"'

            # Process the message
            parts_understand = []
            parts_not_understand = []
            last_end = 0
            for match in re.finditer(r'"(.*?)"', message):
                parts_understand.append(message[last_end:match.start()])
                parts_not_understand.append(message[last_end:match.start()])
                
                understand, not_understand = process_speech(match)
                parts_understand.append(understand)
                parts_not_understand.append(not_understand)
                
                last_end = match.end()
            parts_understand.append(message[last_end:])
            parts_not_understand.append(message[last_end:])

            emit_understand = "".join(parts_understand)
            emit_not_understand = "".join(parts_not_understand)

            # Send language-specific emits
            for receiver in filtered_receivers:
                if receiver != caller:
                    if speaking_language and speaking_language in receiver.get_languages():
                        receiver.msg(emit_understand)
                    else:
                        receiver.msg(emit_not_understand)
                else:
                    receiver.msg(emit_understand)
        else:
            # Send non-language emits
            for receiver in filtered_receivers:
                receiver.msg(processed_args)
