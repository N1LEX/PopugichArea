from celery import Celery

app = Celery('task_service')
app.conf.update(broker_url='redis://redis:6379/0')
app.autodiscover_tasks()
