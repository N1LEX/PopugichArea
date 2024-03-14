import random
from uuid import uuid4

from django.db import models


class User(models.Model):

    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'ADMIN'
        MANAGER = 'MANAGER', 'MANAGER'
        TESTER = 'TESTER', 'TESTER'
        DEVELOPER = 'DEVELOPER', 'DEVELOPER'

    username = models.CharField(max_length=40)
    public_id = models.UUIDField()
    role = models.CharField(max_length=40)
    full_name = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.username


def random_price():
    return random.randint(1, 1000)


class Task(models.Model):

    class StatusChoices(models.TextChoices):
        OPENED = 'opened', 'opened'
        COMPLETED = 'completed', 'completed'
        REASSIGNED = 'reassigned', 'reassigned'

    public_id = models.UUIDField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    description = models.CharField(max_length=255)
    opened_price = models.PositiveSmallIntegerField(default=random_price)
    completed_price = models.PositiveSmallIntegerField(default=random_price)
    status = models.CharField(max_length=40)
    date = models.DateField()


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    public_id = models.UUIDField(default=uuid4)
    balance = models.IntegerField(default=0)


class Log(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='logs')
    amount = models.IntegerField()
    purpose = models.CharField(max_length=255)
