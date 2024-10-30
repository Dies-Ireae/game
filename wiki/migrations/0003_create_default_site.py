from django.db import migrations
from django.conf import settings


def create_default_site(apps, schema_editor):
    """
    Create a default site object if none exists
    """
    Site = apps.get_model('sites', 'Site')
    if not Site.objects.exists():
        # Create the default site
        Site.objects.create(
            id=settings.SITE_ID,
            domain='localhost:4200',
            name='Dies Irae Development'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('wiki', '0002_create_default_site'),
    ]

    operations = [
        migrations.RunPython(create_default_site),
    ] 