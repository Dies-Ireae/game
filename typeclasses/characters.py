# typeclasses/characters.py
from evennia import DefaultCharacter
from evennia.utils.ansi import ANSIString

class Character(DefaultCharacter):
    def get_display_name(self, looker, **kwargs):
        """
        Get the name to display for the character.
        """
        if self.db.gradient_name:
            return ANSIString(self.db.gradient_name)
        return super().get_display_name(looker, **kwargs)

    def at_say(self, message, msg_self=None, msg_location=None, receivers=None, msg_receivers=None, **kwargs):
            """
            Override the default say method to use the gradient name.
            """
            if not self.location:
                return

            if msg_self is None:
                msg_self = f"You say: {message}"
            if msg_location is None:
                if self.db.gradient_name:
                    gradient_name = ANSIString(self.db.gradient_name)
                    msg_location = f"{gradient_name} says: {message}"
                else:
                    msg_location = f"{self.name} says: {message}"

            super().at_say(message, msg_self=msg_self, msg_location=msg_location, 
                        receivers=receivers, msg_receivers=msg_receivers, **kwargs)

    def get_stat(self, stat_name):
        if not hasattr(self.db, "stats"):
            return None
        return self.db.stats.get(stat_name, None)
    
    def set_stat(self, stat_name, value):
        if not hasattr(self.db, "stats"):
            self.db.stats = {}
        self.db.stats[stat_name] = value
    
    def check_stat_value(self, stat_name, value):
        from world.wod20th.models import Stat  
        stat = Stat.objects.filter(name=stat_name).first()
        if stat and (value in stat.values):
            return True
        return False

