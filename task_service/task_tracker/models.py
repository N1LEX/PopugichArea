import random
from uuid import uuid4

from django.db import models
from django.db.models import QuerySet


class User(models.Model):
    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'ADMIN'
        MANAGER = 'MANAGER', 'MANAGER'
        TESTER = 'TESTER', 'TESTER'
        DEVELOPER = 'DEVELOPER', 'DEVELOPER'

    username = models.CharField(max_length=40, editable=False)
    public_id = models.UUIDField(default=uuid4, unique=True)
    role = models.CharField(max_length=9, choices=RoleChoices.choices)
    full_name = models.CharField(max_length=40, null=True)

    @staticmethod
    def workers() -> QuerySet:
        return User.objects.exclude(role__in=(User.RoleChoices.ADMIN, User.RoleChoices.MANAGER))


class Task(models.Model):
    class StatusChoices(models.TextChoices):
        OPEN = 'OPEN', 'OPEN'
        COMPLETED = 'COMPLETED', 'COMPLETED'

    public_id = models.UUIDField(default=uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=9, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    date = models.DateField(auto_now_add=True, editable=False)

    @staticmethod
    def opened() -> QuerySet:
        return Task.objects.filter(status=Task.StatusChoices.OPEN)

    def assign(self, user_id):
        self.user_id = user_id
        self.save()

    def make_completed(self):
        self.status = Task.StatusChoices.COMPLETED
        self.save()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.user = random.choice(User.workers())
        super().save(*args, **kwargs)
