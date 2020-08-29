"""
The timeutils module is supposed to be where ALL time related logic goes.
This is meant to ease handling timezones and custom day-start-hours later.
"""

from datetime import datetime, timedelta

# TODO: make it all custom-day-start-hour aware


def from_str(string):
    return datetime.strptime(string, "%Y-%m-%d")


def as_str(day_):
    if day_ is None:
        return None
    return day(day_).strftime("%Y-%m-%d")


def _suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def as_fancy_str(day_):
    if day_ is None:
        return None
    return day_.strftime("%B {S}, %Y").replace('{S}', str(day_.day) + _suffix(day_.day))


def day(timestamp):
    return datetime(timestamp.year, timestamp.month, timestamp.day)


def today():
    return day(datetime.now())


def day_after(day_):
    return day(day_) + timedelta(days=1)


def day_before(day_):
    return day(day_) - timedelta(days=1)


def is_future(day_):
    return day(day_) > today()


def is_today(day_):
    return day(day_) == today()
