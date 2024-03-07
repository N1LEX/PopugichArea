from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'ADMIN'
        MANAGER = 'MANAGER', 'MANAGER'
        TESTER = 'TESTER', 'TESTER'
        DEVELOPER = 'DEVELOPER', 'DEVELOPER'

    public_id = models.UUIDField(default=uuid4, unique=True)
    email = models.CharField(max_length=40, unique=True)
    role = models.CharField(max_length=9, choices=RoleChoices.choices, default=RoleChoices.DEVELOPER)
    full_name = models.CharField(max_length=40, null=True)
