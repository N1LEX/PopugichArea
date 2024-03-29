import random
from uuid import uuid4

import attrs
from accounting_app import validators
from accounting_app.models import Account, Task
from accounting_app.streaming import EventVersions
from django.db.models import TextChoices
from django.utils.timezone import now


@attrs.define(kw_only=True)
class UserV1:
    public_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    username: str = attrs.field(validator=attrs.validators.instance_of(str))
    full_name: str = attrs.field(default=None)
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    email: str = attrs.field(validator=attrs.validators.instance_of(str))


@attrs.define(kw_only=True)
class TaskV1:
    @staticmethod
    def random_price():
        return random.randint(1, 1000)

    public_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    user_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    description: str = attrs.field(validator=attrs.validators.instance_of(str))
    status: str = attrs.field(validator=attrs.validators.instance_of(str))
    date: str = attrs.field(validator=validators.datetime_validator)
    assigned_price: int = attrs.field(default=attrs.Factory(random_price))
    completed_price: int = attrs.field(default=attrs.Factory(random_price))

    @classmethod
    def from_object(cls, task: Task) -> 'TaskV1':
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
    public_id: str = attrs.field(converter=str)
    user_id: str = attrs.field(converter=str)
    balance: int = attrs.field(default=0)

    @classmethod
    def from_object(cls, account: Account):
        return cls(public_id=account.public_id, user_id=account.user.public_id, balance=account.balance)


@attrs.define(kw_only=True)
class TransactionV1:
    public_id: str = attrs.field(converter=str, default=attrs.Factory(uuid4))
    account_id: str = attrs.field(converter=str)
    billing_cycle_id: str = attrs.field(converter=str)
    type: str = attrs.field()
    debit: int = attrs.field(default=0)
    credit: int = attrs.field(default=0)
    purpose: str = attrs.field()
    datetime: str = attrs.field(default=attrs.Factory(lambda: now().isoformat(timespec='seconds')))

    display_amount: int = attrs.field(default=0)


class SerializerNames(TextChoices):
    USER = 'User'
    TASK = 'Task'
    TRANSACTION = 'Transaction'
    ACCOUNT = 'Account'


SERIALIZERS = {
    EventVersions.v1: {
        SerializerNames.USER: UserV1,
        SerializerNames.TASK: TaskV1,
        SerializerNames.TRANSACTION: TransactionV1,
        SerializerNames.ACCOUNT: AccountV1,
    }
}


def get_serializer(model_name: str, event_version: str):
    return SERIALIZERS[event_version][model_name]
