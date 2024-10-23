from django.apps import AppConfig

class Wod20thConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'world.wod20th'

    def ready(self):
        # Import models here to avoid circular imports
        from . import models

        # Explicitly register models if needed
        # self.apps.register_model('world.wod20th', models.Crisis)
        # self.apps.register_model('world.wod20th', models.Outcome)
        # self.apps.register_model('world.wod20th', models.Task)
