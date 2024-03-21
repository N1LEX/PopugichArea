import attrs
from django.db import transaction

from analytic_service.celery import app
from app.models import Account, User, Transaction, Task, Stats
from app.serializers import get_serializer, SerializerNames


@app.task
def create_user(event):
    serializer = get_serializer(SerializerNames.USER, event['event_version'])
    user_model = serializer(**event['data'])
    User.objects.create(**attrs.asdict(user_model))


@app.task
def create_account(event):
    serializer = get_serializer(SerializerNames.ACCOUNT, event['event_version'])
    account_model = serializer(**event['data'])
    Account.objects.create(**attrs.asdict(account_model))


@app.task
def update_account(event):
    serializer = get_serializer(SerializerNames.ACCOUNT, event['event_version'])
    account_model = serializer(**event['data'])
    Account.objects.filter(public_id=account_model.public_id).update(**attrs.asdict(account_model))


@app.task
def create_transaction(event):
    serializer = get_serializer(SerializerNames.TRANSACTION, event['event_version'])
    transaction_model = serializer(**event['data'])
    Transaction.objects.create(**attrs.asdict(transaction_model))


@app.task
def create_task(event):
    serializer = get_serializer(SerializerNames.TASK, event['event_version'])
    task_model = serializer(**event['data'])
    task = Task.objects.create(**attrs.asdict(task_model))
    if task.status == Task.StatusChoices.COMPLETED:
        Stats.update_stats(task)


@app.task
@transaction.atomic
def update_task(event):
    serializer = get_serializer(SerializerNames.TASK, event['event_version'])
    task_model = serializer(**event['data'])
    task = Task.objects.filter(public_id=task_model.public_id).update(**attrs.asdict(task_model))
    if task.status == Task.StatusChoices.COMPLETED:
        Stats.update_stats(task)
