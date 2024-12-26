# world/wod20th/forms.py
from django import forms
from .models import Stat, ShapeshifterForm
from django.core.management.base import BaseCommand

class StatForm(forms.ModelForm):
    class Meta:
        model = Stat
        fields = ['name', 'description', 'game_line', 'category', 'stat_type', 'values']
        widgets = {
            'values': forms.Textarea(attrs={'rows': 3}),
        }

class Command(BaseCommand):
    help = 'Initialize shapeshifter forms in the database'

    def handle(self, *args, **options):
        create_shifter_forms()
        self.stdout.write(self.style.SUCCESS('Successfully initialized shapeshifter forms'))

def create_shifter_forms():
    forms_data = {
        'garou': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Glabro': {'stat_modifiers': {'Strength': 2, 'Stamina': 2, 'Manipulation': -1, 'Appearance': -1}, 'difficulty': 7},
            'Crinos': {'stat_modifiers': {'Strength': 4, 'Dexterity': 1, 'Stamina': 3, 'Manipulation': -3}, 'difficulty': 6},
            'Hispo': {'stat_modifiers': {'Strength': 3, 'Dexterity': 2, 'Stamina': 3, 'Manipulation': -3}, 'difficulty': 7},
            'Lupus': {'stat_modifiers': {'Strength': 1, 'Dexterity': 2, 'Stamina': 2, 'Manipulation': -3}, 'difficulty': 6}
        },
        'ajaba': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Anthros': {'stat_modifiers': {'Strength': 2, 'Stamina': 2, 'Manipulation': -1, 'Appearance': -1}, 'difficulty': 7},
            'Crinos': {'stat_modifiers': {'Strength': 3, 'Dexterity': 2, 'Stamina': 4, 'Manipulation': -2}, 'difficulty': 6},
            'Crocas': {'stat_modifiers': {'Strength': 2, 'Dexterity': 3, 'Stamina': 3, 'Manipulation': -2}, 'difficulty': 7},
            'Hyaenid': {'stat_modifiers': {'Strength': 1, 'Dexterity': 2, 'Stamina': 2, 'Manipulation': -2}, 'difficulty': 6}
        },
        'kitsune': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Sambuhenge': {'stat_modifiers': {'Dexterity': 1, 'Stamina': 1, 'Manipulation': -1}, 'difficulty': 7},
            'Koto': {'stat_modifiers': {'Strength': 1, 'Dexterity': 2, 'Stamina': 2, 'Manipulation': -1, 'Perception': 1}, 'difficulty': 6},
            'Juko': {'stat_modifiers': {'Dexterity': 3, 'Stamina': 3, 'Manipulation': -2, 'Perception': 1}, 'difficulty': 7},
            'Kyubi': {'stat_modifiers': {'Dexterity': 4, 'Stamina': 2, 'Manipulation': -1, 'Perception': 2}, 'difficulty': 6}
        },
        'gurahl': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Arthren': {'stat_modifiers': {'Strength': 3, 'Stamina': 3, 'Manipulation': -1, 'Appearance': -1}, 'difficulty': 7},
            'Crinos': {'stat_modifiers': {'Strength': 5, 'Dexterity': -1, 'Stamina': 5, 'Manipulation': -3}, 'difficulty': 6},
            'Bjornen': {'stat_modifiers': {'Strength': 4, 'Dexterity': -1, 'Stamina': 4, 'Manipulation': -3}, 'difficulty': 7},
            'Ursus': {'stat_modifiers': {'Strength': 3, 'Dexterity': -1, 'Stamina': 3, 'Manipulation': -3}, 'difficulty': 6}
        },
        'nuwisha': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Tsitsu': {'stat_modifiers': {'Strength': 1, 'Dexterity': 1, 'Stamina': 2, 'Manipulation': -1}, 'difficulty': 7},
            'Manabozho': {'stat_modifiers': {'Strength': 2, 'Dexterity': 3, 'Stamina': 3, 'Manipulation': -2}, 'difficulty': 6},
            'Sendeh': {'stat_modifiers': {'Strength': 2, 'Dexterity': 3, 'Stamina': 3, 'Manipulation': -3}, 'difficulty': 7},
            'Latrani': {'stat_modifiers': {'Dexterity': 3, 'Stamina': 3, 'Manipulation': -3}, 'difficulty': 6}
        },
        'bastet': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Sokto': {'stat_modifiers': {'Strength': 1, 'Dexterity': 2, 'Stamina': 1, 'Manipulation': -1, 'Appearance': -1}, 'difficulty': 7},
            'Crinos': {'stat_modifiers': {'Strength': 2, 'Dexterity': 3, 'Stamina': 3, 'Manipulation': -3}, 'difficulty': 6},
            'Chatro': {'stat_modifiers': {'Strength': 2, 'Dexterity': 4, 'Stamina': 2, 'Manipulation': -2}, 'difficulty': 7},
            'Feline': {'stat_modifiers': {'Strength': 1, 'Dexterity': 4, 'Stamina': 1, 'Manipulation': -2}, 'difficulty': 6}
        },
        'corax': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Crinos': {'stat_modifiers': {'Strength': 2, 'Dexterity': 2, 'Stamina': 2, 'Manipulation': -2}, 'difficulty': 6},
            'Corvid': {'stat_modifiers': {'Strength': -1, 'Dexterity': 3, 'Stamina': -1, 'Manipulation': -2}, 'difficulty': 6}
        },
        'ananasi': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Lilian': {'stat_modifiers': {'Strength': 2, 'Dexterity': 3, 'Stamina': 2, 'Manipulation': -1}, 'difficulty': 6},
            'Pithus': {'stat_modifiers': {'Strength': 4, 'Dexterity': 1, 'Stamina': 3, 'Manipulation': -3}, 'difficulty': 6},
            'Crawlerling': {'stat_modifiers': {'Strength': -5, 'Dexterity': 5, 'Stamina': -5, 'Manipulation': -5}, 'difficulty': 6}
        },
        'mokole': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Archid': {'stat_modifiers': {'Strength': 4, 'Dexterity': -1, 'Stamina': 4, 'Manipulation': -3}, 'difficulty': 6},
            'Suchid': {'stat_modifiers': {'Strength': -1, 'Dexterity': 0, 'Stamina': 1, 'Manipulation': -3}, 'difficulty': 7}
        },
        'ratkin': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Crinos': {'stat_modifiers': {'Strength': 2, 'Dexterity': 3, 'Stamina': 2, 'Manipulation': -2}, 'difficulty': 6},
            'Rodens': {'stat_modifiers': {'Strength': -1, 'Dexterity': 3, 'Stamina': -1, 'Manipulation': -2}, 'difficulty': 7}
        },
        'nagah': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Silkaram': {'stat_modifiers': {'Strength': 2, 'Stamina': 2, 'Manipulation': -2, 'Appearance': -2}, 'difficulty': 7},
            'Azhi': {'stat_modifiers': {'Strength': 3, 'Dexterity': 2, 'Stamina': 3, 'Manipulation': -3}, 'difficulty': 6},
            'Kali': {'stat_modifiers': {'Strength': 2, 'Dexterity': 2, 'Stamina': 2, 'Manipulation': -3}, 'difficulty': 7},
            'Vasuki': {'stat_modifiers': {'Strength': -1, 'Dexterity': 2, 'Stamina': 1, 'Manipulation': -5}, 'difficulty': 6}
        },
        'rokea': {
            'Homid': {'stat_modifiers': {}, 'difficulty': 6},
            'Glabrus': {'stat_modifiers': {'Strength': 2, 'Stamina': 2, 'Manipulation': -2, 'Appearance': -2}, 'difficulty': 7},
            'Gladius': {'stat_modifiers': {'Strength': 3, 'Dexterity': -1, 'Stamina': 2, 'Manipulation': -4, 'Appearance': -5}, 'difficulty': 6},
            'Chasmus': {'stat_modifiers': {'Strength': 4, 'Dexterity': 1, 'Stamina': 3, 'Manipulation': -4}, 'difficulty': 7},
            'Squamus': {'stat_modifiers': {'Strength': 2, 'Dexterity': 3, 'Stamina': 2, 'Manipulation': -4}, 'difficulty': 6}
        }
    }

    # Create forms for each shifter type
    for shifter_type, forms in forms_data.items():
        print(f"Creating forms for {shifter_type}...")
        for form_name, data in forms.items():
            try:
                form, created = ShapeshifterForm.objects.get_or_create(
                    name=form_name,
                    shifter_type=shifter_type,
                    defaults={
                        'description': f'{shifter_type.capitalize()} {form_name} form',
                        'stat_modifiers': data.get('stat_modifiers', {}),
                        'difficulty': data.get('difficulty', 6)
                    }
                )
                print(f"  {'Created' if created else 'Found'} form: {form_name}")
            except Exception as e:
                print(f"  Error creating {form_name}: {str(e)}")

    print("Shifter forms initialization complete.")