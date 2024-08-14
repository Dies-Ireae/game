from django.db import models
from django.db.models import Avg
from evennia.objects.models import ObjectDB
from evennia.accounts.models import AccountDB

class District(models.Model):
    """
    Represents a large area within the game, such as a district.
    Districts encompass multiple sectors and manage overall stats like Order, Infrastructure, and Resolve.
    """
    name = models.CharField(max_length=255)
    order = models.IntegerField(default=7)
    infrastructure = models.IntegerField(default=8)
    resolve = models.IntegerField(default=6)

    # Resource management
    resources = models.JSONField(default=dict)  # Example: {"funds": 10000, "materials": 5000, "manpower": 100}

    # Overseer and proxies
    overseer = models.ForeignKey(AccountDB, related_name='districts_overseen', on_delete=models.SET_NULL, null=True, blank=True)
    proxies = models.ManyToManyField(AccountDB, related_name='districts_proxied', blank=True)

    # Room relationship
    room = models.ForeignKey(ObjectDB, related_name='districts', on_delete=models.SET_NULL, null=True, blank=True)

    _updating = False  # Flag to prevent recursive updates

    def update_values(self):
        """
        Update the Order, Infrastructure, and Resolve values based on the averages of its Sectors.
        """
        if not self._updating:
            self._updating = True
            if self.pk and self.sectors.exists():  # Check if District has been saved and has related Sectors
                averages = self.sectors.aggregate(
                    avg_order=Avg('order'),
                    avg_infrastructure=Avg('infrastructure'),
                    avg_resolve=Avg('resolve')
                )
                self.order = averages['avg_order'] or self.order
                self.infrastructure = averages['avg_infrastructure'] or self.infrastructure
                self.resolve = averages['avg_resolve'] or self.resolve
            else:
                # Set to default or predefined values if there are no sectors
                self.order = 7
                self.infrastructure = 8
                self.resolve = 6
            self.save(update_fields=['order', 'infrastructure', 'resolve'])
            self._updating = False

    def save(self, *args, **kwargs):
        if not self._updating:
            super().save(*args, **kwargs)
            # Ensure the District's values are updated when saved
            self.update_values()

class Sector(models.Model):
    """
    Represents a smaller area within a District, such as a sector.
    Sectors are managed with their own Order, Infrastructure, and Resolve, contributing to the overall District.
    """
    name = models.CharField(max_length=255)
    district = models.ForeignKey(District, related_name='sectors', on_delete=models.CASCADE)
    order = models.IntegerField(default=7)
    infrastructure = models.IntegerField(default=8)
    resolve = models.IntegerField(default=6)

    # Overseer and proxies
    overseer = models.ForeignKey(AccountDB, related_name='sectors_overseen', on_delete=models.SET_NULL, null=True, blank=True)
    proxies = models.ManyToManyField(AccountDB, related_name='sectors_proxied', blank=True)

    # Room relationship
    room = models.ForeignKey(ObjectDB, related_name='sectors', on_delete=models.SET_NULL, null=True, blank=True)

    _updating = False  # Flag to prevent recursive updates

    def update_values(self):
        """
        Update the Order, Infrastructure, and Resolve values based on the averages of its Neighborhoods.
        """
        if not self._updating:
            self._updating = True
            if self.pk and self.neighborhoods.exists():  # Check if Sector has been saved and has related Neighborhoods
                averages = self.neighborhoods.aggregate(
                    avg_order=Avg('order'),
                    avg_infrastructure=Avg('infrastructure'),
                    avg_resolve=Avg('resolve')
                )
                self.order = averages['avg_order'] or self.order
                self.infrastructure = averages['avg_infrastructure'] or self.infrastructure
                self.resolve = averages['avg_resolve'] or self.resolve
            else:
                # Set to default or predefined values if there are no neighborhoods
                self.order = 7
                self.infrastructure = 8
                self.resolve = 6
            self.save(update_fields=['order', 'infrastructure', 'resolve'])
            self._updating = False
            # After updating, ensure the District's values are updated as well
            self.district.update_values()

    def save(self, *args, **kwargs):
        if not self._updating:
            super().save(*args, **kwargs)
            # Ensure the Sector's values are updated when saved
            self.update_values()

