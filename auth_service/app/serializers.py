from enum import Enum

import attrs

from app import validators


@attrs.define(kw_only=True)
class UserV1:
    public_id: str = attrs.field(validator=validators.UUIDValidator, converter=str)
    username: str = attrs.field(validator=attrs.validators.instance_of(str))
    full_name: str = attrs.field(default=None)
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    email: str = attrs.field(validator=attrs.validators.instance_of(str))


class SerializerNames(Enum):
    USER = 'User'
    TASK = 'Task'
    TRANSACTION = 'Transaction'
    ACCOUNT = 'Account'
    DayStats = 'DayStats'
    AllStats = 'AllStats'


SERIALIZERS = {
    'v1': {
        SerializerNames.USER: UserV1,
    }
}


def get_serializer(model_name: str, event_version: str):
    return SERIALIZERS[event_version][model_name]
