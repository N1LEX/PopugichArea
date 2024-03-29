from datetime import datetime
from uuid import UUID


def uuid_validator(instance, attribute, value):
    """
    Raises:
        ValueError: string is not uuid
    """
    UUID(value)


def datetime_validator(instance, attribute, value):
    """
    Raises:
        ValueError: Invalid isoformat string
    """
    datetime.fromisoformat(value)
