from django.db import migrations

def populate_note_ids(apps, schema_editor):
    Note = apps.get_model('wod20th', 'Note')
    # Process each note in order of creation
    for owner_id in Note.objects.values_list('owner', flat=True).distinct():
        if owner_id:
            notes = Note.objects.filter(owner_id=owner_id).order_by('created_at')
            for index, note in enumerate(notes, 1):
                if note.character_note_id != index:
                    note.character_note_id = index
                    note.save()

def reverse_migrate(apps, schema_editor):
    Note = apps.get_model('wod20th', 'Note')
    Note.objects.all().update(character_note_id=1)

class Migration(migrations.Migration):
    dependencies = [
        ('wod20th', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_note_ids, reverse_migrate),
    ] 