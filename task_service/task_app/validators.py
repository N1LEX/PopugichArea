from datetime import datetime
from uuid import UUID


def uuid_validator(value: str):
    """
    Raises:
        ValueError: string is not uuid
    """
    UUID(value)


def datetime_validator(value: str):
    """
    Raises:
        ValueError: Invalid isoformat string
    """
    datetime.fromisoformat(value)
