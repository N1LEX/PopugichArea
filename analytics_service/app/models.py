from datetime import date

from django.db import models


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

    @classmethod
    def update_stats(cls, task: Task):
        day_stats, created = cls.objects.get_or_create(date=task.date)

        if created:
            day_stats.management_earning += task.assigned_price
            day_stats.most_expensive_task = task

        if task.user.account.balance < 0:
            day_stats.negative_balances += 1

        if task.status == task.StatusChoices.COMPLETED:
            day_stats.management_earning -= task.completed_price
            if task.completed_price > day_stats.most_expensive_task.completed_price:
                day_stats.most_expensive_task = task

        day_stats.save()
