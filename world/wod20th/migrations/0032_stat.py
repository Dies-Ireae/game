# Generated by Django 4.2.13 on 2024-10-24 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wod20th", "0031_action_actiontemplate_asset_shapeshifterform_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Stat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(default="")),
                ("game_line", models.CharField(max_length=100)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("attributes", "Attributes"),
                            ("abilities", "Abilities"),
                            ("secondary_abilities", "Secondary Abilities"),
                            ("advantages", "Advantages"),
                            ("backgrounds", "Backgrounds"),
                            ("powers", "Powers"),
                            ("merits", "Merits"),
                            ("flaws", "Flaws"),
                            ("traits", "Traits"),
                            ("identity", "Identity"),
                            ("archetype", "Archetype"),
                            ("virtues", "Virtues"),
                            ("legacy", "Legacy"),
                            ("pools", "Pools"),
                            ("other", "Other"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "stat_type",
                    models.CharField(
                        choices=[
                            ("attribute", "Attribute"),
                            ("ability", "Ability"),
                            ("secondary_ability", "Secondary Ability"),
                            ("advantage", "Advantage"),
                            ("background", "Background"),
                            ("lineage", "Lineage"),
                            ("discipline", "Discipline"),
                            ("gift", "Gift"),
                            ("sphere", "Sphere"),
                            ("rote", "Rote"),
                            ("art", "Art"),
                            ("splat", "Splat"),
                            ("edge", "Edge"),
                            ("discipline", "Discipline"),
                            ("realm", "Realm"),
                            ("sphere", "Sphere"),
                            ("art", "Art"),
                            ("path", "Path"),
                            ("enlightenment", "Enlightenment"),
                            ("power", "Power"),
                            ("other", "Other"),
                            ("virtue", "Virtue"),
                            ("vice", "Vice"),
                            ("merit", "Merit"),
                            ("flaw", "Flaw"),
                            ("trait", "Trait"),
                            ("skill", "Skill"),
                            ("knowledge", "Knowledge"),
                            ("talent", "Talent"),
                            ("secondary_knowledge", "Secondary Knowledge"),
                            ("secondary_talent", "Secondary Talent"),
                            ("secondary_skill", "Secondary Skill"),
                            ("specialty", "Specialty"),
                            ("other", "Other"),
                            ("physical", "Physical"),
                            ("social", "Social"),
                            ("mental", "Mental"),
                            ("personal", "Personal"),
                            ("supernatural", "Supernatural"),
                            ("moral", "Moral"),
                            ("temporary", "Temporary"),
                            ("dual", "Dual"),
                            ("renown", "Renown"),
                            ("arete", "Arete"),
                            ("banality", "Banality"),
                            ("glamour", "Glamour"),
                            ("essence", "Essence"),
                            ("quintessence", "Quintessence"),
                            ("paradox", "Paradox"),
                            ("kith", "Kith"),
                            ("seeming", "Seeming"),
                            ("house", "House"),
                            ("seelie-legacy", "Seelie Legacy"),
                            ("unseelie-legacy", "Unseelie Legacy"),
                        ],
                        max_length=100,
                    ),
                ),
                ("values", models.JSONField(blank=True, default=list, null=True)),
                (
                    "lock_string",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "splat",
                    models.CharField(
                        blank=True, default=None, max_length=100, null=True
                    ),
                ),
                ("hidden", models.BooleanField(default=False)),
                ("locked", models.BooleanField(default=False)),
                ("instanced", models.BooleanField(default=False, null=True)),
                (
                    "default",
                    models.CharField(
                        blank=True, default=None, max_length=100, null=True
                    ),
                ),
            ],
        ),
    ]
