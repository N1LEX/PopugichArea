from celery import Celery

app = Celery('analytics_service')
app.conf.update(broker_url='redis://redis:6379/')
app.autodiscover_tasks(['app'])
