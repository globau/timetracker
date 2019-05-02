import datetime


def pretty_timedelta(timedelta, *, strip_seconds=False):
    # timedelta --> 0h0m0s || 0m0s || 0s
    if isinstance(timedelta, datetime.timedelta):
        seconds = timedelta.total_seconds()
    else:
        seconds = timedelta
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if hours > 0:
        if strip_seconds:
            return "%dh%dm" % (hours, minutes)
        else:
            return "%dh%dm%ds" % (hours, minutes, seconds)
    if minutes > 0:
        if strip_seconds:
            return "%dm" % minutes
        else:
            return "%dm%ds" % (minutes, seconds)
    return "%ds" % seconds


def hms(s):
    # seconds -> hh:mm:ss
    import math

    h = math.floor(s / (60 * 60))
    s -= h * 60 * 60
    m = math.floor(s / 60)
    s -= m * 60
    return "%02d:%02d:%02d" % (h, m, round(s))


def mmss(s):
    # seconds -> mm:ss
    import math

    m = math.floor(s / 60)
    s -= m * 60
    return "%02d:%02d" % (m, round(s))
