import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analytics_service.settings')

app = Celery('analytics_service')
app.conf.broker_url = 'redis://redis:6379/1'
app.autodiscover_tasks()
