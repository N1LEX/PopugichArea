import json

from confluent_kafka import Consumer, Message

from analytics_service.app import tasks


class KafkaConsumer:
    EVENT_HANDLERS = {
        'user-stream': {
            'created': tasks.create_user,
        },
        'task-lifecycle': {
            'created': tasks.create_task,
            'assigned': tasks.update_task,
            'completed': tasks.update_task,
        },
        'account-streaming': {
            'created': tasks.create_account,
            'updated': tasks.update_account,
        },
        'transaction-streaming': {
            'created': tasks.create_transaction,
        }
    }

    def __init__(self):
        self._consumer = Consumer({'bootstrap.servers': 'broker:29092', 'group.id': 'analytics'})
        self._consumer.subscribe(['user-stream', 'task-lifecycle', 'account-streaming'])

    def consume(self):
        try:
            while True:
                msg: Message = self._consumer.poll(1)
                if msg is None:
                    continue
                if msg.error():
                    # TODO requeue msg back to topic?
                    continue
                topic, key, data = msg.topic(), msg.key().decode('utf-8'), json.loads(msg.value())
                print(topic, key, data)
                # TODO SchemaRegistry
                # try:
                #     SchemaRegistry.validate_event(event=data, version='v1')
                # except SchemaValidationError as e:
                #     logger.exception(e)
                handler = self.EVENT_HANDLERS[topic][key]
                handler.delay(data)
        finally:
            self._consumer.close()
