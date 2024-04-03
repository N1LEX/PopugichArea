import json
import logging

from confluent_kafka import Consumer, Message
from django.db.models import TextChoices

from analytics_app import tasks
from analytics_service import settings

logger = logging.getLogger(__name__)


class Topics(TextChoices):
    USER_STREAM = 'user-stream'
    TASK_LIFECYCLE = 'task-lifecycle'
    TASK_STREAM = 'task-stream'
    TRANSACTION_STREAM = 'transaction-stream'
    ACCOUNT_STREAM = 'account-stream'


class KafkaConsumer:

    EVENT_HANDLERS = {
        Topics.USER_STREAM: {
            'created': tasks.create_user,
        },
        Topics.TASK_LIFECYCLE: {
            'created': tasks.create_task,
            'assigned': tasks.update_task_lifecycle,
            'completed': tasks.update_task_lifecycle,
        },
        Topics.TASK_STREAM: {
            'updated': tasks.add_task_price,
        },
        Topics.ACCOUNT_STREAM: {
            'created': tasks.create_account,
            'updated': tasks.update_account,
        },
        Topics.TRANSACTION_STREAM: {
            'deposit': tasks.create_transaction,
            'withdraw': tasks.create_transaction,
            'payment': tasks.create_transaction,
        }
    }

    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': settings.KAFKA_SERVERS,
            'group.id': settings.KAFKA_GROUP,
            'auto.offset.reset': 'earliest',
        })
        self.consumer.subscribe(Topics.values)

    def consume(self):
        try:
            while True:
                try:
                    msg: Message = self.consumer.poll(1)
                    if msg is None:
                        continue
                    if msg.error():
                        logger.error(msg.error().str())
                    topic, key, event = msg.topic(), msg.key().decode('utf-8'), json.loads(msg.value())
                    logger.info(topic, key, event)
                    handler = self.EVENT_HANDLERS[topic][key]
                    handler.delay(event)
                except Exception as e:
                    logger.exception(e)
        finally:
            self.consumer.close()
