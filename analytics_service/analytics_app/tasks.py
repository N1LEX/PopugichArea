from datetime import date

import attrs
from celery import shared_task

from analytics_app.models import (
    Account,
    User,
    Transaction,
    Task,
    Stats,
)
from analytics_app.serializers import SerializerNames, SERIALIZERS


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def create_user(_, event):
    serializer = SERIALIZERS[event['event_version']][SerializerNames.USER]
    user_model = serializer(**event['data'])
    User.objects.create(**attrs.asdict(user_model))


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def create_account(_, event):
    serializer = SERIALIZERS[event['event_version']][SerializerNames.ACCOUNT]
    account_model = serializer(**event['data'])
    user = User.objects.get(public_id=account_model.user_id)
    Account.objects.create(public_id=account_model.public_id, user=user)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def update_account(_, event):
    serializer = SERIALIZERS[event['event_version']][SerializerNames.ACCOUNT]
    account_model = serializer(**event['data'])
    Account.objects.filter(public_id=account_model.public_id).update(balance=account_model.balance)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def create_transaction(_, event):
    serializer = SERIALIZERS[event['event_version']][SerializerNames.TRANSACTION]
    transaction_model = serializer(**event['data'])
    Transaction.create(transaction_model)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def create_task(_, event):
    serializer = SERIALIZERS[event['event_version']][SerializerNames.TASK]
    task_model = serializer(**event['data'])
    Task.create(task_model)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def update_task_lifecycle(_, event):
    serializer = SERIALIZERS[event['event_version']][SerializerNames.TASK]
    task_model = serializer(**event['data'])
    task = Task.objects.filter(public_id=task_model.public_id).first()
    if task:
        task.update_lifecycle(task_model)
    else:
        create_task.delay(event)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def add_task_price(_, event):
    serializer = SERIALIZERS[event['event_version']][SerializerNames.TASK]
    task_model = serializer(**event['data'])
    task = Task.objects.filter(public_id=task_model.public_id).first()
    if not task:
        Task.create(task_model)
    else:
        task.add_price(task_model)


@shared_task
def update_stats():
    stats, _ = Stats.objects.get_or_create(date=date.today())
    stats.update()
