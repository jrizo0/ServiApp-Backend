from django.apps import AppConfig
from .jobs import recomendaciones


class RecomendacionesConfig(AppConfig):
    name = 'recomendaciones'

    def ready(self):
        # from . import updater
        # updater.start()
        # from . import jobs
        recomendaciones()
