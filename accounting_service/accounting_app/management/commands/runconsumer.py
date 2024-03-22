from accounting_app.consuming import KafkaConsumer
from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Running accounting consumer...')
        KafkaConsumer().consume()
        print('Consumer disconnected')
