from django.core.management.base import BaseCommand
from world.wod20th.forms import create_shifter_forms

class Command(BaseCommand):
    help = 'Initialize shapeshifter forms in the database'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            create_shifter_forms()
            self.stdout.write(self.style.SUCCESS('Successfully initialized shapeshifter forms'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error initializing shifter forms: {str(e)}')) 