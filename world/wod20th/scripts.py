from evennia import DefaultScript
from world.wod20th.forms import create_shifter_forms
from datetime import datetime, timedelta
from evennia.utils.search import search_object
from typeclasses.characters import Character
from decimal import Decimal

class InitShifterFormsScript(DefaultScript):
    """
    Script to initialize shifter forms when the server starts.
    """
    def at_script_creation(self):
        self.key = "init_shifter_forms"
        self.desc = "Initializes shifter forms in the database"
        self.persistent = False  # Only runs once when server starts

    def at_start(self):
        """Called when script starts running."""
        create_shifter_forms()
        self.stop()  # Stop the script after running 

class WeeklyXPScript(DefaultScript):
    """A script that runs weekly to award XP."""
    
    def at_script_creation(self):
        """Called when script is first created."""
        self.key = "weekly_xp_awards"
        self.desc = "Awards weekly XP to active characters"
        self.interval = 60 * 60 * 24 * 7  # 1 week in seconds
        self.persistent = True
        
        # Set to run at 5 PM Pacific today or next Friday if after 5 PM
        now = datetime.now()
        target_hour = 17  # 5 PM
        
        # If it's Friday
        if now.weekday() == 4:  # 4 = Friday
            # If it's before 5 PM, run today at 5 PM
            if now.hour < target_hour:
                next_run = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
            else:
                # After 5 PM, schedule for next Friday
                next_run = now + timedelta(days=7)
                next_run = next_run.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        else:
            # Calculate days until next Friday
            days_ahead = 4 - now.weekday()  # 4 = Friday
            if days_ahead <= 0:  # If it's after Friday
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        
        self.start_delay = (next_run - now).total_seconds()
        
    def at_repeat(self):
        """Called every week."""
        characters = search_object(typeclass="typeclasses.characters.Character")
        
        for char in characters:
            if not char.has_account:
                continue
                
            # Check if they completed at least one valid scene
            if char.db.scene_data and char.db.scene_data.get('completed_scenes', 0) > 0:
                # Use the character's add_xp method if it exists, otherwise update directly
                if hasattr(char, 'award_ic_xp'):
                    char.award_ic_xp(4.00)
                    char.msg("You received 4 XP for this week's activity.")
                else:
                    # Fallback direct update
                    if not hasattr(char.db, 'xp'):
                        char.db.xp = {
                            'total': Decimal('0.00'),
                            'current': Decimal('0.00'),
                            'spent': Decimal('0.00'),
                            'ic_earned': Decimal('0.00'),
                            'spends': []
                        }
                    
                    amount = Decimal('4.00')
                    char.db.xp['total'] += amount
                    char.db.xp['current'] += amount
                    char.db.xp['ic_earned'] += amount
                    
                    # Log the award
                    if 'spends' not in char.db.xp:
                        char.db.xp['spends'] = []
                    
                    char.db.xp['spends'].insert(0, {
                        'type': 'receive',
                        'amount': float(amount),
                        'reason': "Weekly Activity",
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    char.msg("You received 4 XP for this week's activity.")
            
            # Reset scene counter
            if char.db.scene_data:
                char.db.scene_data['completed_scenes'] = 0
                char.db.scene_data['last_weekly_reset'] = datetime.now() 