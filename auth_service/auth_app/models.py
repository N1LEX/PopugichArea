from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        ADMIN = 'admin', 'admin'
        MANAGER = 'manager', 'manager'
        TESTER = 'tester', 'tester'
        DEVELOPER = 'developer', 'developer'
        ACCOUNTANT = 'accountant', 'accountant'

    public_id = models.UUIDField(primary_key=True, default=uuid4)
    username = models.CharField(max_length=15, unique=True)
    email = models.CharField(max_length=40, unique=True)
    role = models.CharField(max_length=10, choices=RoleChoices.choices, default=RoleChoices.DEVELOPER)
    full_name = models.CharField(max_length=40, null=True)

    @classmethod
    def create(cls, user_data: dict) -> 'User':
        user = cls(**user_data)
        user.set_password(user.password)
        user.save()
        return user
