import json
import os
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction, connection, IntegrityError

# Import Evennia and initialize it
import evennia
evennia._init()

# Ensure Django settings are configured
import django
django.setup()

# Import the Stat model
from world.wod20th.models import Stat, CATEGORIES, STAT_TYPES

class Command(BaseCommand):
    help = 'Load WoD20th stats from JSON files in a directory'

    def add_arguments(self, parser):
        parser.add_argument('--dir', type=str, default='data', help='Directory containing JSON files')
        parser.add_argument('--file', type=str, help='Specific JSON file to load (optional)')

    def handle(self, *args, **options):
        data_dir = options['dir']
        specific_file = options['file']

        if specific_file:
            # Process single file
            file_path = os.path.join(data_dir, specific_file)
            self.process_file(file_path)
        else:
            # Process all JSON files in directory
            if not os.path.isdir(data_dir):
                self.stdout.write(self.style.ERROR(f'Directory not found: {data_dir}'))
                return

            self.stdout.write(self.style.NOTICE(f'Processing JSON files in {data_dir}...'))
            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(data_dir, filename)
                    self.process_file(file_path)

    def process_file(self, file_path):
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        try:
            self.stdout.write(self.style.NOTICE(f'Processing {file_path}...'))
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Handle both single stats and lists of stats
            if isinstance(data, list):
                for stat_data in data:
                    self.process_stat(stat_data)
            elif isinstance(data, dict):
                # If it's a dictionary of stats
                for stat_name, stat_data in data.items():
                    if isinstance(stat_data, dict):
                        # If it's already a dict, just add the name
                        stat_data['name'] = stat_name
                        self.process_stat(stat_data)
                    else:
                        # If it's just a value, create a basic stat dict
                        self.process_stat({
                            'name': stat_name,
                            'value': stat_data,
                            'category': 'other',
                            'stat_type': 'other'
                        })

            self.stdout.write(self.style.SUCCESS(f'Successfully loaded stats from {file_path}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON in file: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing {file_path}: {str(e)}'))

    def process_stat(self, stat_data):
        if not isinstance(stat_data, dict):
            self.stdout.write(self.style.ERROR(f'Invalid stat data format: {stat_data}'))
            return

        name = stat_data.get('name')
        if not name:
            self.stdout.write(self.style.ERROR('Stat missing name'))
            return

        # Create or update the stat
        try:
            stat, created = Stat.objects.update_or_create(
                name=name,
                defaults={
                    'description': stat_data.get('description', ''),
                    'game_line': stat_data.get('game_line', 'general'),
                    'category': stat_data.get('category', 'other'),
                    'stat_type': stat_data.get('stat_type', 'other'),
                    'values': stat_data.get('values', []),
                    'splat': stat_data.get('splat'),
                    'hidden': stat_data.get('hidden', False),
                    'locked': stat_data.get('locked', False),
                    'instanced': stat_data.get('instanced', False),
                    'default': stat_data.get('default')
                }
            )

            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{action} stat: {name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating/updating stat {name}: {str(e)}'))

    def handle_ability(self, ability_data):
        """Handle loading an ability stat"""
        stat, created = Stat.objects.get_or_create(
            name=ability_data['name'],
            defaults={
                'description': ability_data.get('description', ''),
                'game_line': ability_data.get('game_line', 'Various'),
                'category': ability_data.get('category', 'abilities'),
                'stat_type': ability_data.get('stat_type', 'ability'),
                'values': ability_data.get('values', {}),
                'splat_specific': ability_data.get('splat_specific', False),
                'allowed_splats': ability_data.get('allowed_splats', {})
            }
        )
        
        if not created:
            # Update existing stat with new data
            stat.description = ability_data.get('description', '')
            stat.game_line = ability_data.get('game_line', 'Various')
            stat.category = ability_data.get('category', 'abilities')
            stat.stat_type = ability_data.get('stat_type', 'ability')
            stat.values = ability_data.get('values', {})
            stat.splat_specific = ability_data.get('splat_specific', False)
            stat.allowed_splats = ability_data.get('allowed_splats', {})
            stat.save()
