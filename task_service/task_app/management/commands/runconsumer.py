from django.core.management import BaseCommand

from task_app.consuming import KafkaConsumer


class Command(BaseCommand):

    def handle(self, *args, **options):
        KafkaConsumer().consume()
