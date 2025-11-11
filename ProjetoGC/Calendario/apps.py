# Calendario/apps.py
from django.apps import AppConfig

class CalendarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Calendario'

    def ready(self):
        import Calendario.signals
