import json

from accounting.models import Transaction
from accounting.producer import producer


class EventStreaming:

    @classmethod
    def new_account_transaction(cls, transaction: Transaction):
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
        producer.produce(
            topic='account-streaming',
            key=transaction.type,
            value=json.dumps(data).encode('utf-8'),
        )
