from django.db import migrations

def migrate_notes_to_attributes(apps, schema_editor):
    # For now, we'll just pass - keeping the database model
    pass

def reverse_migrate(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('wod20th', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_notes_to_attributes, reverse_migrate),
    ] 