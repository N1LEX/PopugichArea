import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_service.settings')

app = Celery('task_service')
app.conf.broker_url = 'redis://redis:6379/0'
app.autodiscover_tasks()
