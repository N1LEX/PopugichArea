import json
import typing
from uuid import uuid4

import attrs
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
    event_time: str = attrs.field(default=attrs.Factory(lambda: now().isoformat()))
    producer: str = attrs.field(default='auth-service')


class EventStreaming:

    def __init__(self, version: str = EventVersions.v1.value):
        self.version = version

    def user_created(self, user):
        event = self.get_event(
            EventNames.USER_CREATED.value,
            attrs.asdict(user, filter=attrs.filters.exclude('password'))
        )
        settings.PRODUCER.produce(
            topic=Topics.USER_STREAM.value,
            key='created',
            value=json.dumps(attrs.asdict(event)).encode('utf-8'),
        )
        settings.PRODUCER.flush()

    def get_event(self, name: str, data: dict):
        return Event(event_name=name, event_version=self.version, data=data)


EVENT_STREAMING_VERSIONS = {
    EventVersions.v1: EventStreaming(version=EventVersions.v1.value)
}


def get_event_streaming(event_version: str):
    return EVENT_STREAMING_VERSIONS[event_version]
