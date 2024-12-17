from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0001_initial'),  # Make sure this matches your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='wikipage',
            name='featured_order',
            field=models.IntegerField(default=0),
        ),
    ] 