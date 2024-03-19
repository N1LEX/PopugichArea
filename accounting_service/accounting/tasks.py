from datetime import timedelta

from django.core.mail import send_mail
from django.db import transaction

from accounting.models import User, Task, Account, BillingCycle
from accounting.streaming import EventStreaming
from accounting_service.celery import app


@app.task
@transaction.atomic
def create_user(**user_data):
    user = User.objects.create(
        username=user_data['username'],
        public_id=user_data['public_id'],
        role=user_data['role'],
        full_name=user_data['full_name'],
    )
    Account.objects.create(user=user)
    BillingCycle.objects.create(user=user)


@app.task
@transaction.atomic
def handle_created_task(**task_data):
    user = User.objects.get(public_id=task_data['user_id'])
    task = Task.objects.create(**task_data, user=user)
    EventStreaming.new_account_transaction(
        transaction=user.account.apply_withdraw_transaction(
            amount=-task.assigned_price,
            purpose=f'Withdraw for a assigned task #{task.public_id}',
        )
    )


@app.task
def handle_assigned_task(**task_data):
    task = Task.objects.get(public_id=task_data['public_id'])
    EventStreaming.new_account_transaction(
        transaction=task.user.account.apply_withdraw_transaction(
            amount=-task.assigned_price,
            purpose=f'Withdraw for a assigned task #{task.public_id}',
        )
    )


@app.task
def handle_completed_task(**task_data):
    task = Task.objects.get(public_id=task_data['public_id'])
    EventStreaming.new_account_transaction(
        transaction=task.user.account.apply_deposit_transaction(
            amount=task.completed_price,
            purpose=f'Deposit for a completed task #{task.public_id}',
        )
    )


@app.task
def run_close_billing_cycles():
    for user in User.workers():
        close_billing_cycle.delay(user.id)


@app.shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 1})
@transaction.atomic
def close_billing_cycle(user_id: int):
    user = User.objects.get(id=user_id)
    account = user.account
    if account.balance > 0:
        payment_amount = account.balance
        EventStreaming.account_transaction(
            transaction=account.apply_payment_transaction(
                amount=payment_amount,
                purpose='Payout for completed tasks',
            )
        )
        send_payout_report.delay(user.email, payment_amount)
    user.billing_cycle.close()
    next_cycle_date = user.billing_cycle.end_date + timedelta(days=1)
    BillingCycle.objects.create(user=user, start=next_cycle_date, end=next_cycle_date)


@app.shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 10})
def send_payout_report(email, amount):
    send_mail(
        subject="Payout for completed tasks",
        message=amount,
        from_email="accounting@popug.inc",
        recipient_list=[email],
        fail_silently=False,
    )
