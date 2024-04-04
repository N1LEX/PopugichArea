from typing import List, Optional

import attrs
from django.db.models import TextChoices, QuerySet

from analytics_app import validators
from analytics_app.models import Stats, Task
from analytics_app.streaming import EventVersions


@attrs.define(kw_only=True)
class UserV1:
    public_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    username: str = attrs.field(validator=attrs.validators.instance_of(str))
    full_name: Optional[str] = attrs.field()
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    email: str = attrs.field(validator=attrs.validators.instance_of(str))


@attrs.define(kw_only=True)
class TaskV1:
    public_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    user_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    description: str = attrs.field(validator=attrs.validators.instance_of(str))
    status: str = attrs.field(validator=attrs.validators.instance_of(str))
    date: str = attrs.field(validator=validators.datetime_validator, converter=str)
    assigned_price: int = attrs.field(default=None)
    completed_price: int = attrs.field(default=None)

    @classmethod
    def from_object(cls, task: Task) -> Optional['TaskV1']:
        if task:
            return cls(
                public_id=task.public_id,
                user_id=task.user.public_id,
                description=task.description,
                status=task.status,
                date=task.date,
                assigned_price=task.assigned_price,
                completed_price=task.completed_price,
            )


@attrs.define(kw_only=True)
class AccountV1:
    public_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    user_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    balance: int = attrs.field(validator=attrs.validators.instance_of(int))


@attrs.define(kw_only=True)
class TransactionV1:
    public_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    account_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    billing_cycle_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    type: str = attrs.field(validator=attrs.validators.instance_of(str))
    debit: int = attrs.field(validator=attrs.validators.instance_of(int))
    credit: int = attrs.field(validator=attrs.validators.instance_of(int))
    purpose: str = attrs.field(validator=attrs.validators.instance_of(str))
    datetime: str = attrs.field(validator=validators.datetime_validator, converter=str)

    display_amount: int = attrs.field(default=0)

    @classmethod
    def from_list(cls, data: list[dict]) -> List['TransactionV1']:
        return [cls(**transaction) for transaction in data]


@attrs.define
class StatsV1:
    management_earning: int = attrs.field()
    negative_balances: int = attrs.field()
    date: str = attrs.field(converter=str)
    most_expensive_task: Optional[TaskV1] = attrs.field(converter=TaskV1.from_object)

    @classmethod
    def from_object(cls, stats: Stats) -> 'StatsV1':
        return cls(
            management_earning=stats.management_earning,
            negative_balances=stats.negative_balances,
            date=stats.date,
            most_expensive_task=stats.most_expensive_task,
        )

    @classmethod
    def from_queryset(cls, queryset: QuerySet[Stats]) -> List['StatsV1']:
        return [cls.from_object(stats) for stats in queryset]


@attrs.define
class MostExpensiveTaskRequest:
    start_date: str = attrs.field(validator=validators.datetime_validator)
    end_date: str = attrs.field(validator=validators.datetime_validator)
    version: str = attrs.field(validator=attrs.validators.in_(EventVersions.values))


class SerializerNames(TextChoices):
    USER = 'User'
    TASK = 'Task'
    TRANSACTION = 'Transaction'
    ACCOUNT = 'Account'
    STATS = 'Stats'


SERIALIZERS = {
    EventVersions.v1: {
        SerializerNames.USER: UserV1,
        SerializerNames.TASK: TaskV1,
        SerializerNames.TRANSACTION: TransactionV1,
        SerializerNames.ACCOUNT: AccountV1,
        SerializerNames.STATS: StatsV1,
    }
}
