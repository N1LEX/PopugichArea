from accounting.streaming import EventVersions
from celery import Celery
from celery.schedules import crontab

app = Celery('accounting_service')
app.conf.update(broker_url='redis://redis:6379/0')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'close_billing_cycles_v1': {
        'task': 'accounting.tasks.close_billing_cycles',
        'schedule': crontab(hour=23, minute=59),
        'kwargs': {'event_version': EventVersions.v1.value},
    },
}
