from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel

class Equipment(SharedMemoryModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    resources = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    conceal = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class MeleeWeapon(Equipment):
    damage = models.CharField(max_length=100)
    damage_type = models.CharField(max_length=100)
    difficulty = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class RangedWeapon(Equipment):
    damage = models.CharField(max_length=100)
    damage_type = models.CharField(max_length=100)
    range = models.CharField(max_length=100)
    rate = models.CharField(max_length=100)
    clip = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Armor(Equipment):
    defense = models.CharField(max_length=100)
    defense_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class NaturalWeapon(Equipment):
    damage = models.CharField(max_length=100)
    damage_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name


