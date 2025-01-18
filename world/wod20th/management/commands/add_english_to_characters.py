from django.core.management.base import BaseCommand
from evennia.objects.models import ObjectDB
from typeclasses.characters import Character
import ast

class Command(BaseCommand):
    help = "Adds English as a default language to all existing characters"

    def extract_languages(self, language_data):
        """
        Recursively extract language strings from nested structures
        """
        if isinstance(language_data, str):
            try:
                # Try to parse string representations of lists
                parsed = ast.literal_eval(language_data)
                if isinstance(parsed, (list, tuple)):
                    return self.extract_languages(parsed)
                return [language_data]
            except (ValueError, SyntaxError):
                return [language_data]
        elif isinstance(language_data, (list, tuple)):
            result = []
            for item in language_data:
                result.extend(self.extract_languages(item))
            return result
        return []

    def handle(self, *args, **options):
        # Get all character objects
        characters = ObjectDB.objects.filter(db_typeclass_path='typeclasses.characters.Character')
        
        count = 0
        for obj in characters:
            char = Character.objects.get_id(obj.id)
            if char:
                # Get current languages in whatever format they're in
                old_languages = char.db.languages
                
                # Extract all language strings
                language_list = self.extract_languages(old_languages)
                
                # Clean up each language string
                cleaned_languages = []
                for lang in language_list:
                    # Remove quotes, brackets, and extra whitespace
                    cleaned = lang.strip("[]'\"").strip()
                    if cleaned and cleaned not in cleaned_languages:
                        cleaned_languages.append(cleaned)
                
                # Ensure English is in the list
                if "English" not in cleaned_languages:
                    cleaned_languages.insert(0, "English")
                    count += 1
                
                # Clear and reset the languages attribute
                char.db.languages = None  # Clear it first
                char.db.languages = cleaned_languages  # Set the clean list
                
                self.stdout.write(f"Reset {char.name}'s languages to: {cleaned_languages}")
                
                # Set speaking language to English if none set
                if not char.db.speaking_language:
                    char.db.speaking_language = "English"
                    self.stdout.write(f"Set {char.name}'s speaking language to English")
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully cleaned up languages for all characters and added English where needed ({count} additions)')) 