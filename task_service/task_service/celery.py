import os

from celery import Celery

app = Celery('tasks', tasks='task_tracker.tasks')
app.conf.update(broker_url='redis://redis:6379/0')
