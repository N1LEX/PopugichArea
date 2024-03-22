import os

from celery.schedules import crontab

from accounting_app.streaming import EventVersions
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accounting_service.settings')

app = Celery('tasks')
app.conf.broker_url = 'redis://redis:6379/2'
app.autodiscover_tasks(['accounting_app.tasks'])

app.conf.beat_schedule = {
    'close_billing_cycles_v1': {
        'task': 'accounting_app.tasks.close_billing_cycles',
        'schedule': crontab(hour=23, minute=59),
        'kwargs': {'event_version': EventVersions.v1.value},
    },
}
