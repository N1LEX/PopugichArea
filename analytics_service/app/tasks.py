import attrs
from celery import shared_task
from django.db import transaction

from app.models import Account, User, Transaction, Task, Stats
from app.serializers import get_serializer, SerializerNames


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def create_user(_, event):
    serializer = get_serializer(SerializerNames.USER, event['event_version'])
    user_model = serializer(**event['data'])
    User.objects.create(**attrs.asdict(user_model))


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def create_account(_, event):
    serializer = get_serializer(SerializerNames.ACCOUNT, event['event_version'])
    account_model = serializer(**event['data'])
    Account.objects.create(**attrs.asdict(account_model))


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def update_account(_, event):
    serializer = get_serializer(SerializerNames.ACCOUNT, event['event_version'])
    account_model = serializer(**event['data'])
    Account.objects.filter(public_id=account_model.public_id).update(**attrs.asdict(account_model))


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def create_transaction(_, event):
    serializer = get_serializer(SerializerNames.TRANSACTION, event['event_version'])
    transaction_model = serializer(**event['data'])
    Transaction.objects.create(**attrs.asdict(transaction_model))


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
@transaction.atomic
def create_task(_, event):
    serializer = get_serializer(SerializerNames.TASK, event['event_version'])
    task_model = serializer(**event['data'])
    task = Task.objects.create(**attrs.asdict(task_model))
    if task.status == Task.StatusChoices.COMPLETED:
        Stats.update_stats(task)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
@transaction.atomic
def update_task(_, event):
    serializer = get_serializer(SerializerNames.TASK, event['event_version'])
    task_model = serializer(**event['data'])
    task = Task.objects.filter(public_id=task_model.public_id).update(**attrs.asdict(task_model))
    if task.status == Task.StatusChoices.COMPLETED:
        Stats.update_stats(task)
