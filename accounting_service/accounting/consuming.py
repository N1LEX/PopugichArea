import json
import logging

from accounting import tasks
from confluent_kafka import Consumer, Message
from django.db.models import TextChoices


class Topics(TextChoices):
    USER_STREAM = 'user-stream'
    TASK_LIFECYCLE = 'task-lifecycle'


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

logger = logging.getLogger(__name__)


class KafkaConsumer:

    def __init__(self):
        self.consumer = Consumer({'bootstrap.servers': 'kafka:29092', 'group.id': 'accounting'})
        self.consumer.subscribe(Topics.values)

    def consume(self):
        try:
            while True:
                try:
                    msg: Message = self.consumer.poll(1)
                    if msg is None:
                        continue
                    if msg.error():
                        # TODO requeue msg back to topic?
                        print(msg.error().code())
                        continue
                    topic, key, event = msg.topic(), msg.key().decode('utf-8'), json.loads(msg.value())
                    print(topic, key, event)
                    handler = EVENT_HANDLERS[topic][key]
                    handler.delay(event)
                except Exception as e:
                    print(str(e))
        finally:
            self.consumer.close()
