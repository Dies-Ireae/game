import evennia
evennia._init()

import django
django.setup()

from django.core.management.base import BaseCommand
from world.wod20th.models import Stat

class Command(BaseCommand):
    help = 'Verify and report on splat-specific abilities'

    def handle(self, *args, **options):
        # Check basic abilities
        basic_abilities = Stat.objects.filter(
            category='abilities',
            splat__isnull=True
        )
        self.stdout.write(f"Found {basic_abilities.count()} basic abilities")
        
        # Check splat-specific abilities
        for splat in ['Shifter', 'Changeling', 'Vampire', 'Mage']:
            splat_abilities = Stat.objects.filter(
                category='abilities',
                splat=splat
            )
            self.stdout.write(f"Found {splat_abilities.count()} {splat} abilities:")
            for ability in splat_abilities:
                self.stdout.write(f"  - {ability.name} ({ability.stat_type})")
        
        # Verify Primal-Urge specifically
        try:
            primal_urge = Stat.objects.get(name='Primal-Urge')
            self.stdout.write(f"\nPrimal-Urge details:")
            self.stdout.write(f"  Category: {primal_urge.category}")
            self.stdout.write(f"  Stat Type: {primal_urge.stat_type}")
            self.stdout.write(f"  Splat: {primal_urge.splat}")
        except Stat.DoesNotExist:
            self.stdout.write(self.style.ERROR("\nPrimal-Urge not found in database")) 