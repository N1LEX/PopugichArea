import json

from confluent_kafka import Consumer

from task_tracker.tasks import create_user


class KafkaConsumer:
    def __init__(self):
        self.consumer = Consumer({'bootstrap.servers': 'broker:29092', 'group.id': 'popug'})
        self.consumer.subscribe(['users'])

    def consume(self):
        try:
            while True:
                msg = self.consumer.poll(1)
                if msg is None or msg.error():
                    continue
                user_data = json.loads(msg.value())
                create_user(**user_data)
        except Exception as e:
            print(str(e))
        finally:
            self.consumer.close()
