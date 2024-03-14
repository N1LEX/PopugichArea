from django.db.models import F

from accounting.models import User, Task, Account, Log
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
            'description': task_data['description'],
            'date': task_data['date'],
        }
    )
    account = task.user.account
    account.balance = F('balance') - task.assigned_price
    account.save()
    Log.objects.create(
        account=account,
        amount=task.assigned_price,
        purpose=f'Списание за назначенную задачу ({task.public_id}). Сумма: {task.assigned_price}.',
    )
    return {'message': 'OK'}


@app.task
def handle_completed_task(**task_data):
    task = Task.objects.get(public_id=task_data['public_id'])
    task.status = Task.StatusChoices.COMPLETED
    task.save()
    account = task.user.account
    account.balance = F('balance') + task.completed_price
    account.save()
    Log.objects.create(
        account=account,
        amount=task.completed_price,
        purpose=f'Начисление за выполненную задачу ({task.public_id}). Сумма: {task.completed_price}.',
    )
    return {'message': 'OK'}
