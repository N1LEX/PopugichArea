import json

from confluent_kafka import Producer
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import User
from app.serializers import CustomUserSerializer

producer = Producer({'bootstrap.servers': 'broker:29092'})


@receiver(post_save, sender=User)
def user_created(instance, created, **kwargs):
    if created:
        popug_data = CustomUserSerializer(instance).data
        producer.produce('Users', json.dumps(popug_data).encode('utf-8'), key='Created')
