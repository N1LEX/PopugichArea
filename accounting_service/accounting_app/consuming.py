import json
import logging

from accounting_app import tasks
from confluent_kafka import Consumer, Message
from django.conf import settings
from django.db.models import TextChoices


class Topics(TextChoices):
    USER_STREAM = 'user-stream'
    TASK_LIFECYCLE = 'task-lifecycle'


logger = logging.getLogger(__name__)


class KafkaConsumer:

    EVENT_HANDLERS = {
        Topics.USER_STREAM: {
            'created': tasks.create_user,
        },
        Topics.TASK_LIFECYCLE: {
            'created': tasks.handle_created_task,
            'assigned': tasks.handle_assigned_task,
            'completed': tasks.handle_completed_task,
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
