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
    TRANSACTION_CREATED = 'TransactionCreated'
    ACCOUNT_CREATED = 'AccountCreated'
    ACCOUNT_UPDATED = 'AccountUpdated'


class Topics(Enum):
    TRANSACTION_STREAMING = 'transaction-streaming'
    ACCOUNT_STREAMING = 'account-streaming'


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

    def transaction_created(self, transaction):
        event = Event(
            event_name=EventNames.TRANSACTION_CREATED,
            event_version=self.version,
            data=attrs.asdict(transaction, filter=attrs.filters.exclude('display_amount'))
        )
        settings.PRODUCER.produce(
            topic=Topics.TRANSACTION_STREAMING,
            key=transaction.type,
            value=json.dumps(event).encode('utf-8'),
        )

    def account_created(self, account):
        event = Event(
            event_name=EventNames.ACCOUNT_CREATED,
            event_version=self.version,
            data=attrs.asdict(account),
        )
        settings.PRODUCER.produce(
            topic=Topics.ACCOUNT_STREAMING,
            key='created',
            value=json.dumps(event).encode('utf-8'),
        )

    def account_updated(self, account):
        event = Event(
            event_name=EventNames.ACCOUNT_UPDATED,
            event_version=self.version,
            data=attrs.asdict(account),
        )
        settings.PRODUCER.produce(
            topic=Topics.ACCOUNT_STREAMING,
            key='updated',
            value=json.dumps(event).encode('utf-8'),
        )

    def get_event(self, name: str, data: dict):
        return Event(event_name=name, event_version=self.version, data=data)


EVENT_STREAMING_VERSIONS = {
    '1': EventStreaming(version='1')
}


def get_event_streaming(event_version: str):
    return EVENT_STREAMING_VERSIONS[event_version]
