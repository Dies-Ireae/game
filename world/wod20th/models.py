# world/wod20th/models.py
from django.db import models

# Define predefined categories and extended stat types
CATEGORIES = [
    ('attributes', 'Attributes'),
    ('abilities', 'Abilities'),
    ('advantages', 'Advantages'),
    ('other', 'Other')
]

STAT_TYPES = [
    ('attribute', 'Attribute'),
    ('ability', 'Ability'),
    ('advantage', 'Advantage'),
    ('background', 'Background'),
    ('discipline', 'Discipline'),
    ('gift', 'Gift'),
    ('sphere', 'Sphere'),
    ('rote', 'Rote'),
    ('art', 'Art'),
    ('edge', 'Edge'),
    ('path', 'Path'),
    ('power', 'Power'),
    ('other', 'Other')
]

class Stat(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='')
    game_line = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    stat_type = models.CharField(max_length=100)
    values = models.JSONField(default=list)
    lock_string = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class Asset(models.Model):
    ASSET_TYPES = [
        ('retainer', 'Retainer'),
        ('haven', 'Haven'),
        ('territory', 'Territory'),
        ('contact', 'Contact'),
    ]

    name = models.CharField(max_length=100, unique=True)
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPES)
    description = models.TextField(blank=True, null=True)
    value = models.IntegerField(default=0)
    owner_id = models.IntegerField()  # Store the owner's ID instead of a ForeignKey
    status = models.CharField(max_length=50, default='Active')
    traits = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_asset_type_display()})"

    @property
    def owner(self):
        from typeclasses.characters import Character  # Local import
        try:
            return Character.objects.get(id=self.owner_id)
        except Character.DoesNotExist:
            return None


class ActionTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    downtime_cost = models.IntegerField(default=0)  # Cost in downtime hours
    requires_target = models.BooleanField(default=False)
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Action(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    template = models.ForeignKey(ActionTemplate, on_delete=models.CASCADE)
    character_id = models.IntegerField()  # Store the character's ID instead of a ForeignKey
    target_asset = models.ForeignKey(Asset, null=True, blank=True, on_delete=models.SET_NULL, related_name='targeted_by_actions')
    downtime_spent = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    result = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.character_id} - {self.template.name} targeting {self.target_asset} ({self.get_status_display()})"

    @property
    def character(self):
        from typeclasses.characters import Character  # Local import
        try:
            return Character.objects.get(id=self.character_id)
        except Character.DoesNotExist:
            return None

    def perform_action(self):
        if self.status == 'pending':
            # Implement the logic to resolve the action
            self.status = 'completed'
            self.result = "Action completed successfully."
            self.save()
