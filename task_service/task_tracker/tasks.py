import random

from celery import shared_task
from task_tracker.models import Task, User
from task_tracker.serializers import get_serializer, SerializerNames
from task_tracker.streaming import get_event_streaming


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
        event_streaming = get_event_streaming(event_version)
        task_model = serializer(**task.to_dict())
        event_streaming.task_updated(task_model)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def task_completed(_, task_pk: str, event_version: str):
    task = Task.objects.get(pk=task_pk)
    serializer = get_serializer(SerializerNames.TASK, event_version)
    event_streaming = get_event_streaming(event_version)
    task_model = serializer(**task.to_dict())
    event_streaming.task_updated(task_model)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def create_user(_, event: dict):
    serializer = get_serializer(SerializerNames.USER, event['event_version'])
    user_model = serializer(**event['data'])
    User.objects.create(**user_model)
