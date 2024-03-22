from django.core.management import BaseCommand

from app.consuming import KafkaConsumer


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Running analytics consumer...')
        KafkaConsumer().consume()
        print('Consumer disconnected')
