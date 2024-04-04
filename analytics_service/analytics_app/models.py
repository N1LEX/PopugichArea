import datetime
from datetime import date

from django.db import models
from django.db.models import Sum


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
        return self.role in (
            self.RoleChoices.ADMIN,
            self.RoleChoices.MANAGER,
        )

    @property
    def is_worker(self) -> bool:
        return self.role in (
            self.RoleChoices.TESTER,
            self.RoleChoices.DEVELOPER,
            self.RoleChoices.ACCOUNTANT,
        )


class Task(models.Model):

    class StatusChoices(models.TextChoices):
        ASSIGNED = 'assigned', 'assigned'
        COMPLETED = 'completed', 'completed'

    public_id = models.UUIDField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    description = models.CharField(max_length=255)
    assigned_price = models.PositiveSmallIntegerField(null=True)
    completed_price = models.PositiveSmallIntegerField(null=True)
    status = models.CharField(max_length=40)
    date = models.DateField()

    class Meta:
        ordering = ['-id']

    @classmethod
    def create(cls, task_model) -> 'Task':
        return Task.objects.get_or_create(
            public_id=task_model.public_id,
            user=User.objects.get(public_id=task_model.user_id),
            description=task_model.description,
            assigned_price=task_model.assigned_price,
            completed_price=task_model.completed_price,
            date=task_model.date,
            status=task_model.status,
        )

    def update_lifecycle(self, task_model):
        user = User.objects.get(public_id=task_model.user_id)
        self.user = user
        self.status = task_model.status
        self.save()

    def add_price(self, task_model):
        self.assigned_price = task_model.assigned_price
        self.completed_price = task_model.completed_price
        self.save()


class Account(models.Model):
    public_id = models.UUIDField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)


class Transaction(models.Model):

    class TypeChoices(models.TextChoices):
        DEPOSIT = 'deposit', 'deposit'
        WITHDRAW = 'withdraw', 'withdraw'
        PAYMENT = 'payment', 'payment'

    public_id = models.UUIDField()
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    type = models.CharField(max_length=8)
    debit = models.PositiveIntegerField(default=0)
    credit = models.PositiveIntegerField(default=0)
    purpose = models.CharField(max_length=100)
    datetime = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, transaction_model) -> 'Transaction':
        return Transaction.objects.create(
            public_id=transaction_model.public_id,
            account=Account.objects.get(public_id=transaction_model.account_id),
            type=transaction_model.type,
            debit=transaction_model.debit,
            credit=transaction_model.credit,
            purpose=transaction_model.purpose,
            datetime=transaction_model.datetime,
        )

    class Meta:
        ordering = ['-id']

    @property
    def display_amount(self) -> int:
        if self.type == self.TypeChoices.WITHDRAW:
            return -self.credit
        return self.debit


class Stats(models.Model):
    management_earning = models.IntegerField(default=0)
    negative_balances = models.PositiveSmallIntegerField(default=0)
    most_expensive_task = models.ForeignKey(Task, on_delete=models.PROTECT, null=True)
    date = models.DateField(default=date.today)

    def update(self):
        self.management_earning = Transaction.objects.filter(
            datetime__range=(
                datetime.datetime.combine(date=self.date, time=datetime.time.min),
                datetime.datetime.combine(date=self.date, time=datetime.time.max),
            )
        ).aggregate(earning=Sum('credit', default=0) - Sum('debit', default=0))['earning']
        self.most_expensive_task = self.get_most_expensive_task(start_date=self.date, end_date=self.date)
        self.negative_balances = Account.objects.filter(balance__lt=0).count()
        self.save()

    @classmethod
    def get_most_expensive_task(cls, start_date: date, end_date: date) -> 'Task':
        return Task.objects\
            .filter(status=Task.StatusChoices.COMPLETED, date__range=(start_date, end_date))\
            .order_by('-completed_price')\
            .first()
