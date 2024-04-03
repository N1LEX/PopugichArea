import random
from uuid import uuid4

from django.db import models
from django.db.models import QuerySet


class User(models.Model):
    class RoleChoices(models.TextChoices):
        ADMIN = 'admin', 'admin'
        MANAGER = 'manager', 'manager'
        TESTER = 'tester', 'tester'
        DEVELOPER = 'developer', 'developer'
        ACCOUNTANT = 'accountant', 'accountant'

    username = models.CharField(max_length=40)
    public_id = models.UUIDField()
    role = models.CharField(max_length=40)
    full_name = models.CharField(max_length=40, blank=True, null=True)
    email = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return self.username

    @staticmethod
    def workers() -> QuerySet:
        return User.objects.exclude(role__in=(User.RoleChoices.ADMIN, User.RoleChoices.MANAGER))


class Task(models.Model):
    class StatusChoices(models.TextChoices):
        CREATED = 'created', 'created'
        ASSIGNED = 'assigned', 'assigned'
        COMPLETED = 'completed', 'completed'

    public_id = models.UUIDField(default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', null=True)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=9, choices=StatusChoices.choices, default=StatusChoices.ASSIGNED)
    date = models.DateField(auto_now_add=True)

    @property
    def link(self):
        return f'http://192.168.0.103:8002/{self.id}/'

    @classmethod
    def create(cls, task_model) -> 'Task':
        return cls.objects.create(
            user=random.choice(User.workers()),
            description=task_model.description,
        )

    @staticmethod
    def assigned() -> QuerySet:
        return Task.objects.filter(status=Task.StatusChoices.ASSIGNED)

    def assign(self, user_id):
        self.user_id = user_id
        self.save()

    def complete(self):
        self.status = Task.StatusChoices.COMPLETED
        self.save()
