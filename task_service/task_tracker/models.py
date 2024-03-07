import random
from dataclasses import dataclass
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models import QuerySet


class User(models.Model):
    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'ADMIN'
        MANAGER = 'MANAGER', 'MANAGER'
        TESTER = 'TESTER', 'TESTER'
        DEVELOPER = 'DEVELOPER', 'DEVELOPER'

    public_id = models.UUIDField(default=uuid4, unique=True)
    role = models.CharField(max_length=9, choices=RoleChoices.choices)
    full_name = models.CharField(max_length=40, null=True)

    @staticmethod
    def for_assign() -> QuerySet:
        return User.objects.exclude(role__in=(User.RoleChoices.ADMIN, User.RoleChoices.MANAGER))

    @staticmethod
    def with_tasks() -> QuerySet:
        return User.for_assign().filter(tasks__isnull=False)


class Task(models.Model):
    class StatusChoices(models.TextChoices):
        OPEN = 'OPEN', 'OPEN'
        COMPLETED = 'COMPLETED', 'COMPLETED'

    public_id = models.UUIDField(default=uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', editable=False)
    description = models.CharField(max_length=255, editable=False)
    status = models.CharField(max_length=9, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    date = models.DateField(auto_now_add=True, editable=False)

    @staticmethod
    def opened() -> QuerySet:
        return Task.objects.filter(status=Task.StatusChoices.OPEN)

    @transaction.atomic()
    def assign(self, user_id):
        task = Task.objects.filter(id=self.id).select_for_update().get()
        task.user_id = user_id
        self.save()

    def save(self, *args, **kwargs):
        if self.pk is None:
            """New task: set random user excluding users with no tasks (new user)"""
            self.user = random.choice(User.with_tasks())
        super().save(*args, **kwargs)
