from datetime import date

import attrs
from celery import shared_task
from django.db import transaction

from analytics_app.models import Account, User, Transaction, Task, Stats
from analytics_app.serializers import get_serializer, SerializerNames


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def create_user(_, event):
    serializer = get_serializer(SerializerNames.USER, event['event_version'])
    user_model = serializer(**event['data'])
    User.objects.create(**attrs.asdict(user_model))


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
def create_account(_, event):
    serializer = get_serializer(SerializerNames.ACCOUNT, event['event_version'])
    account_model = serializer(**event['data'])
    user = User.objects.get(public_id=account_model.user_id)
    Account.objects.create(public_id=account_model.public_id, user=user)


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
    Task.create(task_model)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
@transaction.atomic
def update_task_flow(_, event):
    serializer = get_serializer(SerializerNames.TASK, event['event_version'])
    task_model = serializer(**event['data'])
    task = Task.objects.filter(public_id=task_model.public_id).first()
    if task:
        task.update_flow(task_model)
    else:
        create_task.delay(event)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
@transaction.atomic
def add_task_price(_, event):
    serializer = get_serializer(SerializerNames.TASK, event['event_version'])
    task_model = serializer(**event['data'])
    task = Task.objects.filter(public_id=task_model.public_id).first()
    if not task:
        task = Task.create(task_model)
    task.add_task_price(task_model)


@shared_task
def update_stats(_):
    stats, _ = Stats.objects.get_or_create(date=date.today())
    stats.update()
