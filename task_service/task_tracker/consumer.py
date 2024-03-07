import json
import logging

from confluent_kafka import Consumer

from task_tracker.tasks import create_user


MAP_EVENT_HANDLERS = {
    'Users': {
        'Created': create_user,
    }
}


class KafkaConsumer:
    def __init__(self):
        self.consumer = Consumer({'bootstrap.servers': 'broker:29092', 'group.id': 'popug'})
        self.consumer.subscribe(['Users'])

    def consume(self):
        try:
            while True:
                msg = self.consumer.poll(1)
                if msg is None or msg.error():
                    continue
                topic, key, data = msg.topic(), msg.key().decode('utf-8'), json.loads(msg.value())
                handler = MAP_EVENT_HANDLERS[topic][key]
                print(data)
                handler.delay(**data)
        except Exception as e:
            print(str(e))
        finally:
            self.consumer.close()
