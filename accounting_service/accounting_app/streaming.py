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
    TRANSACTION_CREATED = 'TransactionCreated'
    ACCOUNT_CREATED = 'AccountCreated'
    ACCOUNT_UPDATED = 'AccountUpdated'
    TASK_UPDATED = 'TaskUpdated'


class Topics(TextChoices):
    TRANSACTION_STREAM = 'transaction-stream'
    ACCOUNT_STREAM = 'account-stream'
    TASK_STREAM = 'task-stream'


@attrs.define(kw_only=True)
class Event:
    event_version: str = attrs.field()
    event_name: str = attrs.field()
    data: typing.Union[typing.List, typing.Dict] = attrs.field()
    event_id: str = attrs.field(converter=str, default=attrs.Factory(uuid4))
    event_time: str = attrs.field(default=attrs.Factory(lambda: now().isoformat(timespec='seconds')))
    producer: str = attrs.field(default='accounting-service')


class EventStreaming:

    def __init__(self, version: str = EventVersions.v1):
        self.version = version
        self.producer = Producer({'bootstrap.servers': settings.KAFKA_SERVERS})

    def transaction_created(self, transaction):
        event = Event(
            event_name=EventNames.TRANSACTION_CREATED,
            event_version=self.version,
            data=attrs.asdict(transaction, filter=attrs.filters.exclude('display_amount')),
        )
        self.producer.produce(
            topic=Topics.TRANSACTION_STREAM,
            key=transaction.type,
            value=json.dumps(attrs.asdict(event)).encode('utf-8'),
        )
        self.producer.poll()

    def account_created(self, account):
        event = Event(
            event_name=EventNames.ACCOUNT_CREATED,
            event_version=self.version,
            data=attrs.asdict(account),
        )
        self.producer.produce(
            topic=Topics.ACCOUNT_STREAM,
            key='created',
            value=json.dumps(attrs.asdict(event)).encode('utf-8'),
        )
        self.producer.poll()

    def account_updated(self, account):
        event = Event(
            event_name=EventNames.ACCOUNT_UPDATED,
            event_version=self.version,
            data=attrs.asdict(account),
        )
        self.producer.produce(
            topic=Topics.ACCOUNT_STREAM,
            key='updated',
            value=json.dumps(attrs.asdict(event)).encode('utf-8'),
        )
        self.producer.poll()

    def task_updated(self, task):
        event = Event(
            event_name=EventNames.TASK_UPDATED,
            event_version=self.version,
            data=attrs.asdict(task),
        )
        self.producer.produce(
            topic=Topics.TASK_STREAM,
            key='updated',
            value=json.dumps(attrs.asdict(event)).encode('utf-8'),
        )
        self.producer.poll()
