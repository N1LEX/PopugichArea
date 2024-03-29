import json
import typing
from uuid import uuid4

import attrs
from confluent_kafka.cimpl import Producer
from django.conf import settings
from django.db.models import TextChoices
from django.utils.timezone import now


class EventVersions(TextChoices):
    v1 = 'v1'


class EventNames(TextChoices):
    TASK_CREATED = 'TaskCreated'
    TASK_ASSIGNED = 'TaskAssigned'
    TASK_COMPLETED = 'TaskCompleted'


class Topics(TextChoices):
    TASK_LIFECYCLE = 'task-lifecycle'


@attrs.define(kw_only=True)
class Event:
    event_version: str = attrs.field()
    event_name: str = attrs.field()
    data: typing.Union[typing.List, typing.Dict] = attrs.field()
    event_id: str = attrs.field(converter=str, default=attrs.Factory(uuid4))
    event_time: str = attrs.field(default=attrs.Factory(lambda: now().isoformat(timespec='seconds')))
    producer: str = attrs.field(default='task-tracker')


class EventStreaming:

    def __init__(self, version: str = EventVersions.v1):
        self.version = version
        self.producer = Producer({'bootstrap.servers': settings.KAFKA_SERVERS})

    def task_created(self, task):
        event = Event(
            event_name=EventNames.TASK_CREATED,
            event_version=self.version,
            data=attrs.asdict(task),
        )
        self.producer.produce(
            topic=Topics.TASK_LIFECYCLE,
            key=task.status,
            value=json.dumps(attrs.asdict(event)).encode('utf-8'),
        )
        self.producer.poll()

    def task_assigned(self, task):
        event = Event(
            event_name=EventNames.TASK_ASSIGNED,
            event_version=self.version,
            data=attrs.asdict(task),
        )
        self.producer.produce(
            topic=Topics.TASK_LIFECYCLE,
            key=task.status,
            value=json.dumps(event).encode('utf-8'),
        )
        self.producer.poll()

    def task_completed(self, task):
        event = Event(
            event_name=EventNames.TASK_COMPLETED,
            event_version=self.version,
            data=attrs.asdict(task),
        )
        self.producer.produce(
            topic=Topics.TASK_LIFECYCLE,
            key=task.status,
            value=json.dumps(event).encode('utf-8'),
        )
        self.producer.poll()
