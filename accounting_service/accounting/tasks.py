from datetime import timedelta

import attrs
from celery import shared_task
from django.core.mail import send_mail
from django.db import transaction

from accounting import models
from accounting.models import User, Task, Account, BillingCycle
from accounting.serializers import get_serializer, SerializerNames
from accounting.streaming import get_event_streaming
from accounting_service.celery import app


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
@transaction.atomic
def create_user(event):
    user_model = get_serializer(SerializerNames.USER, event['event_version'])(data=event['data'])
    user = User.objects.create(**attrs.asdict(user_model))
    if user.role in (User.RoleChoices.ADMIN, User.RoleChoices.MANAGER):
        Account.objects.create(user=user)
        BillingCycle.new(user=user)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
@transaction.atomic
def handle_created_task(event):
    event_version = event['event_version']
    task_model = get_serializer(SerializerNames.TASK, event_version)(data=event['data'])
    task = Task.objects.create(**attrs.asdict(task_model))
    if task.user:
        transaction_serializer = get_serializer(SerializerNames.TRANSACTION, event_version)
        transaction_model = transaction_serializer(
            account_id=task.user.account_id,
            billing_cycle_id=task.user.billing_cycle.id,
            type=models.Transaction.TypeChoices.WITHDRAW,
            credit=task.assigned_price,
            purpose=f'Withdraw for a assigned task #{task.public_id}',
        )
        task.user.account.create_transaction(transaction_model)
        event_streaming = get_event_streaming(event_version)
        event_streaming.transaction_created(transaction_model)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
@transaction.atomic
def handle_assigned_task(event):
    event_version = event['event_version']

    task_serializer = get_serializer(SerializerNames.TASK, event_version)(data=event['data'])
    task_model = task_serializer(**event['data'])
    task = Task.objects.get(public_id=task_model.public_id)
    task.user_id = task_model.user_id
    task.save()

    transaction_serializer = get_serializer(SerializerNames.TRANSACTION, event_version)
    transaction_model = transaction_serializer(
        account_id=task.user.account_id,
        billing_cycle_id=task.user.billing_cycle.id,
        type=models.Transaction.TypeChoices.WITHDRAW,
        credit=task.assigned_price,
        purpose=f'Withdraw for a assigned task #{task.public_id}',
    )
    task.user.account.create_transaction(transaction_model)
    event_streaming = get_event_streaming(event_version)
    event_streaming.transaction_created(transaction_model)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
@transaction.atomic
def handle_completed_task(event):
    event_version = event['event_version']

    serializer = get_serializer(SerializerNames.TASK, event_version)(data=event['data'])
    task_model = serializer(**event['data'])
    task = Task.objects.get(public_id=task_model.public_id)
    task.status = Task.StatusChoices.COMPLETED
    task.save()

    transaction_serializer = get_serializer('Transaction', event_version)
    transaction_model = transaction_serializer(
        account_id=task.user.account_id,
        billing_cycle_id=task.user.billing_cycle.id,
        type=models.Transaction.TypeChoices.DEPOSIT,
        credit=task.assigned_price,
        purpose=f'Deposit for a completed task #{task.public_id}',
    )
    task.user.account.create_transaction(transaction_model)
    event_streaming = get_event_streaming(event_version)
    event_streaming.transaction_created(transaction_model)


@app.task
def close_billing_cycles(event_version: str):
    for user in User.workers():
        close_billing_cycle.delay(user.id, event_version)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1})
@transaction.atomic
def close_billing_cycle(user_id: int, event_version: str):
    send_report = False
    user = User.objects.get(id=user_id)
    account = user.account
    payment_amount = account.balance

    if account.balance > 0:
        send_report = True
        transaction_serializer = get_serializer(SerializerNames.TRANSACTION, event_version)
        transaction_model = transaction_serializer(
            account_id=user.account_id,
            billing_cycle_id=user.billing_cycle.id,
            type=models.Transaction.TypeChoices.PAYMENT,
            credit=payment_amount,
            purpose=f'Payout for completed tasks',
        )
        account.create_transaction(transaction_model)
        event_streaming = get_event_streaming(event_version)
        event_streaming.transaction_created(transaction_model)

    user.billing_cycle.close()
    next_cycle_date = user.billing_cycle.end_date + timedelta(days=1)
    BillingCycle.new(user=user, start=next_cycle_date, end=next_cycle_date)

    if send_report:
        send_payout_report.delay(user.email, payment_amount)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 10})
def send_payout_report(email, amount):
    send_mail(
        subject="Payout for completed tasks",
        message=amount,
        from_email="accounting@popug.inc",
        recipient_list=[email],
        fail_silently=False,
    )
