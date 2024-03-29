from accounting_app.streaming import EventVersions
from celery.schedules import crontab

from celery import Celery

app = Celery('accounting_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'close_billing_cycles_v1': {
        'task': 'accounting_app.tasks.close_billing_cycles',
        'schedule': crontab(hour=23, minute=59),
        'kwargs': {'event_version': EventVersions.v1},
    },
}
