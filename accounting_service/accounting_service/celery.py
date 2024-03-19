from celery import Celery
from celery.schedules import crontab

app = Celery('accounting_service')
app.conf.update(broker_url='redis://redis:6379/1')
app.autodiscover_tasks(['accounting'])

app.conf.beat_schedule = {
    'close-billing-cycles': {
        'task': 'accounting.tasks.run_close_billing_cycles',
        'schedule': crontab(hour=23, minute=59),
    },
}
