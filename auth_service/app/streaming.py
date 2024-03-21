import json
import typing
from enum import Enum
from uuid import uuid4

import attrs
from django.conf import settings
from django.utils.timezone import now


class EventVersions(Enum):
    v1 = '1'


class EventNames(Enum):
    USER_CREATED = 'UserCreated'


class Topics(Enum):
    USER_STREAMING = 'user-streaming'


@attrs.define(kw_only=True)
class Event:
    event_version: str = attrs.field()
    event_name: str = attrs.field()
    data: typing.Union[typing.List, typing.Dict] = attrs.field()
    event_id: str = attrs.field(default=uuid4(), converter=str)
    event_time: str = attrs.field(default=now(), converter=str)
    producer: str = attrs.field(default='accounting-service')


class EventStreaming:

    def __init__(self, version: str = EventVersions.v1):
        self.version = version

    def user_created(self, user):
        event = self.get_event(EventNames.USER_CREATED, attrs.asdict(user))
        settings.PRODUCER.produce(
            topic=Topics.USER_STREAMING,
            key='created',
            value=json.dumps(event).encode('utf-8'),
        )

    def get_event(self, name: str, data: dict):
        return Event(event_name=name, event_version=self.version, data=data)


EVENT_STREAMING_VERSIONS = {
    'v1': EventStreaming(version='v1')
}


def get_event_streaming(event_version: str):
    return EVENT_STREAMING_VERSIONS[event_version]
