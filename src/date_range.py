from functools import total_ordering

import cfg


@total_ordering
class DateRange(object):
    def __init__(self, start_dt, end_dt):
        assert start_dt.datetime.tzname() == cfg.time_zone_name
        assert end_dt.datetime.tzname() == cfg.time_zone_name

        self._start_dt = start_dt.floor("minute")
        self._end_dt = end_dt.floor("minute")
        self.minutes = 0
        self._calc_minutes()

    def __str__(self):
        return "%s - %s" % (
            self._start_dt.format("Do MMM"),
            self._end_dt.format("Do MMM"),
        )

    def __eq__(self, other):
        return (
            self._start_dt.timestamp == other.start_dt.timestamp
            and self._end_dt.timestamp == other.end_dt.timestamp
        )

    def __ne__(self, other):
        return (
            self._start_dt.timestamp != other.start_dt.timestamp
            and self._end_dt.timestamp != other.end_dt.timestamp
        )

    def __lt__(self, other):
        return self._start_dt < other.end_dt

    @property
    def start_dt(self):
        return self._start_dt

    @start_dt.setter
    def start_dt(self, dt):
        self._start_dt = dt
        self._calc_minutes()

    @property
    def end_dt(self):
        return self._end_dt

    @end_dt.setter
    def end_dt(self, dt):
        self._end_dt = dt
        self._calc_minutes()

    @property
    def start_ymd(self):
        return self._start_dt.format("YYYYMMDD")

    @property
    def end_ymd(self):
        return self._end_dt.format("YYYYMMDD")

    def _calc_minutes(self):
        self.minutes = round((self._end_dt - self._start_dt).total_seconds() / 60)
