import attrs
from auth_app.streaming import EventVersions
from django.db.models import TextChoices
from uuid import uuid4


@attrs.define(kw_only=True)
class UserV1:
    public_id: str = attrs.field(converter=str, default=attrs.Factory(uuid4))
    username: str = attrs.field(validator=attrs.validators.instance_of(str))
    full_name: str = attrs.field(default=None)
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    email: str = attrs.field(validator=attrs.validators.instance_of(str))


@attrs.define(kw_only=True)
class UserSignUpV1(UserV1):
    password: str = attrs.field(converter=str, validator=attrs.validators.min_len(6))


class SerializerNames(TextChoices):
    USER = 'User'
    USER_SIGNUP = 'UserSignUp'


SERIALIZERS = {
    EventVersions.v1.value: {
        SerializerNames.USER.value: UserV1,
        SerializerNames.USER_SIGNUP.value: UserSignUpV1,
    }
}


def get_serializer(model_name: str, event_version: str):
    return SERIALIZERS[event_version][model_name]
