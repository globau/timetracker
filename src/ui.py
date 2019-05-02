import re
from datetime import datetime

import arrow
import cfg
from process import call
from terminal import coloured

CHAR_EDITED = "Δ"
CHAR_CURRENT = "←"


def parse_date(date_str):
    date_str = date_str.lower()

    # today, yesterday, tomorrow
    if date_str == "today" or date_str == "now":
        return arrow.now(tz=cfg.time_zone).floor("day")
    if date_str == "yesterday" or date_str == "yes" or date_str == "prev":
        return arrow.now(tz=cfg.time_zone).shift(days=-1).floor("day")
    if date_str == "tomorrow" or date_str == "tom" or date_str == "next":
        return arrow.now(tz=cfg.time_zone).shift(days=1).floor("day")

    # yyyy-mm-dd, yyyy/mm/dd, yyyymmdd
    m = re.search(r"^(20\d\d)[-/]?(0\d|1[012])[-/]?([012]\d|3[01])$", date_str)
    if m:
        yyyy = int(m.group(1))
        mm = int(m.group(2))
        dd = int(m.group(3))
        return arrow.get(datetime(yyyy, mm, dd, tzinfo=cfg.time_zone)).floor("day")

    # dd-mm-yyyy, dd/mm/yyyy
    m = re.search(r"^([012]\d|3[01])[-/](0\d|1[012])[-/](20\d\d)$", date_str)
    if m:
        dd = int(m.group(1))
        mm = int(m.group(2))
        yyyy = int(m.group(3))
        return arrow.get(datetime(yyyy, mm, dd, tzinfo=cfg.time_zone)).floor("day")

    # day of week
    weekdays = dict(mon=0, tue=1, wed=2, thu=3, fri=4, sat=5, sun=6)
    if date_str[:3] in weekdays:
        dt = arrow.now(tz=cfg.time_zone).floor("day")
        if dt.weekday() == weekdays[date_str[:3]]:
            return dt
        return dt.shift(days=-7).shift(weekday=weekdays[date_str[:3]])

    raise ValueError("invalid date: %s" % date_str)


def parse_adjustment(adjustment_str):
    # returns minutes
    m = re.search(
        r"^([+-]\d*(?:\.\d+)?)(m|minutes?|h|hours?|d|days?)$",
        adjustment_str,
        re.IGNORECASE,
    )
    try:
        if not m:
            raise ValueError()
        adjust_amount = float(m.group(1))
        adjust_unit = m.group(2)
    except ValueError:
        raise ValueError("invalid adjustment: %s" % adjustment_str)

    if adjust_unit == "d":
        return 60 * (cfg.work_week / 5) * adjust_amount

    elif adjust_unit == "h":
        return 60 * adjust_amount

    else:
        return adjust_amount


def format_minutes(minutes):
    # hh:mm
    hours, minutes = divmod(abs(minutes), 60)
    return "%02d:%02d" % (hours, minutes)


def format_minutes_relative(target, minutes):
    if minutes == target:
        return coloured("green", "⦗ %s⦘" % format_minutes(0))
    elif minutes < target:
        return coloured("red", "⦗-%s⦘" % format_minutes(target - minutes))
    else:
        return coloured("green", "⦗+%s⦘" % format_minutes(minutes - target))


def notify(*, away=False, back=False):
    assert away or back
    if away:
        message = "Marked as Away"
    else:
        message = "Marked as Back"
    call(
        [cfg.terminal_notifier]
        + ["-message", message]
        + ["-title", "Time Tracker"]
        + ["-sender", "uno.glob.timetracker"]
    )
