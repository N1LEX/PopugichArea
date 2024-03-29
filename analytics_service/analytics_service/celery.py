import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analytics_service.settings')

app = Celery('analytics_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-stats-every-30-seconds': {
        'task': 'analytics_app.tasks.update_stats',
        'schedule': 30.0,
    },
}
