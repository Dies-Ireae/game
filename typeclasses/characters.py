"""
Characters

Characters are (by default) Objects that are puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type for your game. It is from
here you can define how all characters will look and behave by default.
"""
from evennia.objects.objects import DefaultCharacter
from evennia.utils.utils import lazy_property
from evennia.utils.ansi import ANSIString
from world.wod20th.models import Stat, Note
from world.wod20th.utils.ansi_utils import wrap_ansi
import re
import random
from datetime import datetime
from evennia.comms.models import ChannelDB
from commands.CmdLanguage import AVAILABLE_LANGUAGES
from evennia.commands.cmdset import CmdSet

class Character(DefaultCharacter):
    """
    The Character defaults to implementing some of its hook methods with the
    following standard functionality:
    ...
    """

    def at_object_creation(self):
        """
        Called only at initial creation.
        """
        super().at_object_creation()

        # Initialize basic attributes
        self.db.desc = ""
        self.db.stats = {}
        
        # Initialize languages with English as default
        self.db.languages = ["English"]
        self.db.speaking_language = "English"
        
        self.tags.add("in_material", category="state")
        self.db.unfindable = False
        self.db.fae_desc = ""
        self.db.approved = False  # Ensure all new characters start unapproved
        self.db.in_umbra = False  # Use a persistent attribute instead of a tag
        
        # Initialize health tracking
        self.db.agg = 0
        self.db.lethal = 0
        self.db.bashing = 0
        self.db.injury_level = "Healthy"

        # Auto-subscribe to Public channel
        try:
            public_channel = ChannelDB.objects.get(db_key__iexact="public")
            if not public_channel.has_connection(self):
                public_channel.connect(self)
        except ChannelDB.DoesNotExist:
            pass

    @lazy_property
    def notes(self):
        return Note.objects.filter(character=self)

    def add_note(self, name, text, category="General", is_public=False):
        """Add a new note."""
        notes = self.attributes.get('notes', default={})
        note_id = str(len(notes) + 1)
        
        note = Note(
            name=name,
            text=text,
            category=category,
            is_public=is_public,
            note_id=note_id
        )
        
        notes[note_id] = note.to_dict()
        self.attributes.add('notes', notes)
        return note

    def get_note(self, note_id):
        """Get a specific note by ID."""
        notes = self.attributes.get('notes', default={})
        note_data = notes.get(str(note_id))
        return Note.from_dict(note_data) if note_data else None

    def get_all_notes(self):
        """Get all notes for this character."""
        notes = self.attributes.get('notes', default={})
        return [Note.from_dict(note_data) for note_data in notes.values()]

    def update_note(self, note_id, text=None, category=None, **kwargs):
        """Update an existing note."""
        notes = self.attributes.get('notes', default={})
        if str(note_id) in notes:
            note_data = notes[str(note_id)]
            if text is not None:
                note_data['text'] = text
            if category is not None:
                note_data['category'] = category
            note_data.update(kwargs)
            note_data['updated_at'] = datetime.now().isoformat()
            notes[str(note_id)] = note_data
            self.attributes.add('notes', notes)
            return True
        return False

    def change_note_status(self, note_name, is_public):
        """Change the visibility status of a note."""
        try:
            note = self.get_note(note_name)
            if note:
                note.is_public = is_public
                note.save()
                return True
            return False
        except Exception as e:
            logger.log_err(f"Error in change_note_status: {e}")
            return False

    def get_display_name(self, looker, **kwargs):
        """
        Get the name to display for the character.
        """
        name = self.key
        
        if self.db.gradient_name:
            name = ANSIString(self.db.gradient_name)
            if looker.check_permstring("builders"):
                name += f"({self.dbref})"
            return name
        
        # If the looker is builder+ show the dbref
        if looker.check_permstring("builders"):
            name += f"({self.dbref})"

        return name

    def get_languages(self):
        """
        Get the character's known languages.
        """
        # Get current languages, initialize if needed
        current_languages = self.db.languages or []
        
        # Convert to list if it's not already
        if not isinstance(current_languages, list):
            current_languages = [current_languages]
        
        # Clean up the languages list
        cleaned_languages = []
        seen = set()
        
        # First pass: extract all language strings and clean them
        for entry in current_languages:
            # Convert to string and clean it
            lang_str = str(entry).replace('"', '').replace("'", '').replace('[', '').replace(']', '')
            # Split on commas and process each part
            for part in lang_str.split(','):
                clean_lang = part.strip()
                if clean_lang and clean_lang.lower() not in seen:
                    # Check if it's a valid language
                    for available_lang in AVAILABLE_LANGUAGES.values():
                        if available_lang.lower() == clean_lang.lower():
                            cleaned_languages.append(available_lang)
                            seen.add(available_lang.lower())
                            break
        
        # Ensure English is first
        if "English" in cleaned_languages:
            cleaned_languages.remove("English")
        cleaned_languages.insert(0, "English")
        
        # Store the cleaned list back to the database
        self.db.languages = cleaned_languages
        return cleaned_languages

    def set_speaking_language(self, language):
        """
        Set the character's currently speaking language.
        """
        if language is None:
            self.db.speaking_language = None
            return
            
        # Get clean language list
        known_languages = self.get_languages()
        
        # Case-insensitive check
        for known in known_languages:
            if known.lower() == language.lower():
                self.db.speaking_language = known
                return
                
        raise ValueError(f"You don't know the language: {language}")

    def get_speaking_language(self):
        """
        Get the character's currently speaking language.
        """
        return self.db.speaking_language

    def detect_tone(self, message):
        """
        Detect the tone of the message based on punctuation and keywords.
        """
        if message.endswith('!'):
            return "excitedly"
        elif message.endswith('?'):
            return "questioningly"
        elif any(word in message.lower() for word in ['hello', 'hi', 'hey', 'greetings']):
            return "in greeting"
        elif any(word in message.lower() for word in ['goodbye', 'bye', 'farewell']):
            return "in farewell"
        elif any(word in message.lower() for word in ['please', 'thank', 'thanks']):
            return "politely"
        elif any(word in message.lower() for word in ['sorry', 'apologize']):
            return "apologetically"
        else:
            return None  # No specific tone detected

    def mask_language(self, message, language):
        """
        Mask the language in the message with more dynamic responses.
        """
        words = len(message.split())
        tone = self.detect_tone(message)

        if words <= 3:
            options = [
                f"<< mutters a few words in {language} >>",
                f"<< something brief in {language} >>",
                f"<< speaks a short {language} phrase >>",
            ]
        elif words <= 10:
            options = [
                f"<< speaks a sentence in {language} >>",
                f"<< a {language} phrase >>",
                f"<< conveys a short message in {language} >>",
            ]
        else:
            options = [
                f"<< gives a lengthy explanation in {language} >>",
                f"<< engages in an extended {language} dialogue >>",
                f"<< speaks at length in {language} >>",
            ]

        masked = random.choice(options)
        
        if tone:
            masked = f"{masked[:-3]}, {tone} >>"

        return masked

    def prepare_say(self, message, language_only=False):
        """
        Prepare the messages for the say command, handling tilde-based language switching.
        """
        use_language = message.lstrip().startswith('~')
        name = self.db.gradient_name if self.db.gradient_name else self.name
        language = self.get_speaking_language()
        
        if use_language:
            # strip the tilde from the message
            message = message[1:].lstrip()
            
                       
            if language and not language_only:
                # Preserve the tilde in the message
                masked_message = self.mask_language(message, language)
                msg_self = f'You say, "{message} |w<< in {language} >>|n"'
                msg_understand = f'{name} says, "{message} |w<< in {language} >>|n"'
                msg_not_understand = f'{name} says, "{masked_message}"'
            else:
                msg_self = f'You say, "{message}"'
                msg_understand = f'{name} says, "{message}"'
                msg_not_understand = msg_understand
               
        else:
            msg_self = f'You say, "{message}"'
            msg_understand = f'{name} says, "{message}"'
            msg_not_understand = msg_understand
           
        
        if language_only and language:
            msg_self = f'{message} |w<< in {language} >>|n'
            msg_understand = f'{message} |w<< in {language} >>|n'
            msg_not_understand = f'{self.mask_language(message, language)}'    
        elif language_only:
            msg_self = f'{message}'
            msg_understand = f'{message}'
            msg_not_understand = f'{message}'
            language = None

        else:
            language = None

        return msg_self, msg_understand, msg_not_understand, language

    def step_sideways(self):
        """Attempt to step sideways into the Umbra."""
        if self.db.in_umbra:
            self.msg("You are already in the Umbra.")
            return False
        
        if self.location:
            success = self.location.step_sideways(self)
            if success:
                # Use attributes.add for more reliable attribute setting
                self.attributes.add('in_umbra', True)
                self.tags.remove("in_material", category="state")
                self.tags.add("in_umbra", category="state")
                self.location.msg_contents(f"{self.name} shimmers and fades from view as they step into the Umbra.", exclude=[self])
            return success
        return False

    def return_from_umbra(self):
        """Return from the Umbra to the material world."""
        if not self.db.in_umbra:
            self.msg("You are not in the Umbra.")
            return False
        
        # Use attributes.add for more reliable attribute setting
        self.attributes.add('in_umbra', False)
        self.tags.remove("in_umbra", category="state")
        self.tags.add("in_material", category="state")
        self.location.msg_contents(f"{self.name} shimmers into view as they return from the Umbra.", exclude=[self])
        return True

    def return_appearance(self, looker, **kwargs):
        """
        This formats a description for any object looking at this object.
        """
        if not looker:
            return ""
        
        # Get the description
        desc = self.db.desc

        # Start with the name
        string = f"|c{self.get_display_name(looker)}|n\n"

        # Process character description
        if desc:
            # Replace both %t and |- with a consistent tab marker
            desc = desc.replace('%t', '|t').replace('|-', '|t')
            
            paragraphs = desc.split('%r')
            formatted_paragraphs = []
            for p in paragraphs:
                if not p.strip():
                    formatted_paragraphs.append('')  # Add blank line for empty paragraph
                    continue
                
                # Handle tabs manually
                lines = p.split('|t')
                indented_lines = [line.strip() for line in lines]
                indented_text = '\n    '.join(indented_lines)
                
                # Wrap each line individually
                wrapped_lines = [wrap_ansi(line, width=78) for line in indented_text.split('\n')]
                formatted_paragraphs.append('\n'.join(wrapped_lines))
            
            # Join paragraphs with a single newline, and remove any consecutive newlines
            joined_paragraphs = '\n'.join(formatted_paragraphs)
            joined_paragraphs = re.sub(r'\n{3,}', '\n\n', joined_paragraphs)
            
            string += joined_paragraphs + "\n"

        # Add any other details you want to include in the character's appearance
        # For example, you might want to add information about their equipment, stats, etc.

        return string

    def announce_move_from(self, destination, msg=None, mapping=None, **kwargs):
        """
        Called just before moving out of the current room.
        """
        if not self.location:
            return

        string = f"{self.name} is leaving {self.location}, heading for {destination}."
        
        # Send message directly to the room
        self.location.msg_contents(string, exclude=[self], from_obj=self)

    def announce_move_to(self, source_location, msg=None, mapping=None, **kwargs):
        """
        Called just after arriving in a new room.
        """
        if not source_location:
            return

        string = f"{self.name} arrives to {self.location} from {source_location}."
        
        # Send message directly to the room
        self.location.msg_contents(string, exclude=[self], from_obj=self)

    def at_say(self, message, msg_self=None, msg_location=None, receivers=None, msg_receivers=None, **kwargs):
        """Hook method for the say command."""
        if not self.location:
            return

        # Filter receivers based on Umbra state
        filtered_receivers = [
            r for r in self.location.contents 
            if hasattr(r, 'has_account') and r.has_account and r.db.in_umbra == self.db.in_umbra
        ]

        # Prepare the say messages
        msg_self, msg_understand, msg_not_understand, language = self.prepare_say(message)

        # Send messages to receivers
        for receiver in filtered_receivers:
            if receiver != self:
                if language and language in receiver.get_languages():
                    receiver.msg(msg_understand)
                else:
                    receiver.msg(msg_not_understand)

        # Send message to the speaker
        self.msg(msg_self)

    def at_pose(self, pose_understand, pose_not_understand, pose_self, speaking_language):
        if not self.location:
            return

        # Filter receivers based on Umbra state
        filtered_receivers = [
            r for r in self.location.contents 
            if hasattr(r, 'has_account') and r.has_account and r.db.in_umbra == self.db.in_umbra
        ]

        # Send messages to receivers
        for receiver in filtered_receivers:
            if receiver != self:
                if speaking_language and speaking_language in receiver.get_languages():
                    receiver.msg(pose_understand)
                else:
                    receiver.msg(pose_not_understand)

        # Send message to the poser
        self.msg(pose_self)

        # Log the pose (only visible to those in the same realm)
        self.location.msg_contents(pose_understand, exclude=filtered_receivers + [self], from_obj=self)

    def at_emote(self, message, msg_self=None, msg_location=None, receivers=None, msg_receivers=None, **kwargs):
        """Display an emote to the room."""
        if not self.location:
            return

        # Filter receivers based on Umbra state
        filtered_receivers = [
            r for r in self.location.contents 
            if hasattr(r, 'has_account') and r.has_account and r.db.in_umbra == self.db.in_umbra
        ]
        
        # Send the emote to filtered receivers
        for receiver in filtered_receivers:
            if receiver != self:
                receiver.msg(message)
        
        # Send the emote to the emitter
        self.msg(msg_self or message)

    def get_stat(self, category, stat_type, stat_name, temp=False):
        """
        Retrieve the value of a stat, considering instances if applicable.
        """
        if not hasattr(self.db, "stats") or not self.db.stats:
            return None

        category_stats = self.db.stats.get(category, {})
        type_stats = category_stats.get(stat_type, {})

        # Handle background instances
        if category == "backgrounds":
            instance_match = re.match(r"(\w+)\(([\w\s]+)\)", stat_name)
            if instance_match:
                base_stat = instance_match.group(1)
                instance = instance_match.group(2)
                
                if base_stat in type_stats:
                    instances = type_stats[base_stat].get('instances', {})
                    if instance in instances:
                        return instances[instance]['temp' if temp else 'perm']
                return None

        # Handle non-instanced stats
        if stat_name in type_stats:
            if isinstance(type_stats[stat_name], dict) and 'instances' in type_stats[stat_name]:
                # Return base value for background without instance
                return type_stats[stat_name]['base']['temp' if temp else 'perm']
            return type_stats[stat_name]['temp' if temp else 'perm']

        # If not found and the category is 'pools', check in 'dual' as well
        if category == 'pools' and 'dual' in self.db.stats:
            dual_stats = self.db.stats['dual']
            if stat_name in dual_stats:
                return dual_stats[stat_name]['temp' if temp else 'perm']

        # If still not found, check the Stat model
        stat = Stat.objects.filter(name=stat_name, category=category, stat_type=stat_type).first()
        if stat:
            return stat.default

        return None

    def set_stat(self, category, stat_type, stat_name, value, temp=False):
        """
        Set the value of a stat, considering instances if applicable.
        Also handles special cases like Appearance for certain splats/forms.
        """
        if not hasattr(self.db, "stats") or not self.db.stats:
            self.db.stats = {}
        if category not in self.db.stats:
            self.db.stats[category] = {}
        if stat_type not in self.db.stats[category]:
            self.db.stats[category][stat_type] = {}
        if stat_name not in self.db.stats[category][stat_type]:
            self.db.stats[category][stat_type][stat_name] = {'perm': 0, 'temp': 0}

        # Special handling for Appearance stat
        if stat_name == 'Appearance':
            splat = self.db.stats.get('other', {}).get('splat', {}).get('Splat', {}).get('perm', '')
            clan = self.db.stats.get('identity', {}).get('lineage', {}).get('Clan', {}).get('perm', '')
            form = self.db.stats.get('other', {}).get('form', {}).get('Form', {}).get('temp', '')

            # Force Appearance to 0 for specific cases
            if (splat == 'Vampire' and clan in ['Nosferatu', 'Samedi']) or \
               (splat == 'Shifter' and form == 'Crinos'):
                value = 0
                self.db.stats[category][stat_type][stat_name]['perm'] = 0
                self.db.stats[category][stat_type][stat_name]['temp'] = 0
                return

        # Normal stat setting
        if temp:
            self.db.stats[category][stat_type][stat_name]['temp'] = value
        else:
            self.db.stats[category][stat_type][stat_name]['perm'] = value

    def check_stat_value(self, category, stat_type, stat_name, value, temp=False):
        """
        Check if a value is valid for a stat, considering instances if applicable.
        """
        from world.wod20th.models import Stat  
        stat = Stat.objects.filter(name=stat_name, category=category, stat_type=stat_type).first()
        if stat:
            stat_values = stat.values
            return value in stat_values['temp'] if temp else value in stat_values['perm']
        return False

    def colorize_name(self, message):
        """
        Replace instances of the character's name with their gradient name in the message.
        """
        if self.db.gradient_name:
            gradient_name = ANSIString(self.db.gradient_name)
            return message.replace(self.name, str(gradient_name))
        return message
 
    def delete_note(self, note_id):
        """Delete a note."""
        notes = self.attributes.get('notes', default={})
        if str(note_id) in notes:
            del notes[str(note_id)]
            self.attributes.add('notes', notes)
            return True
        return False

    def get_notes_by_category(self, category):
        """Get all notes in a specific category."""
        return [note for note in self.get_all_notes() 
                if note.category.lower() == category.lower()]

    def get_public_notes(self):
        """Get all public notes."""
        return [note for note in self.get_all_notes() if note.is_public]

    def get_approved_notes(self):
        """Get all approved notes."""
        return [note for note in self.get_all_notes() if note.is_approved]

    def approve_note(self, name):
        if self.character_sheet:
            return self.character_sheet.approve_note(name)
        return False

    def unapprove_note(self, name):
        if self.character_sheet:
            return self.character_sheet.unapprove_note(name)
        return False

    def change_note_status(self, name, is_public):
        if self.character_sheet:
            return self.character_sheet.change_note_status(name, is_public)
        return False

    def get_fae_description(self):
        """Get the fae description of the character."""
        return self.db.fae_desc or f"{self.name} has no visible fae aspect."

    def set_fae_description(self, description):
        """Set the fae description of the character."""
        self.db.fae_desc = description

    def is_fae_perceiver(self):
        """Check if the character is a Changeling or Kinain."""
        if not self.db.stats or 'other' not in self.db.stats or 'splat' not in self.db.stats['other']:
            return False
        splat = self.db.stats['other']['splat'].get('Splat', {}).get('perm', '')
        return splat in ['Changeling', 'Kinain']

    def search_notes(self, search_term):
        """Search notes by name or content."""
        search_term = search_term.lower()
        return [
            note for note in self.get_all_notes()
            if search_term in note.name.lower() or search_term in note.text.lower()
        ]

    def can_have_ability(self, ability_name):
        """Check if character can have a specific ability based on splat."""
        from world.wod20th.models import Stat
        
        stat = Stat.objects.filter(name=ability_name).first()
        if not stat or not stat.splat:
            return True
            
        # Get character's splat info
        splat_type = self.db.stats.get('other', {}).get('splat', {}).get('Splat', {}).get('perm', '')
        clan = self.db.stats.get('identity', {}).get('lineage', {}).get('Clan', {}).get('perm', '')
        shifter_type = self.db.stats.get('identity', {}).get('lineage', {}).get('Type', {}).get('perm', '')

        # Check allowed splats
        allowed_splats = stat.splat
        if isinstance(allowed_splats, list):
            for allowed in allowed_splats:
                if ':' in allowed:
                    splat_name, subtype = allowed.split(':')
                    if splat_type == splat_name:
                        if splat_name == 'Vampire' and clan == subtype:
                            return True
                        elif splat_name == 'Shifter' and shifter_type == subtype:
                            return True
                else:
                    if splat_type == allowed:
                        return True
                        
        return False

    def shift_form(self, new_form):
        """Handle form changes for shifters, including Appearance adjustments."""
        old_form = self.db.stats.get('other', {}).get('form', {}).get('Form', {}).get('temp', '')
        
        # Set the new form
        self.set_stat('other', 'form', 'Form', new_form, temp=True)
        
        # Handle Appearance changes
        if new_form == 'Crinos':
            self.set_stat('attributes', 'social', 'Appearance', 0, temp=True)
        elif old_form == 'Crinos' and new_form != 'Crinos':
            # Restore original Appearance when leaving Crinos
            perm_appearance = self.db.stats.get('attributes', {}).get('social', {}).get('Appearance', {}).get('perm', 1)
            self.set_stat('attributes', 'social', 'Appearance', perm_appearance, temp=True)

    def matches_name(self, searchstring):
        """
        Check if the searchstring matches this character's name or alias.
        """
        searchstring = searchstring.lower().strip()
        
        # First check direct name match
        if self.key.lower() == searchstring:
            return True
            
        # Then check alias
        if self.attributes.has("alias"):
            alias = self.attributes.get("alias")
            if alias and alias.lower() == searchstring:
                return True
            
        return False

    @classmethod
    def get_by_alias(cls, searchstring):
        """
        Find a character by their alias.
        
        Args:
            searchstring (str): The alias to search for
            
        Returns:
            Character or None: The character with matching alias, if any
        """
        from evennia.utils.search import search_object
        
        # Search for objects with matching alias attribute
        matches = search_object(
            searchstring, 
            attribute_name="alias",
            exact=True,
            typeclass='typeclasses.characters.Character'
        )
        
        return matches[0] if matches else None

    def at_post_create(self):
        """
        Called after character creation and after all attributes are set.
        """
        super().at_post_create()

        # Auto-subscribe to Public channel
        try:
            public_channel = ChannelDB.objects.get(db_key__iexact="public")
            if not public_channel.has_connection(self):
                public_channel.connect(self)
        except ChannelDB.DoesNotExist:
            pass

    def handle_language_merit_change(self):
        """
        Handle changes to Language merit or Natural Linguist merit.
        Removes excess languages if merit points are reduced.
        """
        merits = self.db.stats.get('merits', {})
        language_points = 0
        natural_linguist = False
        
        # Check for Natural Linguist in both categories
        for category in ['mental', 'social']:
            if category in merits:
                if any(merit.lower().replace(' ', '') == 'naturallinguist' 
                      for merit in merits[category].keys()):
                    natural_linguist = True
                    break
        
        # Get Language merit points
        if 'social' in merits:
            for merit_name, merit_data in merits['social'].items():
                if merit_name == 'Language':
                    base_points = merit_data.get('perm', 0)
                    language_points = base_points * 2 if natural_linguist else base_points
                    break
        
        # Get current languages
        current_languages = self.get_languages()
        
        # If we have more languages than points allow (accounting for free English)
        if len(current_languages) - 1 > language_points:
            # Keep English and only as many additional languages as we have points for
            new_languages = ["English"]
            additional_languages = [lang for lang in current_languages if lang != "English"]
            new_languages.extend(additional_languages[:language_points])
            
            # Update languages
            self.db.languages = new_languages
            
            # Reset speaking language to English if current language was removed
            if self.db.speaking_language not in new_languages:
                self.db.speaking_language = "English"
            
            # Notify the character with more detail
            removed_languages = set(current_languages) - set(new_languages)
            self.msg(f"Your language merit points have been reduced to {language_points}. "
                    f"The following languages have been removed: {', '.join(removed_languages)}\n"
                    f"Your known languages are now: {', '.join(new_languages)}")
        
        # If Natural Linguist was removed, update the display
        if not natural_linguist and len(current_languages) > 1:
            self.msg(f"Natural Linguist merit removed. Your current language points: {language_points}")

