import random
from typing import List

import attrs
from django.db.models import TextChoices

from accounting.streaming import EventVersions
from accounting import validators



@attrs.define(kw_only=True)
class UserV1:
    public_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    username: str = attrs.field(validator=attrs.validators.instance_of(str))
    full_name: str = attrs.field(default=None)
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    email: str = attrs.field(validator=attrs.validators.instance_of(str))


@attrs.define(kw_only=True)
class TaskV1:
    @staticmethod
    def random_price():
        return random.randint(1, 1000)

    public_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    user_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    description: str = attrs.field(validator=attrs.validators.instance_of(str))
    status: str = attrs.field(validator=attrs.validators.instance_of(str))
    date: str = attrs.field(validator=validators.DatetimeValidator)
    assigned_price: int = attrs.field(default=random_price())
    completed_price: int = attrs.field(default=random_price())


@attrs.define(kw_only=True)
class AccountV1:
    public_id: str = attrs.field(converter=str)
    user_id: str = attrs.field(converter=str)
    balance: int = attrs.field(default=0)


@attrs.define(kw_only=True)
class TransactionV1:
    public_id: str = attrs.field(converter=str)
    account_id: str = attrs.field(converter=str)
    billing_cycle_id: str = attrs.field(converter=str)
    type: str = attrs.field()
    debit: int = attrs.field(default=0)
    credit: int = attrs.field(default=0)
    purpose: str = attrs.field()
    datetime: str = attrs.field()

    display_amount: int = attrs.field(default=0)

    @classmethod
    def from_list(cls, data: list[dict]) -> List['TransactionV1']:
        return [cls(**transaction) for transaction in data]


@attrs.define(kw_only=True)
class AccountStateV1:
    balance: int = attrs.field()
    transactions: List[TransactionV1] = attrs.field(converter=TransactionV1.from_list)


@attrs.define(kw_only=True)
class ManagementEarningV1:
    sum: int = attrs.field()
    date: str = attrs.field(converter=str)

    @classmethod
    def from_list(cls, data: list[dict]) -> List['ManagementEarningV1']:
        return [cls(**earning) for earning in data]


@attrs.define(kw_only=True)
class ManagementEarningStatsV1:
    current_date: ManagementEarningV1 = attrs.field(converter=ManagementEarningV1)
    history: List[ManagementEarningV1] = attrs.field(converter=ManagementEarningV1.from_list)


class SerializerNames(TextChoices):
    USER = 'User'
    TASK = 'Task'
    TRANSACTION = 'Transaction'
    ACCOUNT = 'Account'
    ACCOUNT_STATE = 'AccountState'
    MANAGEMENT_EARNING_STATS = 'ManagementEarningStats'


SERIALIZERS = {
    EventVersions.v1: {
        SerializerNames.USER: UserV1,
        SerializerNames.TASK: TaskV1,
        SerializerNames.TRANSACTION: TransactionV1,
        SerializerNames.ACCOUNT: AccountV1,
        SerializerNames.ACCOUNT_STATE: AccountStateV1,
        SerializerNames.MANAGEMENT_EARNING_STATS: ManagementEarningStatsV1,
    }
}


def get_serializer(model_name: str, event_version: str):
    return SERIALIZERS[event_version][model_name]
