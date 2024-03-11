import json

from confluent_kafka import Consumer

from task_tracker.tasks import create_user

MAP_EVENT_HANDLERS = {
    'user-stream': {
        'Created': create_user,
    }
}


class KafkaConsumer:
    def __init__(self):
        self._consumer = Consumer({'bootstrap.servers': 'broker:29092', 'group.id': 'popug'})
        self._consumer.subscribe(['user-stream'])

    def consume(self):
        try:
            while True:
                msg = self._consumer.poll(1)
                if msg is None or msg.error():
                    continue
                topic, key, data = msg.topic(), msg.key().decode('utf-8'), json.loads(msg.value())
                handler = MAP_EVENT_HANDLERS[topic][key]
                handler.delay(**data)
        finally:
            self._consumer.close()
