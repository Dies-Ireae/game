from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0008_wikipage_right_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='wikipage',
            name='is_featured',
            field=models.BooleanField(
                default=False,
                help_text="Show this article in the featured articles list"
            ),
        ),
    ] 