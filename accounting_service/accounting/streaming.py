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
    TRANSACTION_CREATED = 'TransactionCreated'
    ACCOUNT_CREATED = 'AccountCreated'
    ACCOUNT_UPDATED = 'AccountUpdated'


class Topics(TextChoices):
    TRANSACTION_STREAM = 'transaction-stream'
    ACCOUNT_STREAM = 'account-stream'


@attrs.define(kw_only=True)
class Event:
    event_version: str = attrs.field()
    event_name: str = attrs.field()
    data: typing.Union[typing.List, typing.Dict] = attrs.field()
    event_id: str = attrs.field(converter=str, default=attrs.Factory(uuid4))
    event_time: str = attrs.field(default=attrs.Factory(lambda: now().isoformat()))
    producer: str = attrs.field(default='accounting-service')


class EventStreaming:

    def __init__(self, version: str = EventVersions.v1.value):
        self.version = version

    def transaction_created(self, transaction):
        event = Event(
            event_name=EventNames.TRANSACTION_CREATED.value,
            event_version=self.version,
            data=attrs.asdict(transaction, filter=attrs.filters.exclude('display_amount'))
        )
        settings.PRODUCER.produce(
            topic=Topics.TRANSACTION_STREAM.value,
            key=transaction.type,
            value=json.dumps(event).encode('utf-8'),
        )
        settings.PRODUCER.flush()

    def account_created(self, account):
        event = Event(
            event_name=EventNames.ACCOUNT_CREATED.value,
            event_version=self.version,
            data=attrs.asdict(account),
        )
        settings.PRODUCER.produce(
            topic=Topics.ACCOUNT_STREAM.value,
            key='created',
            value=json.dumps(event).encode('utf-8'),
        )
        settings.PRODUCER.flush()

    def account_updated(self, account):
        event = Event(
            event_name=EventNames.ACCOUNT_UPDATED.value,
            event_version=self.version,
            data=attrs.asdict(account),
        )
        settings.PRODUCER.produce(
            topic=Topics.ACCOUNT_STREAM.value,
            key='updated',
            value=json.dumps(event).encode('utf-8'),
        )
        settings.PRODUCER.flush()

    def get_event(self, name: str, data: dict):
        return Event(event_name=name, event_version=self.version, data=data)


EVENT_STREAMING_VERSIONS = {
    EventVersions.v1: EventStreaming(version=EventVersions.v1.value)
}


def get_event_streaming(event_version: str):
    return EVENT_STREAMING_VERSIONS[event_version]
