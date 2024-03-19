from django.core.mail import send_mail

from accounting.models import User, Task, Account
from accounting_service.celery import app


@app.task
def create_user(**user_data):
    user = User.objects.create(
        username=user_data['username'],
        public_id=user_data['public_id'],
        role=user_data['role'],
        full_name=user_data['full_name'],
    )
    Account.objects.create(user=user, balance=0)
    return {'message': 'User created', 'public_id': str(user.public_id)}


@app.task
def handle_assigned_task(**task_data):
    user = User.objects.get(public_id=task_data['user_id'])
    task, _ = Task.objects.get_or_create(
        public_id=task_data['public_id'],
        defaults={
            'user': user,
            'status': 'assigned',
            'description': task_data['description'],
            'date': task_data['date'],
        }
    )
    task.handle_assigned()
    return {'message': 'OK'}


@app.task
def handle_completed_task(**task_data):
    task = Task.objects.get(public_id=task_data['public_id'])
    task.handle_completed()
    return {'message': 'OK'}


@app.task
def payout_profits():
    workers_with_profit = User.workers().filter(account__balance__gt=0).select_related('account')
    for worker in workers_with_profit:
        send_mail_profit.delay(worker.email, worker.account.balance)
        worker.account.payout()


@app.task
def send_mail_profit(email, amount):
    send_mail(
        subject="Выплата за выполненные задачи",
        message=amount,
        from_email="accounting@popug.inc",
        recipient_list=[email],
        fail_silently=False,
    )
