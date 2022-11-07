from django.apps import AppConfig
from .jobs import get_recomendaciones


class RecomendacionesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recomendaciones"

    def ready(self):
        from . import updater

        # updater.start()
        # get_recomendaciones()
