from django.apps import AppConfig


class CandidatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.candidate'

    def ready(self):
        import apps.candidate.signals