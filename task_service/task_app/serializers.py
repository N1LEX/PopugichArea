import random
from datetime import date
from uuid import uuid4

import attrs
from django.db.models import TextChoices
from task_app import validators
from task_app.models import Task, User
from task_app.streaming import EventVersions


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


@attrs.define(kw_only=True)
class TaskDashboardViewV1(TaskV1):
    username: str = attrs.field()
    link: str = attrs.field()

    @classmethod
    def from_object(cls, task: Task):
        return cls(
            public_id=task.public_id,
            user_id=task.user.public_id,
            description=task.description,
            status=task.status,
            date=task.date,
            username=task.user.username,
            link=task.link,
        )


class SerializerNames(TextChoices):
    USER = 'User'
    TASK = 'Task'
    TASK_DASHBOARD = 'TaskDashboard'


SERIALIZERS = {
    EventVersions.v1: {
        SerializerNames.USER: UserV1,
        SerializerNames.TASK: TaskV1,
        SerializerNames.TASK_DASHBOARD: TaskDashboardViewV1,
    }
}
