import random
from datetime import date
from uuid import uuid4

import attrs
from django.db.models import TextChoices
from task_app import validators
from task_app.models import Task, User


@attrs.define(kw_only=True)
class UserV1:
    public_id: str = attrs.field(validator=validators.uuid_validator, converter=str)
    username: str = attrs.field(validator=attrs.validators.instance_of(str))
    full_name: str = attrs.field()
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    email: str = attrs.field(validator=attrs.validators.instance_of(str))


@attrs.define(kw_only=True)
class TaskV1:
    public_id: str = attrs.field(converter=str, default=attrs.Factory(uuid4))
    user_id: str = attrs.field(converter=str, default=attrs.Factory(lambda: random.choice(User.workers())))
    description: str = attrs.field(validator=attrs.validators.instance_of(str))
    status: str = attrs.field(default=Task.StatusChoices.ASSIGNED, converter=str)
    date: str = attrs.field(converter=str, default=attrs.Factory(date.today))

    @classmethod
    def from_object(cls, task: Task):
        return cls(
            public_id=task.public_id,
            user_id=task.user.public_id,
            description=task.description,
            status=task.status,
            date=task.date
        )


class SerializerNames(TextChoices):
    USER = 'User'
    TASK = 'Task'


SERIALIZERS = {
    'v1': {
        SerializerNames.USER: UserV1,
        SerializerNames.TASK: TaskV1,
    }
}


def get_serializer(model_name: str, event_version: str):
    return SERIALIZERS[event_version][model_name]
