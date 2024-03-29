import json
import typing
from uuid import uuid4

import attrs
from confluent_kafka import Producer
from django.conf import settings
from django.db.models import TextChoices
from django.utils.timezone import now


class EventVersions(TextChoices):
    v1 = 'v1'


class EventNames(TextChoices):
    USER_CREATED = 'UserCreated'


class Topics(TextChoices):
    USER_STREAM = 'user-stream'


@attrs.define(kw_only=True)
class Event:
    event_version: str = attrs.field()
    event_name: str = attrs.field()
    data: typing.Union[typing.List, typing.Dict] = attrs.field()
    event_id: str = attrs.field(converter=str, default=attrs.Factory(uuid4))
    event_time: str = attrs.field(default=attrs.Factory(lambda: now().isoformat(timespec='seconds')))
    producer: str = attrs.field(default='auth-service')


class EventStreaming:

    def __init__(self, version: str = EventVersions.v1):
        self.version = version
        self.producer = Producer({'bootstrap.servers': settings.KAFKA_SERVERS})

    def user_created(self, user):
        event = Event(
            event_name=EventNames.USER_CREATED,
            event_version=self.version,
            data=attrs.asdict(user, filter=attrs.filters.exclude('password'))
        )
        self.producer.produce(
            topic=Topics.USER_STREAM,
            key='created',
            value=json.dumps(attrs.asdict(event)).encode('utf-8'),
        )
        self.producer.poll()
