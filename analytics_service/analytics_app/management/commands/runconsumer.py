from django.core.management import BaseCommand

from analytics_app.consuming import KafkaConsumer


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Running analytics consumer...')
        KafkaConsumer().consume()
        print('Consumer disconnected')
