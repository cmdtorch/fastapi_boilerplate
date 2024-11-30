import datetime

import pytz


def is_valid_timezone(timezone: str) -> bool:
    try:
        datetime.datetime.now(pytz.timezone(timezone))
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False
