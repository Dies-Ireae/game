from django.apps import AppConfig


class WikiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wiki"

    def ready(self):
        """
        Initialize app when it's ready.
        """
        pass
