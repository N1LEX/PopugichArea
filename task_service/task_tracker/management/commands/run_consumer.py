import logging

from django.core.management import BaseCommand

from task_tracker.consumer import KafkaConsumer


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Running consumer...')
        KafkaConsumer().consume()
        print('Consumer disconnected')
