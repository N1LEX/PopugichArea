import json

from confluent_kafka import Consumer, Message

from task_tracker.tasks import create_user

EVENT_HANDLERS = {
    'user-stream': {
        'created': create_user,
    }
}


class KafkaConsumer:

    def __init__(self):
        self._consumer = Consumer({'bootstrap.servers': 'broker:29092', 'group.id': 'task-tracker'})
        self._consumer.subscribe(['user-stream'])

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
