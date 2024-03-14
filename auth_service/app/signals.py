import json

from confluent_kafka import Producer
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import User
from app.serializers import UserSerializer

producer = Producer({'bootstrap.servers': 'broker:29092'})


@receiver(post_save, sender=User)
def user_created(instance, created, **kwargs):
    popug_data = UserSerializer(instance).data
    producer.produce(topic='user-stream', key='created', value=json.dumps(popug_data).encode('utf-8'))
    producer.flush()
