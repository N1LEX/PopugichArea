from django.db import transaction

from accounting.models import Task
from accounting_service.celery import app
from analytics_service.app.models import Account, DayStats
from analytics_service.app.serializers import (
    UserSerializerV1,
    AccountSerializerV1,
    TransactionSerializerV1,
    TaskSerializerV1,
)


@app.task
def create_user(event_data):
    serializer = UserSerializerV1(data=event_data['data'])
    serializer.is_valid(raise_exception=True)
    serializer.save()


@app.task
def create_account(event_data):
    serializer = AccountSerializerV1(data=event_data['data'])
    serializer.is_valid(raise_exception=True)
    serializer.save()


@app.task
def update_account(event_data):
    serializer = AccountSerializerV1(data=event_data['data'])
    serializer.is_valid(raise_exception=True)
    account = Account.objects.get(public_id=event_data['data']['public_id'])
    serializer.update(account, serializer.validated_data)


@app.task
def create_transaction(event_data):
    serializer = TransactionSerializerV1(data=event_data['data'])
    serializer.is_valid(raise_exception=True)
    serializer.save()


@app.task
def create_task(event_data):
    serializer = TaskSerializerV1(data=event_data['data'])
    serializer.is_valid(raise_exception=True)
    serializer.save()

    task = serializer.instance
    if task.status == Task.StatusChoices.COMPLETED:
        DayStats.update_stats(task)


@app.task
@transaction.atomic
def update_task(event_data):
    serializer = TaskSerializerV1(data=event_data['data'])
    serializer.is_valid(raise_exception=True)
    task = Task.objects.get(public_id=event_data['data']['public_id'])
    serializer.update(task, serializer.validated_data)

    if task.status == Task.StatusChoices.COMPLETED:
        DayStats.update_stats(task)
