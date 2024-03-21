from typing import List

import attrs
from django.db.models import TextChoices
from rest_framework import serializers

from app import validators
from app.streaming import EventVersions


@attrs.define(kw_only=True)
class UserV1:
    public_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    username: str = attrs.field(validator=attrs.validators.instance_of(str))
    full_name: str = attrs.field(default=None)
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    email: str = attrs.field(validator=attrs.validators.instance_of(str))


@attrs.define(kw_only=True)
class TaskV1:
    public_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    user_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    description: str = attrs.field(validator=attrs.validators.instance_of(str))
    status: str = attrs.field(validator=attrs.validators.instance_of(str))
    date: str = attrs.field(validator=validators.DatetimeValidator)
    assigned_price: int = attrs.field(default=None)
    completed_price: int = attrs.field(default=None)

    @classmethod
    def from_dict(cls, data: dict) -> 'TaskV1':
        return cls(**data)


@attrs.define(kw_only=True)
class AccountV1:
    public_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    user_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    balance: int = attrs.field(validator=attrs.validators.instance_of(int))


@attrs.define(kw_only=True)
class TransactionV1:
    public_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    account_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    billing_cycle_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    type: str = attrs.field(validator=attrs.validators.instance_of(str))
    debit: int = attrs.field(validator=attrs.validators.instance_of(int))
    credit: int = attrs.field(validator=attrs.validators.instance_of(int))
    purpose: str = attrs.field(validator=attrs.validators.instance_of(str))
    datetime: str = attrs.field(validator=validators.DatetimeValidator, converter=str)

    display_amount: int = attrs.field(default=0)

    @classmethod
    def from_list(cls, data: list[dict]) -> List['TransactionV1']:
        return [cls(**transaction) for transaction in data]


@attrs.define
class DayStatsV1:
    management_earning: int = attrs.field()
    negative_balances: int = attrs.field()
    date: str = attrs.field(converter=str)
    most_expensive_task: TaskV1 = attrs.field(converter=TaskV1.from_dict)

    @classmethod
    def from_list(cls, data: list[dict]) -> List['DayStatsV1']:
        return [cls(**stats) for stats in data]


@attrs.define
class AllStatsV1:
    data: List[DayStatsV1] = attrs.field(converter=DayStatsV1.from_list)


class MostExpensiveTaskRequest(serializers.ModelSerializer):
    start_date: str = attrs.field(validator=validators.DatetimeValidator)
    end_date: str = attrs.field(validator=validators.DatetimeValidator)
    version: str = attrs.field(
        default=EventVersions,
        validator=attrs.validators.in_([EventVersions.values]),
    )


class SerializerNames(TextChoices):
    USER = 'User'
    TASK = 'Task'
    TRANSACTION = 'Transaction'
    ACCOUNT = 'Account'
    DayStats = 'DayStats'
    AllStats = 'AllStats'


SERIALIZERS = {
    EventVersions.v1: {
        SerializerNames.USER: UserV1,
        SerializerNames.TASK: TaskV1,
        SerializerNames.TRANSACTION: TransactionV1,
        SerializerNames.ACCOUNT: AccountV1,
        SerializerNames.DayStats: DayStatsV1,
        SerializerNames.AllStats: AllStatsV1,
    }
}


def get_serializer(model_name: str, event_version: str):
    return SERIALIZERS[event_version][model_name]
