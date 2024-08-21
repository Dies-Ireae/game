# mygame/server/conf/models.py
from django.db import models
from django.db.models import JSONField  # Use the built-in JSONField
from evennia.locks.lockhandler import LockHandler
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField
import re


CATEGORIES = [
    ('attributes', 'Attributes'),
    ('abilities', 'Abilities'),
    ('advantages', 'Advantages'),
    ('backgrounds', 'Backgrounds'),
    ('powers', 'Powers'),
    ('merits', 'Merits'),
    ('flaws', 'Flaws'),
    ('traits', 'Traits'),
    ('identity', 'Identity'),
    ('virtues', 'Virtues'),
    ('pools', 'Pools'),
    ('other', 'Other')
]

STAT_TYPES = [
    ('attribute', 'Attribute'),
    ('ability', 'Ability'),
    ('advantage', 'Advantage'),
    ('background', 'Background'),
    ('lineage', 'Lineage'),
    ('discipline', 'Discipline'),
    ('gift', 'Gift'),
    ('sphere', 'Sphere'),
    ('rote', 'Rote'),
    ('art', 'Art'),
    ('splat', 'Splat'),
    ('edge', 'Edge'),
    ('discipline', 'Discipline'),
    ('path', 'Path'),
    ('power', 'Power'),
    ('other', 'Other'),
    ('virtue', 'Virtue'),
    ('vice', 'Vice'),
    ('merit', 'Merit'),
    ('flaw', 'Flaw'),
    ('trait', 'Trait'),
    ('skill', 'Skill'),
    ('knowledge', 'Knowledge'),
    ('knowlege-secondary', 'Secondary Knowledge'),
    ('telent-secondary', 'Secondary Talent'),
    ('skill-secondary', 'Secondary Skill'),
    ('talent', 'Talent'),
    ('specialty', 'Specialty'),
    ('other', 'Other'),
    ('physical', 'Physical'),
    ('social', 'Social'),
    ('mental', 'Mental'),
    ('personal', 'Personal'),
    ('supernatural', 'Supernatural'),
    ('moral', 'Moral'),
    ('inhuman', 'Inhuman'),
    ('temporary', 'Temporary'),
    ('other', 'Other')
]

class Stat(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='')
    game_line = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=CATEGORIES)
    stat_type = models.CharField(max_length=100, choices=STAT_TYPES)
    values = models.JSONField(default=list, blank=True, null=True)
    lock_string = models.CharField(max_length=255, blank=True, null=True)
    splat = models.CharField(max_length=100, blank=True, null=True, default=None)
    hidden = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    instanced = models.BooleanField(default=False, null=True)
    default = models.CharField(max_length=100, blank=True, null=True, default=None)

    def __str__(self):
        return self.name

    @property
    def lock_storage(self):
        return self.lock_string or ""

    def can_access(self, accessing_obj, access_type):
        temp_lock_handler = LockHandler(self)
        return temp_lock_handler.check(accessing_obj, access_type)

    
    def __str__(self):
        return self.name

    @property
    def lock_storage(self):
        """
        Mimics the lock_storage attribute expected by LockHandler.
        """
        return self.lock_string or ""

    def can_access(self, accessing_obj, access_type):
        """
        Check if the accessing_obj can access this Stat based on the lock_string.
        """
        # Create a temporary lock handler to handle the lock check
        temp_lock_handler = LockHandler(self)
        
        # Perform the access check
        return temp_lock_handler.check(accessing_obj, access_type)


class ShapeshifterForm(models.Model):
    name = models.CharField(max_length=100, unique=True)
    shifter_type = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    stat_modifiers = models.JSONField(default=dict, blank=True)
    rage_cost = models.PositiveIntegerField(default=0)
    difficulty = models.PositiveIntegerField(default=6)
    lock_string = models.CharField(max_length=255, blank=True)
    form_message = models.TextField(blank=True, help_text="Message to display when this form is assumed.")

    class Meta:
        verbose_name = "Shapeshifter Form"
        verbose_name_plural = "Shapeshifter Forms"
        ordering = ['shifter_type', 'name']

    def __str__(self):
        return f"{self.shifter_type.capitalize()} - {self.name}"

    def clean(self):
        # Validate stat_modifiers
        if not isinstance(self.stat_modifiers, dict):
            raise ValidationError({'stat_modifiers': 'Must be a dictionary'})
        for key, value in self.stat_modifiers.items():
            if not isinstance(key, str) or not isinstance(value, int):
                raise ValidationError({'stat_modifiers': 'Keys must be strings and values must be integers'})

        # Validate difficulty
        if self.difficulty < 1 or self.difficulty > 10:
            raise ValidationError({'difficulty': 'Difficulty must be between 1 and 10'})

    def save(self, *args, **kwargs):
        self.clean()
        self.shifter_type = self.sanitize_shifter_type(self.shifter_type)
        super().save(*args, **kwargs)

    @staticmethod
    def sanitize_shifter_type(shifter_type):
        # Convert to lowercase and remove any non-alphanumeric characters except spaces
        sanitized = re.sub(r'[^\w\s]', '', shifter_type.lower())
        # Replace spaces with underscores
        return re.sub(r'\s+', '_', sanitized)