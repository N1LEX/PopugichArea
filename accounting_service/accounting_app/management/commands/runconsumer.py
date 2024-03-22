from django.core.management import BaseCommand

from accounting.consuming import KafkaConsumer


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Running accounting consumer...')
        KafkaConsumer().consume()
        print('Consumer disconnected')
