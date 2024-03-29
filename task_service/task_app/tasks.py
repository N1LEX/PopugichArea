import random

import attrs
from celery import shared_task
from task_app.models import Task, User
from task_app.serializers import get_serializer, SerializerNames
from task_app.streaming import EventStreaming


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def assign_tasks(_, event_version: str):
    users = User.workers()
    for task in Task.assigned():
        assign_task.delay(str(task.pk), random.choice(users).id, event_version)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def assign_task(_, task_pk: str, user_id: int, event_version: str):
    task = Task.objects.get(pk=task_pk)
    if task.status == Task.StatusChoices.ASSIGNED:
        task.assign(user_id)
        serializer = get_serializer(SerializerNames.TASK, event_version)
        event_streaming = EventStreaming(event_version)
        created_model = serializer.from_object(task)
        event_streaming.task_created(created_model)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def task_completed(_, task_pk: str, event_version: str):
    task = Task.objects.get(pk=task_pk)
    serializer = get_serializer(SerializerNames.TASK, event_version)
    event_streaming = EventStreaming(event_version)
    task_model = serializer.from_object(task)
    event_streaming.task_completed(task_model)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def create_user(_, event: dict):
    serializer = get_serializer(SerializerNames.USER, event['event_version'])
    user_model = serializer(**event['data'])
    User.objects.create(**attrs.asdict(user_model))
