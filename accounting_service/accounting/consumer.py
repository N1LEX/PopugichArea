import json
import logging

from confluent_kafka import Consumer

from accounting.tasks import create_user, handle_assigned_task, handle_completed_task

MAP_EVENT_HANDLERS = {
    'user-stream': {
        'created': create_user,
    },
    'tasks': {
        'assigned': handle_assigned_task,
        'completed': handle_completed_task,
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
                msg = self._consumer.poll(1)
                if msg is None or msg.error():
                    continue
                topic, key, data = msg.topic(), msg.key().decode('utf-8'), json.loads(msg.value())
                print(topic, key, data)
                # TODO SchemaRegistry
                # try:
                #     SchemaRegistry.validate_event(event=data, version='v1')
                # except SchemaValidationError as e:
                #     logger.exception(e)
                handler = MAP_EVENT_HANDLERS[topic][key]
                handler.delay(**data)
        finally:
            self._consumer.close()
