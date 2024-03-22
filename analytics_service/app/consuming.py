import json

from confluent_kafka import Consumer, Message
from django.db.models import TextChoices

from app import tasks


class Topics(TextChoices):
    USER_STREAM = 'user-stream'
    TASK_LIFECYCLE = 'task-lifecycle'
    TRANSACTION_STREAM = 'transaction-stream'
    ACCOUNT_STREAM = 'account-stream'


class KafkaConsumer:
    EVENT_HANDLERS = {
        Topics.USER_STREAM: {
            'created': tasks.create_user,
        },
        Topics.TASK_LIFECYCLE: {
            'created': tasks.create_task,
            'assigned': tasks.update_task,
            'completed': tasks.update_task,
        },
        Topics.ACCOUNT_STREAM: {
            'created': tasks.create_account,
            'updated': tasks.update_account,
        },
        Topics.TRANSACTION_STREAM: {
            'created': tasks.create_transaction,
        }
    }

    def __init__(self):
        self.consumer = Consumer({'bootstrap.servers': 'kafka:29092', 'group.id': 'analytics'})
        self.consumer.subscribe([Topics.values])

    def consume(self):
        try:
            while True:
                try:
                    msg: Message = self.consumer.poll(1)
                    if msg is None:
                        continue
                    if msg.error():
                        # TODO requeue msg back to topic?
                        continue
                    topic, key, event = msg.topic(), msg.key().decode('utf-8'), json.loads(msg.value())
                    print(topic, key, event)
                    # TODO SchemaRegistry
                    # try:
                    #     SchemaRegistry.validate_event(event=data, version='v1')
                    # except SchemaValidationError as e:
                    #     logger.exception(e)
                    handler = self.EVENT_HANDLERS[topic][key]
                    handler.delay(event)
                except Exception as e:
                    print(str(e))
        finally:
            self.consumer.close()
