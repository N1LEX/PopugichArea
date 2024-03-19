from uuid import uuid4

from attrs import define
from django.utils.timezone import now


@define
class Event:
    data: dict

    event_version: str
    event_name: str
    producer: str
    event_time: str = str(now())
    event_id: str = str(uuid4())
