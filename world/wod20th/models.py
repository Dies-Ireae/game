# world/wod20th/models.py
from django.db import models
from django.db.models import JSONField

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
    values = JSONField(default=list, blank=True, null=True)
    lock_string = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name