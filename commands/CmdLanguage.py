from evennia.utils import evtable
from evennia.commands.default.muxcommand import MuxCommand

# This dictionary should be populated with all available languages
AVAILABLE_LANGUAGES = {
    "arabic": "Arabic",
    "chinese": "Chinese",
    "english": "English",
    "french": "French",
    "german": "German",
    "italian": "Italian",
    "japanese": "Japanese",
    "russian": "Russian",
    "spanish": "Spanish",
    # Add more languages as needed
}

class CmdLanguage(MuxCommand):
    """
    Set your speaking language, view known languages, or add a new language.

    Usage:
      +language
      +language <language>
      +language none
      +language/add <language>

    Examples:
      +language
      +language Spanish
      +language none
      +language/add French
    """

    key = "+language"
    aliases = ["+lang"]
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.list_languages()
        elif "add" in self.switches:
            self.add_language()
        elif self.args.lower() == "none":
            self.set_speaking_language(None)
        else:
            self.set_speaking_language(self.args.lower().capitalize())

    def list_languages(self):
        languages = self.caller.get_languages()
        current = self.caller.get_speaking_language()
        table = evtable.EvTable("Known Languages", "Currently Speaking", border="cells")
        table.add_row(", ".join(languages) or "None", current or "None")
        self.caller.msg(table)

    def set_speaking_language(self, language):
        try:
            self.caller.set_speaking_language(language)
            if language:
                self.caller.msg(f"|cLANGUAGE>|n Now speaking in |w{language}|n.")
            else:
                self.caller.msg("|cLANGUAGE>|n You are no longer speaking in any specific language.")
        except ValueError as e:
            self.caller.msg(str(e))

    def add_language(self):
        if not self.args:
            self.caller.msg("Usage: +language/add <language>")
            return

        # Check if the character is approved
        if self.caller.db.approved:
            self.caller.msg("You cannot add languages after character approval.")
            return

        language = self.args.lower()
        if language not in AVAILABLE_LANGUAGES:
            self.caller.msg(f"Invalid language. Available languages are: {', '.join(AVAILABLE_LANGUAGES.values())}")
            return

        # Check for Language merit
        language_merit = self.caller.db.stats.get('merits', {}).get('social', {}).get('Language', {}).get('perm', 0)
        current_languages = self.caller.get_languages()

        if len(current_languages) >= language_merit:
            self.caller.msg("You don't have enough Language merit points to add another language.")
            return

        if AVAILABLE_LANGUAGES[language] in current_languages:
            self.caller.msg(f"You already know {AVAILABLE_LANGUAGES[language]}.")
            return

        # Add the language
        if not hasattr(self.caller.db, 'languages') or self.caller.db.languages is None:
            self.caller.db.languages = []
        self.caller.db.languages.append(AVAILABLE_LANGUAGES[language])
        self.caller.msg(f"You have learned {AVAILABLE_LANGUAGES[language]}.")
