# world/wod20th/models.py
from django.db import models
from django.db.models import JSONField
from typeclasses.characters import Character

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
    ('discipline', 'Discipline'),
    ('path', 'Path'),
    ('power', 'Power'),
    ('other', 'Other')
]



class Stat(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='')  # Changed to non-nullable with default empty string
    game_line = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    stat_type = models.CharField(max_length=100)
    values = JSONField(default=list)
    lock_string = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class Asset(models.Model):
    ASSET_TYPES = [
        ('retainer', 'Retainer'),
        ('haven', 'Haven'),
        ('territory', 'Territory'),
        ('contact', 'Contact'),
        # Add more asset types as needed
    ]

    name = models.CharField(max_length=100, unique=True)  # Ensure the name is unique
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPES)
    description = models.TextField(blank=True, null=True)
    value = models.IntegerField(default=0)  # Represents the level or value of the asset
    owner = models.ForeignKey(Character, related_name='assets', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='Active')  # General status (e.g., Active, Under Attack)
    traits = models.JSONField(default=dict, blank=True, null=True)  # Additional characteristics or stats

    def __str__(self):
        return f"{self.name} ({self.get_asset_type_display()})"


class ActionTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ensure the name is unique
    description = models.TextField()
    downtime_cost = models.IntegerField(default=0)  # Default to 0 if unspecified
    requires_target = models.BooleanField(default=False)
    category = models.CharField(max_length=100, blank=True, null=True)  # Optional categorization field

    def __str__(self):
        return self.name

from django.db import models
from typeclasses.characters import Character

class Action(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    template = models.ForeignKey(ActionTemplate, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    target_asset = models.ForeignKey(Asset, null=True, blank=True, on_delete=models.SET_NULL, related_name='targeted_by_actions')
    downtime_spent = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    result = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.target_character or self.target_asset
        return f"{self.character} - {self.template.name} targeting {target} ({self.get_status_display()})"

    def perform_action(self):
        # Example method to simulate action results
        if self.status == 'PENDING':
            # Implement the logic to resolve the action
            self.status = 'COMPLETED'
            self.result = "Action completed successfully."
            self.save()