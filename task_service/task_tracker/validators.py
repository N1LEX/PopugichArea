from datetime import datetime
from uuid import UUID


class UUIDValidator:

    def __call__(self, obj, attribute, value):
        """
        Raises:
            ValueError: string is not uuid
        """
        UUID(value)


class DatetimeValidator:

    def __call__(self, obj, attribute, value):
        """
        Raises:
            ValueError: Invalid isoformat string
        """
        datetime.fromisoformat(value)
