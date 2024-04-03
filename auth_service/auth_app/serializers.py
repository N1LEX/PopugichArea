from uuid import uuid4

import attrs
from auth_app.streaming import EventVersions
from django.db.models import TextChoices


@attrs.define(kw_only=True)
class UserV1:
    public_id: str = attrs.field(converter=str, default=attrs.Factory(uuid4))
    username: str = attrs.field(validator=attrs.validators.instance_of(str))
    full_name: str = attrs.field(default=None)
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    email: str = attrs.field(validator=attrs.validators.instance_of(str))

    @classmethod
    def from_object(cls, user_model) -> 'UserV1':
        return cls(
            public_id=user_model.public_id,
            username=user_model.username,
            full_name=user_model.full_name,
            role=user_model.role,
            email=user_model.email,
        )


@attrs.define(kw_only=True)
class UserSignUpV1(UserV1):
    password: str = attrs.field(converter=str, validator=attrs.validators.min_len(6))


class SerializerNames(TextChoices):
    USER = 'User'
    USER_SIGNUP = 'UserSignUp'


SERIALIZERS = {
    EventVersions.v1: {
        SerializerNames.USER: UserV1,
        SerializerNames.USER_SIGNUP: UserSignUpV1,
    }
}
