from django.db import migrations

def migrate_note_owners(apps, schema_editor):
    Note = apps.get_model('wod20th', 'Note')
    for note in Note.objects.all():
        if note.character and not note.owner:
            note.owner = note.character
            note.save()

class Migration(migrations.Migration):

    dependencies = [
        ('wod20th', '0006_merge_20241231_0000'),  # Replace with actual previous migration
    ]

    operations = [
        migrations.RunPython(migrate_note_owners),
    ] 