from datetime import datetime, timedelta, timezone
import pytz


def _suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


class Day:
    def __init__(self, year, month, day, user):
        self.user = user
        self._timestamp = datetime(year, month, day, tzinfo=timezone.utc)

    @staticmethod
    def from_str(string, user):
        return Day.from_timestamp(datetime.strptime(string, "%Y-%m-%d"), user)

    @staticmethod
    def from_timestamp(timestamp, user):
        """
        This function is NOT meant to be aware of timezones etc, you should
        only use it to handle data stored in the database, in the format of the
        output of the ".timestamp" property.
        """
        return Day(timestamp.year, timestamp.month, timestamp.day, user)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.year == other.year \
            and self.month == other.month \
            and self.day == other.day

    def __add__(self, other, oper="+"):
        if not isinstance(other, int):
            raise TypeError(
                'Unsupported operands for "+". The right hand side needs to be a number.')
        else:
            return Day.from_timestamp(self.timestamp + timedelta(days=other), self.user)

    def __sub__(self, other):
        if not isinstance(other, int):
            raise TypeError(
                'Unsupported operands for "-". The right hand side needs to be a number.')
        else:
            return Day.from_timestamp(self.timestamp + timedelta(days=-other), self.user)

    def __lt__(self, other): return self.timestamp < other.timestamp
    def __gt__(self, other): return self.timestamp > other.timestamp
    def __le__(self, other): return self < other or self == other
    def __ge__(self, other): return self > other or self == other

    def __repr__(self): return "<Day[%s,user=%s]>" % (self.url, self.user)

    @property
    def year(self): return self._timestamp.year

    @property
    def month(self): return self._timestamp.month

    @property
    def day(self): return self._timestamp.day

    @property
    def timestamp(self): return self._timestamp

    @property
    def is_today(self):
        return self == Day.today(self.user)

    @property
    def is_future(self):
        return self > Day.today(self.user)

    @property
    def pretty(self):
        if self.is_today:
            return "Today"
        return self._timestamp.strftime("%B {S}, %Y").replace('{S}', str(self.day) + _suffix(self.day))

    @property
    def url(self):
        return self._timestamp.strftime("%Y-%m-%d")

    @staticmethod
    def today(user):
        tz = pytz.timezone(user.timezone)

        now = datetime.now(tz)
        day = Day(now.year, now.month, now.day, user)

        if now.hour < user.start_of_day:
            day -= 1

        return day
