import random

from task_service.celery import app
from task_tracker.models import Task, User


@app.task
def assign_tasks():
    users = User.workers()
    for task in Task.opened():
        assign_task.delay(task.id, random.choice(users).id)


@app.task
def assign_task(task_id: int, user_id: int):
    task = Task.objects.get(id=task_id)
    if task.status == Task.StatusChoices.OPEN:
        task.assign(user_id)
        return {'message': f'task ({task_id}) reassigned'}
    return {'message': f'task ({task_id}) has already completed'}


@app.task
def create_user(**kwargs):
    u = User.objects.create(
        username=kwargs['username'],
        public_id=kwargs['public_id'],
        role=kwargs['role'],
        full_name=kwargs['full_name'],
    )
    return {'message': 'User created', 'public_id': str(u.public_id)}
