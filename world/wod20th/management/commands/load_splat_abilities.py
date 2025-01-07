import json
import os
from django.core.management.base import BaseCommand
from world.wod20th.models import Stat

class Command(BaseCommand):
    help = 'Load splat-specific abilities from JSON'

    def handle(self, *args, **options):
        # Load the splat abilities JSON file
        json_file = 'data/splat_abilities.json'
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            return

        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            # Process each splat
            for splat, categories in data.items():
                self.stdout.write(f"Processing {splat} abilities...")
                
                # Process each category (talents, skills, knowledges, etc.)
                for category_name, abilities in categories.items():
                    for ability_name, ability_data in abilities.items():
                        try:
                            # Create or update the ability
                            stat, created = Stat.objects.update_or_create(
                                name=ability_data['name'],
                                defaults={
                                    'description': ability_data.get('description', ''),
                                    'game_line': ability_data.get('game_line', 'general'),
                                    'category': ability_data.get('category', 'abilities'),
                                    'stat_type': ability_data.get('stat_type', 'talent'),
                                    'values': ability_data.get('values', [1, 2, 3, 4, 5]),
                                    'splat': ability_data.get('splat', splat)
                                }
                            )
                            action = 'Created' if created else 'Updated'
                            self.stdout.write(self.style.SUCCESS(
                                f"  {action} {splat} {ability_data['name']} ({ability_data.get('stat_type', 'talent')})"
                            ))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(
                                f"  Error processing {ability_name}: {str(e)}"
                            ))

            self.stdout.write(self.style.SUCCESS('Successfully loaded splat abilities'))
            
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON in file: {json_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing file: {str(e)}')) 