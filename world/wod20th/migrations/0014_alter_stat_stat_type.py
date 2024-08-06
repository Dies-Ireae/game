# Generated by Django 4.2.13 on 2024-08-05 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wod20th", "0013_alter_stat_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stat",
            name="stat_type",
            field=models.CharField(
                choices=[
                    ("attribute", "Attribute"),
                    ("ability", "Ability"),
                    ("advantage", "Advantage"),
                    ("background", "Background"),
                    ("lineage", "Lineage"),
                    ("discipline", "Discipline"),
                    ("gift", "Gift"),
                    ("sphere", "Sphere"),
                    ("rote", "Rote"),
                    ("art", "Art"),
                    ("edge", "Edge"),
                    ("discipline", "Discipline"),
                    ("path", "Path"),
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
                    ("specialty", "Specialty"),
                    ("other", "Other"),
                    ("physical", "Physical"),
                    ("social", "Social"),
                    ("mental", "Mental"),
                    ("personal", "Personal"),
                    ("supernatural", "Supernatural"),
                    ("other", "Other"),
                ],
                max_length=100,
            ),
        ),
    ]
