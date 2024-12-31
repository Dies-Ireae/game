import json
from pathlib import Path
from world.wod20th.models import Stat

def load_stats(data_dir):
    """Load all stats from JSON files"""
    import os
    
    # Load basic stats
    basic_stats_path = os.path.join(data_dir, 'attributes_merits_flaws_basic_backgrounds.json')
    with open(basic_stats_path) as f:
        basic_stats = json.load(f)
    
    # Load splat-specific abilities
    splat_abilities_path = os.path.join(data_dir, 'splat_abilities.json')
    with open(splat_abilities_path) as f:
        splat_abilities = json.load(f)
    
    # Create basic stats
    for stat_data in basic_stats:
        Stat.objects.get_or_create(
            name=stat_data['name'],
            defaults=stat_data
        )
    
    # Create splat-specific abilities
    for splat, categories in splat_abilities.items():
        for category, abilities in categories.items():
            for ability_data in abilities.values():
                print(f"Creating/updating {ability_data['name']} for {splat}")  # Debug print
                Stat.objects.get_or_create(
                    name=ability_data['name'],
                    defaults=ability_data
                ) 