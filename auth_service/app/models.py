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

    public_id = models.UUIDField(default=uuid4, unique=True)
    email = models.CharField(max_length=40, unique=True)
    role = models.CharField(max_length=10, choices=RoleChoices.choices, default=RoleChoices.DEVELOPER)
    full_name = models.CharField(max_length=40, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.set_password(self.password)
        super().save(*args, **kwargs)
