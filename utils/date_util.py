from datetime import datetime
from typing import Union

import pytz


class DateUtil:
    @staticmethod
    def get_current_time(timezone: Union[pytz.timezone, str] = None, date_only=False) -> datetime:
        """
        Retrieves the current time in the specified timezone, defaults to UTC if no timezone is provided.
        Can return just the date portion if date_only is set to True.

        Args:
            timezone: The timezone as a timezone object or a string that pytz can interpret.
            date_only: If True, returns just the date portion.

        Returns:
            datetime: Current time in the given timezone, with microseconds set to 0. If date_only is True, returns just
             the date.
        """
        if not timezone:
            timezone = pytz.timezone("UTC")
        elif isinstance(timezone, str):
            timezone = pytz.timezone(timezone)
        current_time = datetime.now(timezone).replace(microsecond=0)
        return current_time.date() if date_only else current_time