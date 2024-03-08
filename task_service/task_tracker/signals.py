import json

from confluent_kafka import Producer
from django.db.models.signals import post_save
from django.dispatch import receiver

from task_tracker.models import Task
from task_tracker.serializers import TaskSerializer

producer = Producer({'bootstrap.servers': 'broker:29092'})


@receiver(post_save, sender=Task)
def task_save(instance, created, **kwargs):
    task_data = TaskSerializer(instance).data
    producer.produce('TaskWorkFlow', json.dumps(task_data).encode('utf-8'))
