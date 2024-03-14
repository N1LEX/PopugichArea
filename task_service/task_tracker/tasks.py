import random

from task_service.celery import app
from task_tracker.models import Task, User


@app.task
def assign_tasks():
    users = User.workers()
    for task in Task.assigned():
        assign_task.delay(task.id, random.choice(users).id)


@app.task
def assign_task(task_id: int, user_id: int):
    task = Task.objects.get(id=task_id)
    if task.status == Task.StatusChoices.ASSIGNED:
        task.assign(user_id)
        return {'message': f'task ({task_id}) reassigned'}
    return {'message': f'task ({task_id}) has already completed'}


@app.task
def create_user(**user_data):
    user = User.objects.create(
        username=user_data['username'],
        public_id=user_data['public_id'],
        role=user_data['role'],
        full_name=user_data['full_name'],
    )
    return {'message': 'User created', 'public_id': str(user.public_id)}
