import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teuempregoaqui.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'resync-all-candidate-profiles': {
        'task': 'apps.candidate.tasks.resync_all_candidate_profiles',
        'schedule': 3600.0,
    },
}