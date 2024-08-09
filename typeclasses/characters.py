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
            msg_self = f"You say, \"{message}\""
        if msg_location is None:
            if self.db.gradient_name:
                gradient_name = ANSIString(self.db.gradient_name)
                msg_location = f"{gradient_name} says, \"{message}\""
            else:
                msg_location = f"{self.name} says, \"{message}\""

        super().at_say(message, msg_self=msg_self, msg_location=msg_location, 
                       receivers=receivers, msg_receivers=msg_receivers, **kwargs)

    def at_pose(self, message, msg_self=None, msg_location=None, receivers=None, msg_receivers=None, **kwargs):
        """
        Override the default pose method to use the gradient name.
        """
        if not self.location:
            return

        if msg_self is None:
            msg_self = f"You pose: {message}"
        if msg_location is None:
            if self.db.gradient_name:
                gradient_name = ANSIString(self.db.gradient_name)
                msg_location = f"{gradient_name} {message}"
            else:
                msg_location = f"{self.name} {message}"

        super().at_pose(message, msg_self=msg_self, msg_location=msg_location, 
                        receivers=receivers, msg_receivers=msg_receivers, **kwargs)

    def at_emote(self, emote, msg_self=None, msg_location=None, receivers=None, msg_receivers=None, **kwargs):
        """
        Override the default emote method to use the gradient name.
        """
        if not self.location:
            return

        if msg_self is None:
            msg_self = f"You emote: {emote}"
        if msg_location is None:
            if self.db.gradient_name:
                gradient_name = ANSIString(self.db.gradient_name)
                msg_location = f"{gradient_name} {emote}"
            else:
                msg_location = f"{self.name} {emote}"

        super().at_emote(emote, msg_self=msg_self, msg_location=msg_location, 
                         receivers=receivers, msg_receivers=msg_receivers, **kwargs)

    def get_stat(self, category, stat_type, stat_name, temp=False):
        if not hasattr(self.db, "stats") or not self.db.stats:
            self.db.stats = {}
        category_stats = self.db.stats.get(category, {})
        type_stats = category_stats.get(stat_type, {})
        stat = type_stats.get(stat_name, None)
        if stat:
            return stat['temp'] if temp else stat['perm']
        return None

    def set_stat(self, category, stat_type, stat_name, value, temp=False):
        if not hasattr(self.db, "stats") or not self.db.stats:
            self.db.stats = {}
        if category not in self.db.stats:
            self.db.stats[category] = {}
        if stat_type not in self.db.stats[category]:
            self.db.stats[category][stat_type] = {}
        if stat_name not in self.db.stats[category][stat_type]:
            self.db.stats[category][stat_type][stat_name] = {'perm': 0, 'temp': 0}
        if temp:
            self.db.stats[category][stat_type][stat_name]['temp'] = value
        else:
            self.db.stats[category][stat_type][stat_name]['perm'] = value
            
    def check_stat_value(self, category, stat_type, stat_name, value, temp=False):
        from world.wod20th.models import Stat  
        stat = Stat.objects.filter(name=stat_name, category=category, stat_type=stat_type).first()
        if stat:
            stat_values = stat.values
            return value in stat_values['temp'] if temp else value in stat_values['perm']
        return False


    def at_post_login(self):
        """
        This hook is called every time the character logs in.
        """
        print("at_post_login is being called")
        super().at_post_login()

        # Check if the character has staff permissions
        if self.locks.check_lockstring(self, "perm(Admin) or perm(Builder) or perm(Immortal)"):
            print("Staff permissions detected")
            self.msg("Welcome back, staff member!")
            
            # List jobs assigned to this character
            account = self.account if hasattr(self, 'account') else self
            jobs = Job.objects.filter(assignee=account, status__in=['open', 'claimed'])

            if jobs.exists():
                self.msg("Jobs assigned to you:")
                table = evtable.EvTable("ID", "Title", "Status", "Requester", "Queue")
                for job in jobs:
                    table.add_row(
                        job.id, job.title, job.status,
                        job.requester.key, job.queue.name if job.queue else "None"
                    )
                self.msg(table)
            else:
                self.msg("You have no assigned jobs.")
        else:
            print("No staff permissions detected")

        # Automatically run the +queue/list command
        self.execute_cmd("+queue/list")
        self.msg("Queue list has been displayed.")