class Note:
    def __init__(self, name, text, category="General", is_public=False, is_approved=False, 
                 approved_by=None, approved_at=None, created_at=None, updated_at=None, note_id=None):
        self.name = name
        self.text = text
        self.category = category
        self.is_public = is_public
        self.is_approved = is_approved
        self.approved_by = approved_by
        self.approved_at = approved_at
        self.created_at = created_at if isinstance(created_at, datetime) else datetime.now()
        self.updated_at = updated_at if isinstance(updated_at, datetime) else datetime.now()
        self.note_id = note_id

    @property
    def id(self):
        """For backwards compatibility"""
        return self.note_id

    def to_dict(self):
        return {
            'name': self.name,
            'text': self.text,
            'category': self.category,
            'is_public': self.is_public,
            'is_approved': self.is_approved,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'note_id': self.note_id
        }

    @classmethod
    def from_dict(cls, data):
        # Handle SaverDict by creating a new dict with its items
        note_data = {k: v for k, v in data.items()}
        
        # Convert datetime strings back to datetime objects
        for field in ['created_at', 'updated_at', 'approved_at']:
            if note_data.get(field):
                try:
                    if isinstance(note_data[field], str):
                        note_data[field] = datetime.fromisoformat(note_data[field])
                except (ValueError, TypeError):
                    note_data[field] = None
            else:
                note_data[field] = None
                
        return cls(**note_data)