class Neighborhood(models.Model):
    """
    Represents a neighborhood within a Sector.
    Neighborhoods can influence their Sector through specific events or off-screen actions.
    """
    name = models.CharField(max_length=255)
    sector = models.ForeignKey(Sector, related_name='neighborhoods', on_delete=models.CASCADE)
    order = models.IntegerField(default=7)
    infrastructure = models.IntegerField(default=7)
    resolve = models.IntegerField(default=6)

    # Overseer and proxies
    overseer = models.ForeignKey(AccountDB, related_name='neighborhoods_overseen', on_delete=models.SET_NULL, null=True, blank=True)
    proxies = models.ManyToManyField(AccountDB, related_name='neighborhoods_proxied', blank=True)

    # Room relationship
    room = models.ForeignKey(ObjectDB, related_name='neighborhoods', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Avoid recursion issues by checking if we're already updating
        if not getattr(self, '_sector_updating', False):
            self._sector_updating = True
            self.sector.save()
            self._sector_updating = False


class Site(models.Model):
    """
    Represents a specific site within a Neighborhood.
    Sites can be landmarks, businesses, or any place of interest that influences the Neighborhood.
    """
    name = models.CharField(max_length=255)
    neighborhood = models.ForeignKey(Neighborhood, related_name='sites', on_delete=models.CASCADE)
    importance = models.IntegerField(default=5)  # Scale from 1-10, default is 5

    # Landlord and tenants
    landlord = models.ForeignKey(AccountDB, related_name='sites_owned', on_delete=models.SET_NULL, null=True, blank=True)
    tenants = models.ManyToManyField(AccountDB, related_name='sites_tenanted', blank=True)

    # Room relationship
    room = models.ForeignKey(ObjectDB, related_name='sites', on_delete=models.SET_NULL, null=True, blank=True)

class Task(models.Model):
    """
    Represents a type of task that can be undertaken in the game.
    This model includes details like the target (District, Sector, Neighborhood, or Site),
    the dice pool required for the task, and the downtime cost.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    dice_pool = models.CharField(max_length=255)  # A string representing the dice pool, e.g., "strength+dexterity+3"
    downtime_cost = models.IntegerField(default=1)  # The downtime cost for this task

    def execute(self, task_instance):
        """
        Execute the task by rolling the dice pools of all participating characters.
        The task_instance parameter is an instance of TaskInstance.
        """
        results = []
        for character in task_instance.participants.all():
            try:
                dice_pool_expression = self.dice_pool
                # Parse the dice pool expression and roll the dice for this character
                roll_result = character.execute_dice_pool(dice_pool_expression)
                results.append((character, roll_result))
            except Exception as e:
                results.append((character, f"Error executing dice pool: {str(e)}"))
        
        return results

    def __str__(self):
        return self.name

from django.db import models

class TaskInstance(models.Model):
    """
    Represents an instance of a task being undertaken.
    Holds references to participating characters and the target neighborhoods or sites.
    """
    task = models.ForeignKey('Task', related_name='instances', on_delete=models.CASCADE)
    participants = models.ManyToManyField(AccountDB, related_name='task_instances')
    neighborhoods = models.ManyToManyField('Neighborhood', related_name='task_instances')
    sites = models.ManyToManyField('Site', related_name='task_instances', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def execute(self):
        """
        Execute the task instance by rolling the dice pools for all participating characters.
        """
        results = self.task.execute(self)
        self.completed = True
        self.save()
        return results

class Outcome(models.Model):
    """
    Represents an outcome of an event. Each outcome has a name, description, 
    and a list of effects that will be applied if the outcome is selected.
    It also has a list of tasks that can be executed by players to support it.
    The support_rating holds the total accumulated successes of all tasks conducted to support it.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    tasks = models.ManyToManyField('Task', related_name='outcomes')
    support_rating = models.IntegerField(default=0)
    effects = models.JSONField(default=list)  # Stores the list of effects to be applied

    BOOST_INFRASTRUCTURE = 'Boost Infrastructure'
    DIMINISH_INFRASTRUCTURE = 'Diminish Infrastructure'
    BOOST_RESOLVE = 'Boost Resolve'
    DIMINISH_RESOLVE = 'Diminish Resolve'
    BOOST_ORDER = 'Boost Order'
    DIMINISH_ORDER = 'Diminish Order'
    DESTROY_SITE = 'Destroy Site'

    @staticmethod
    def apply_effect(effect_name, neighborhood=None, site=None, resource_allocation=None):
        """
        Apply the specified effect to the given neighborhood or site.
        """
        try:
            if effect_name == Outcome.BOOST_INFRASTRUCTURE and neighborhood:
                neighborhood.infrastructure += 1
                neighborhood.save()

            elif effect_name == Outcome.DIMINISH_INFRASTRUCTURE and neighborhood:
                neighborhood.infrastructure -= 1
                neighborhood.save()

            elif effect_name == Outcome.BOOST_RESOLVE and neighborhood:
                neighborhood.resolve += 1
                neighborhood.save()

            elif effect_name == Outcome.DIMINISH_RESOLVE and neighborhood:
                neighborhood.resolve -= 1
                neighborhood.save()

            elif effect_name == Outcome.BOOST_ORDER and neighborhood:
                neighborhood.order += 1
                neighborhood.save()

            elif effect_name == Outcome.DIMINISH_ORDER and neighborhood:
                neighborhood.order -= 1
                neighborhood.save()

            elif effect_name == Outcome.DESTROY_SITE and site:
                site.delete()

            # Add more mechanical effect types and their logic as needed
        except AttributeError as e:
            raise ValueError(f"Error applying effect: {effect_name}. Details: {str(e)}")

    def add_effect(self, effect_name):
        """
        Add an effect to the list of effects for this outcome.
        """
        if effect_name not in self.effects:
            self.effects.append(effect_name)
            self.save()

    def remove_effect(self, effect_name):
        """
        Remove an effect from the list of effects for this outcome.
        """
        if effect_name in self.effects:
            self.effects.remove(effect_name)
            self.save()

    def apply_effects(self, neighborhoods, resource_allocation=None):
        """
        Apply all effects associated with this outcome to the given neighborhoods.
        """
        for neighborhood in neighborhoods:
            for effect in self.effects:
                Outcome.apply_effect(effect, neighborhood, resource_allocation=resource_allocation)

    def __str__(self):
        return self.name

class OSSEvent(models.Model):
    """
    Represents an event in the game world. An event has a name, description,
    and a list of possible outcomes. The event targets neighborhoods or sites and tracks whether it has been resolved.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    outcomes = models.ManyToManyField(Outcome, related_name='events')
    selected_outcome = models.ForeignKey(Outcome, related_name='selected_for_events', on_delete=models.SET_NULL, null=True, blank=True)
    neighborhoods = models.ManyToManyField('Neighborhood', related_name='events')
    sites = models.ManyToManyField('Site', related_name='events', blank=True)
    resolved = models.BooleanField(default=False)

    def resolve(self, resource_allocation=None):
        """
        Resolve the event by applying the selected outcome's effects
        to the associated neighborhoods and sites.
        """
        if self.selected_outcome:
            self.selected_outcome.apply_effects(self.neighborhoods.all(), resource_allocation)
            self.resolved = True
            self.save()
        else:
            raise ValueError("No outcome has been selected for this event.")

    def __str__(self):
        return f"OSSEvent ({self.name})"