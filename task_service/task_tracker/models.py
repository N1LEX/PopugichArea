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

    def __str__(self):
        return self.username

    @staticmethod
    def workers() -> QuerySet:
        return User.objects.exclude(role__in=(User.RoleChoices.ADMIN, User.RoleChoices.MANAGER))


class Task(models.Model):
    class StatusChoices(models.TextChoices):
        ASSIGNED = 'assigned', 'assigned'
        COMPLETED = 'completed', 'completed'

    public_id = models.UUIDField(default=uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=25)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=9, choices=StatusChoices.choices, default=StatusChoices.ASSIGNED)
    date = models.DateField(auto_now_add=True, editable=False)

    @staticmethod
    def assigned() -> QuerySet:
        return Task.objects.filter(status=Task.StatusChoices.ASSIGNED)

    def assign(self, user_id):
        self.user_id = user_id
        self.save()

    def complete(self):
        self.status = Task.StatusChoices.COMPLETED
        self.save()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.user = random.choice(User.workers())
        super().save(*args, **kwargs)
