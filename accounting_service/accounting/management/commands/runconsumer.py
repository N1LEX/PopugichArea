from django.core.management import BaseCommand

from accounting.consumer import KafkaConsumer


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Running consumer...')
        KafkaConsumer().consume()
        print('Consumer disconnected')
