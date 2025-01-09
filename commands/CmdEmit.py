from evennia import default_cmds
from evennia.utils import ansi
from commands.CmdPose import PoseBreakMixin
import re

class CmdEmit(PoseBreakMixin, default_cmds.MuxCommand):
    """
    @emit - Send a message to the room without your name attached.

    Usage:
      @emit <message>
      @emit/language <message>

    Switches:
      /language - Use this to emit a message in your set language.

    Examples:
      @emit A cool breeze blows through the room.
      @emit "~Bonjour, mes amis!" A voice calls out in French.
      @emit/language The entire message is in the set language.

    Use quotes with a leading tilde (~) for speech in your set language.
    This will be understood only by those who know the language.
    """

    key = "@emit"
    aliases = ["\\\\"]
    locks = "cmd:all()"
    help_category = "Storytelling"

    def process_special_characters(self, message):
        """
        Process %r and %t in the message, replacing them with appropriate ANSI codes.
        """
        message = message.replace('%r', '|/').replace('%t', '|-')
        return message

    def func(self):
        """Execute the @emit command"""
        caller = self.caller

        if not self.args:
            caller.msg("Usage: @emit <message>")
            return

        # Process special characters in the message
        processed_args = self.process_special_characters(self.args)

        # Check if there's a language-tagged speech and set speaking language
        if "~" in processed_args or 'language' in self.switches:
            speaking_language = caller.get_speaking_language()
            if not speaking_language:
                caller.msg("You need to set a speaking language first with +language <language>")
                return

        # Filter receivers based on Umbra state
        filtered_receivers = [
            obj for obj in caller.location.contents
            if obj.has_account and obj.db.in_umbra == caller.db.in_umbra
        ]

        # Send pose break before the message
        self.send_pose_break()

        if 'language' in self.switches:
            # The entire emit is in the set language
            speaking_language = caller.get_speaking_language()
            _, msg_understand, msg_not_understand, _ = caller.prepare_say(processed_args, language_only=True)

            for receiver in filtered_receivers:
                has_universal = any(
                    merit.lower().replace(' ', '') == 'universallanguage'
                    for category in receiver.db.stats.get('merits', {}).values()
                    for merit in category.keys()
                )
                
                if receiver == caller or has_universal or speaking_language in receiver.get_languages():
                    receiver.msg(msg_understand)
                else:
                    receiver.msg(msg_not_understand)
        else:
            # Handle mixed language content
            for receiver in filtered_receivers:
                if "~" in processed_args:
                    parts = []
                    current_pos = 0
                    for match in re.finditer(r'"~([^"]+)"', processed_args):
                        # Add text before the speech
                        parts.append(processed_args[current_pos:match.start()])
                        
                        # Process the speech
                        speech = match.group(1)
                        _, msg_understand, msg_not_understand, _ = caller.prepare_say(speech, language_only=True)
                        
                        # Check for Universal Language merit
                        has_universal = any(
                            merit.lower().replace(' ', '') == 'universallanguage'
                            for category in receiver.db.stats.get('merits', {}).values()
                            for merit in category.keys()
                        )
                        
                        speaking_language = caller.get_speaking_language()
                        if receiver == caller or has_universal or (speaking_language and speaking_language in receiver.get_languages()):
                            parts.append(f'"{msg_understand}"')
                        else:
                            parts.append(f'"{msg_not_understand}"')
                        
                        current_pos = match.end()
                    
                    # Add any remaining text
                    parts.append(processed_args[current_pos:])
                    
                    # Send the final message
                    receiver.msg(''.join(parts))
                else:
                    # No language-tagged content, send as is
                    receiver.msg(processed_args)