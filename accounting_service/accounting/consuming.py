import json
import logging

from confluent_kafka import Consumer, Message

from accounting import tasks

EVENT_HANDLERS = {
    'user-stream': {
        'created': tasks.create_user,
    },
    'task-lifecycle': {
        'created': tasks.handle_created_task,
        'assigned': tasks.handle_assigned_task,
        'completed': tasks.handle_completed_task,
    }
}

logger = logging.getLogger(__name__)


class KafkaConsumer:

    def __init__(self):
        self._consumer = Consumer({'bootstrap.servers': 'broker:29092', 'group.id': 'accounting'})
        self._consumer.subscribe(['user-stream', 'tasks'])

    def consume(self):
        try:
            while True:
                msg: Message = self._consumer.poll(1)
                if msg is None:
                    continue
                if msg.error():
                    # TODO requeue msg back to topic?
                    continue
                topic, key, event = msg.topic(), msg.key().decode('utf-8'), json.loads(msg.value())
                print(topic, key, event)
                handler = EVENT_HANDLERS[topic][key]
                handler.delay(event)
        finally:
            self._consumer.close()
