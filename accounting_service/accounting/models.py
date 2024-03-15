import random
from uuid import uuid4

from django.db import models, transaction
from django.db.models import QuerySet, F


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

    @staticmethod
    def workers() -> QuerySet:
        return User.objects.exclude(role__in=(User.RoleChoices.ADMIN, User.RoleChoices.MANAGER))

    def send_mail_profit(self, amount):
        return amount

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
    assigned_price = models.PositiveSmallIntegerField(default=random_price)
    completed_price = models.PositiveSmallIntegerField(default=random_price)
    status = models.CharField(max_length=40)
    date = models.DateField()

    @transaction.atomic
    def handle_completed(self):
        self.status = Task.StatusChoices.COMPLETED
        self.save()
        account = self.user.account
        account.balance = F('balance') + self.completed_price
        account.save()
        Log.objects.create(
            account=account,
            amount=self.completed_price,
            purpose=f'Начисление за выполненную задачу ({self.public_id}). Сумма: {self.completed_price}.',
        )

    @transaction.atomic
    def handle_assigned(self):
        account = self.user.account
        account.balance = F('balance') - self.assigned_price
        account.save()
        Log.objects.create(
            account=account,
            amount=self.assigned_price,
            purpose=f'Списание за назначенную задачу ({self.public_id}). Сумма: {self.assigned_price}.',
        )


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    @transaction.atomic
    def payout(self):
        Log.objects.create(
            account=self,
            amount=self.balance,
            purpose=f'Выплата за выполненные задачи. Сумма: {self.balance}.',
        )
        self.balance = 0
        self.save()


class Log(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='logs')
    amount = models.IntegerField()
    purpose = models.CharField(max_length=255)
