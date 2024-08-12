from evennia import default_cmds
from evennia.utils import ansi
import re

class CmdEmit(default_cmds.MuxCommand):
    """
    @emit - Send a message to the room without your name attached.

    Usage:
      @emit <message>
      @emit/language <message>

    Switches:
      /language - Use this to emit a message in your character's set language.

    Examples:
      @emit A cool breeze blows through the room.
      @emit "~Bonjour, mes amis!" A voice calls out in French.
      @emit/language The entire message is in the set language.

    Use quotes with a leading tilde (~) for speech in your set language.
    This will be understood only by those who know the language.
    """

    key = "@emit"
    aliases = ["@remit", "\\\\"]
    locks = "cmd:all()"
    help_category = "Storytelling"

    def func(self):
        """Execute the @emit command"""
        caller = self.caller

        if not self.args:
            caller.msg("Usage: @emit <message>")
            return

        # Check if the language switch is used
        use_language = 'language' in self.switches

        # Get the character's speaking language
        speaking_language = caller.get_speaking_language()

        message = self.args.strip()

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

        # Send the message to the room
        for receiver in [char for char in caller.location.contents if char.has_account]:
            if receiver != caller:
                if speaking_language and speaking_language in receiver.get_languages():
                    receiver.msg(emit_understand)
                else:
                    receiver.msg(emit_not_understand)
            else:
                receiver.msg(f"{emit_understand}")

        # Log the emit
        caller.location.msg_contents(f"{message}", exclude=caller)
