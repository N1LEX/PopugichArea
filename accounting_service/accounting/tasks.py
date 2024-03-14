from django.db.models import F

from accounting.models import User, Task, Account, Log
from accounting_service.celery import app


@app.task
def create_user(**kwargs):
    user = User.objects.create(
        username=kwargs['username'],
        public_id=kwargs['public_id'],
        role=kwargs['role'],
        full_name=kwargs['full_name'],
    )
    Account.objects.create(user=user, balance=0)
    return {'message': 'User created', 'public_id': str(user.public_id)}


@app.task
def handle_opened_task(**kwargs):
    data = kwargs['data']
    task, _ = Task.objects.get_or_create(**data)
    account = task.user.account
    account.balance = F('balance') - task.opened_price
    account.save()
    Log.objects.create(
        account=account,
        amount=task.opened_price,
        purpose=f'Списание за назначенную задачу ({task.public_id}). Сумма: {task.opened_price}.',
    )
    return {'message': 'OK'}


@app.task
def handle_completed_task(**kwargs):
    data = kwargs['data']
    task = Task.objects.get(public_id=data['public_id'])
    account = task.user.account
    account.balance = F('balance') + task.completed_price
    account.save()
    Log.objects.create(
        account=account,
        amount=task.completed_price,
        purpose=f'Начисление за выполненную задачу ({task.public_id}). Сумма: {task.completed_price}.',
    )
    return {'message': 'OK'}
