from evennia.utils import evtable
from evennia.commands.default.muxcommand import MuxCommand
from world.wod20th.utils.language_data import AVAILABLE_LANGUAGES

# This dictionary should be populated with all available languages
class CmdLanguage(MuxCommand):
    """
    Set your speaking language, view known languages, or add a new language.

    Usage:
      +language
      +language <language>
      +language none
      +language/add <language>
      +language/all
      +language/set <character>=<language1>,<language2>,...  (Staff only)

    Examples:
      +language
      +language Spanish
      +language none
      +language/add French
      +language/all
      +language/set Bob=English,Spanish,French
    """

    key = "+language"
    aliases = ["+lang"]
    locks = "cmd:all()"

    def func(self):
        if "set" in self.switches:
            self.do_set_languages()
        elif "all" in self.switches:
            self.list_all_languages()
        elif not self.args:
            self.list_languages()
        elif "add" in self.switches:
            self.add_language()
        elif self.args.lower() == "none":
            self.set_speaking_language(None)
        else:
            self.set_speaking_language(self.args.lower().capitalize())

    def list_languages(self):
        """Display the character's known languages and current speaking language."""
        languages = self.caller.get_languages()
        current = self.caller.get_speaking_language()
        
        table = evtable.EvTable("Known Languages", "Currently Speaking", border="cells")
        table.add_row(", ".join(languages) if languages else "None", 
                     current if current else "None")
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

        # Get the proper case version of the language
        proper_language = AVAILABLE_LANGUAGES[language]

        # Everyone knows English by default
        if proper_language == "English":
            self.caller.msg("Everyone knows English by default.")
            return

        # Get current languages and clean them
        current_languages = self.caller.get_languages()

        # Check for Language merit points and Natural Linguist
        language_merit_points = 0
        natural_linguist = False
        merits = self.caller.db.stats.get('merits', {})
        
        # Check for Natural Linguist in all merit categories
        for category in merits:
            category_merits = merits[category]
            if any(merit.lower().replace(' ', '') == 'naturallinguist' 
                  for merit in category_merits.keys()):
                natural_linguist = True
                break
        
        # Check for Language merit in all merit categories
        for category in merits:
            category_merits = merits[category]
            for merit_name, merit_data in category_merits.items():
                if merit_name == 'Language':
                    base_points = merit_data.get('perm', 0)
                    language_merit_points = base_points * 2 if natural_linguist else base_points
                    break  # Found the main Language merit, no need to check further
                elif merit_name.startswith('Language('):
                    base_points = merit_data.get('perm', 0)
                    points = base_points * 2 if natural_linguist else base_points
                    language_merit_points += points

        # Subtract 1 from the comparison since English is free
        if (len(current_languages) - 1) >= language_merit_points:
            msg = [
                "You don't have enough Language merit points to add another language.",
                "You need to purchase the Language merit using:",
                "  +selfstat Language/social=<points>",
            ]
            if natural_linguist:
                msg.append("You have Natural Linguist, which doubles your language points!")
            msg.append(f"Current: {language_merit_points} point(s) ({language_merit_points//2 if natural_linguist else language_merit_points} from Language merit{' x2 from Natural Linguist' if natural_linguist else ''})")
            msg.append(f"Languages used: {len(current_languages) - 1}")
            
            self.caller.msg("\n".join(msg))
            return

        # Check if language is already known (case-insensitive)
        if proper_language in current_languages:
            self.caller.msg(f"You already know {proper_language}.")
            return

        # Add the new language and store the updated list
        current_languages.append(proper_language)
        self.caller.db.languages = current_languages
        
        self.caller.msg(f"You have learned {proper_language}. "
                       f"({len(current_languages) - 1}/{language_merit_points} additional languages used)")

    def do_set_languages(self):
        """
        Staff command to set languages on a character.
        Usage: +language/set <character>=<language1>,<language2>,...
        """
        if not self.caller.check_permstring("Developer"):
            self.caller.msg("You don't have permission to set languages.")
            return
            
        if not self.lhs or not self.rhs:
            self.caller.msg("Usage: +language/set <character>=<language1>,<language2>,...\n"
                          "Example: +language/set Bob=English,Spanish,French")
            return
            
        # Find the target character
        target = self.caller.search(self.lhs)
        if not target:
            return
            
        # Parse the languages
        new_languages = []
        invalid_languages = []
        
        # Always include English first
        new_languages.append("English")
        
        # Process each language
        for lang in self.rhs.split(','):
            lang = lang.strip()
            if not lang or lang.lower() == "english":  # Skip empty or English (already added)
                continue
                
            # Try to find the proper case version
            found = False
            for available_lang in AVAILABLE_LANGUAGES.values():
                if available_lang.lower() == lang.lower():
                    if available_lang not in new_languages:  # Avoid duplicates
                        new_languages.append(available_lang)
                    found = True
                    break
                    
            if not found:
                invalid_languages.append(lang)
        
        if invalid_languages:
            self.caller.msg(f"Warning: The following languages were not recognized: {', '.join(invalid_languages)}\n"
                          f"Available languages are: {', '.join(AVAILABLE_LANGUAGES.values())}")
            return
            
        # Set the languages
        target.db.languages = new_languages
        
        # Update speaking language if needed
        if target.get_speaking_language() not in new_languages:
            target.db.speaking_language = "English"
            
        self.caller.msg(f"Set {target.name}'s languages to: {', '.join(new_languages)}")
        target.msg(f"Your known languages have been set to: {', '.join(new_languages)}")

    def list_all_languages(self):
        """Display all available languages organized by region."""
        # Define categories and their languages
        categories = {
            "Major World Languages": [
                "Arabic", "Bengali", "Chinese (Mandarin)", "English", "French", 
                "German", "Hindi", "Indonesian", "Italian", "Japanese", "Korean",
                "Persian (Farsi)", "Portuguese", "Russian", "Spanish", "Turkish",
                "Urdu", "Vietnamese"
            ],
            "African Languages": [
                "Amharic", "Hausa", "Igbo", "Lingala", "Oromo", "Somali",
                "Swahili", "Twi", "Wolof", "Yoruba", "Zulu"
            ],
            "European Languages": [
                "Bosnian", "Bulgarian", "Croatian", "Czech", "Danish", "Dutch",
                "Finnish", "Greek", "Hungarian", "Norwegian", "Polish", "Romanian",
                "Serbian", "Swedish", "Ukrainian"
            ],
            "Asian Languages": [
                "Burmese", "Chinese (Cantonese)", "Gujarati", "Khmer", "Lao",
                "Malay", "Punjabi", "Tamil", "Telugu", "Thai", "Vietnamese"
            ],
            "Middle Eastern Languages": [
                "Hebrew", "Kurdish"
            ],
            "Indigenous American Languages": [
                "Navajo", "Quechua"
            ],
            "Pacific Languages": [
                "Hawaiian", "Maori", "Tagalog"
            ]
        }
        
        # Create the display table
        from evennia.utils import evtable
        
        # Header
        self.caller.msg("|wAvailable Languages:|n")
        self.caller.msg("=" * 78)
        
        # Display each category
        for category_name, languages in categories.items():
            if languages:  # Only show categories that have languages
                self.caller.msg(f"\n|y{category_name}:|n")
                
                # Sort languages alphabetically within each category
                languages.sort()
                
                # Create columns (3 columns of approximately equal size)
                table = evtable.EvTable(border=None)
                col_width = 25  # Adjust this if needed
                
                # Split languages into columns
                col1 = languages[::3]
                col2 = languages[1::3]
                col3 = languages[2::3]
                
                # Add columns to table
                table.add_column(*col1, width=col_width)
                if col2:  # Only add column if there are languages for it
                    table.add_column(*col2, width=col_width)
                if col3:  # Only add column if there are languages for it
                    table.add_column(*col3, width=col_width)
                
                # Display the table
                self.caller.msg(table)
        
        self.caller.msg("\n" + "=" * 78)
