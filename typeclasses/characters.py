# typeclasses/characters.py
from evennia import DefaultCharacter
from commands.oss.oss_commandset import OssCmdSet

class Character(DefaultCharacter):
    def at_cmdset_get(self, **kwargs):
        """
        Called when the cmdset is requested from this object. We
        just add our OssCmdSet here, no need for the super call.
        """
        self.cmdset.add_default(OssCmdSet, permanent=True)
    
    def get_stat(self, stat_name):
        if not hasattr(self.db, "stats"):
            return None
        return self.db.stats.get(stat_name, None)
    
    def set_stat(self, stat_name, value):
        if not hasattr(self.db, "stats"):
            self.db.stats = {}
        self.db.stats[stat_name] = value
    
    def check_stat_value(self, stat_name, value):
        from world.wod20th.models import Stat  # Import here to avoid circular reference
        stat = Stat.objects.filter(name=stat_name).first()
        if stat and (value in stat.values):
            return True
        return False

    @property
    def downtime_hours(self):
        # Calculating downtime hours based on Intelligence, Willpower, and Stamina
        intelligence = self.get_stat("Intelligence") or 0
        willpower = self.get_stat("Willpower") or 0
        stamina = self.get_stat("Stamina") or 0
        return (intelligence + willpower + stamina) * 4

    def spend_downtime(self, hours):
        current_hours = self.db.downtime_hours or self.downtime_hours
        if current_hours >= hours:
            self.db.downtime_hours = current_hours - hours
            return True
        return False

    def refresh_downtime(self):
        self.db.downtime_hours = self.downtime_hours

    def add_asset(self, asset):
        if not hasattr(self.db, "assets"):
            self.db.assets = []
        self.db.assets.append(asset)

    def remove_asset(self, asset):
        if hasattr(self.db, "assets"):
            self.db.assets.remove(asset)

    def get_assets(self):
        return self.db.assets if hasattr(self.db, "assets") else []

    def add_influence(self, influence):
        if not hasattr(self.db, "influence"):
            self.db.influence = []
        self.db.influence.append(influence)

    def remove_influence(self, influence):
        if hasattr(self.db, "influence"):
            self.db.influence.remove(influence)

    def get_influence(self):
        return self.db.influence if hasattr(self.db, "influence") else []
