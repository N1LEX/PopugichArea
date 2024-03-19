import json

from confluent_kafka import Producer

from accounting.models import Transaction


class EventStreaming:
    producer = Producer({'bootstrap.servers': 'broker:29092'})

    @classmethod
    def account_transaction(cls, transaction: Transaction):
        data = {
            'public_id': str(transaction.public_id),
            'account_id': str(transaction.public_id),
            'user_id': str(transaction.account.user_id),
            'type': transaction.type,
            'debit': transaction.debit,
            'credit': transaction.credit,
            'purpose': transaction.purpose,
            'datetime': str(transaction.datetime),
        }
        cls.producer.produce(
            topic='account-streaming',
            key=transaction.type,
            value=json.dumps(data).encode('utf-8'),
        )
