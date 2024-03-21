import random
from datetime import date
from uuid import uuid4

import attrs
from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.functional import cached_property


class User(models.Model):
    class RoleChoices(models.TextChoices):
        ADMIN = 'admin', 'admin'
        MANAGER = 'manager', 'manager'
        TESTER = 'tester', 'tester'
        DEVELOPER = 'developer', 'developer'
        ACCOUNTANT = 'accountant', 'accountant'

    public_id = models.UUIDField()
    username = models.CharField(max_length=40)
    role = models.CharField(max_length=40)
    full_name = models.CharField(max_length=40, blank=True, null=True)
    email = models.CharField(max_length=40, null=True, blank=True)

    @property
    def is_manager(self) -> bool:
        return self.role in (self.RoleChoices.ADMIN, self.RoleChoices.MANAGER)

    @property
    def is_worker(self) -> bool:
        return self.role in (self.RoleChoices.TESTER, self.RoleChoices.DEVELOPER, self.RoleChoices.ACCOUNTANT)

    @staticmethod
    def workers() -> QuerySet:
        return User.objects.exclude(role__in=(User.RoleChoices.ADMIN, User.RoleChoices.MANAGER))

    @cached_property
    def billing_cycle(self) -> 'BillingCycle':
        return self.billing_cycles.filter(status=BillingCycle.StatusChoices.OPENED).last()

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

    class Meta:
        ordering = ['-id']


class BillingCycle(models.Model):
    class StatusChoices(models.TextChoices):
        OPENED = 'opened', 'opened'
        CLOSED = 'closed', 'closed'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billing_cycles')
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    status = models.CharField(max_length=6, default=StatusChoices.OPENED)

    @classmethod
    def new(cls, user: User, start: date = None, end: date = None) -> 'BillingCycle':
        return cls.objects.create(user=user, start_date=start, end_date=end)

    def close(self):
        self.status = self.StatusChoices.CLOSED
        self.save()


class Account(models.Model):
    public_id = models.UUIDField(default=uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    @transaction.atomic
    def create_transaction(self, transaction_model) -> 'Transaction':
        _transaction = Transaction.objects.create(
            **attrs.asdict(transaction_model, filter=attrs.filters.exclude('display_amount'))
        )
        if _transaction.type in (_transaction.TypeChoices.WITHDRAW, _transaction.TypeChoices.PAYMENT):
            self.balance += -_transaction.credit
        else:
            self.balance -= _transaction.debit
        self.save()
        return _transaction


class Transaction(models.Model):
    class TypeChoices(models.TextChoices):
        DEPOSIT = 'deposit', 'deposit'
        WITHDRAW = 'withdraw', 'withdraw'
        PAYMENT = 'payment', 'payment'

    public_id = models.UUIDField(default=uuid4, unique=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    billing_cycle = models.ForeignKey(BillingCycle, on_delete=models.PROTECT, related_name='transactions')
    type = models.CharField(max_length=8, choices=TypeChoices.choices)
    debit = models.PositiveIntegerField(default=0)
    credit = models.PositiveIntegerField(default=0)
    purpose = models.CharField(max_length=100)
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    @property
    def display_amount(self) -> int:
        if self.type == self.TypeChoices.WITHDRAW:
            return -self.credit
        return self.debit
