from celery import Celery
from celery.schedules import crontab

app = Celery('accounting_service')
app.conf.update(broker_url='redis://redis:6379/1')
app.autodiscover_tasks(['accounting'])

app.conf.beat_schedule = {
    'payout-profits': {
        'task': 'accounting.tasks.payout_profits',
        'schedule': crontab(hour=0, minute=0),
    },
}
