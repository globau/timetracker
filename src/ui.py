import re
import sys
from datetime import datetime

import arrow

import cfg
from harness import logger
from process import call
from terminal import coloured

CHAR_EDITED = "Δ"
CHAR_CURRENT = "←"


def parse_date(date_str, *, context):
    date_str = date_str.lower()

    if context == "day":
        # today, yesterday, tomorrow
        if date_str in ("today", "now"):
            return arrow.now(tz=cfg.time_zone).floor("day")
        if date_str in ("yesterday", "yes", "prev"):
            return arrow.now(tz=cfg.time_zone).shift(days=-1).floor("day")
        if date_str in ("tomorrow", "tom", "next"):
            return arrow.now(tz=cfg.time_zone).shift(days=1).floor("day")

    elif context == "week":
        # today
        if date_str in ("today", "now"):
            return arrow.now(tz=cfg.time_zone).floor("day")
        # last week
        if date_str in ("last",):
            return arrow.now(tz=cfg.time_zone).floor("day").shift(days=-7)

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
    try:
        m = re.search(
            r"^([+-]\d*(?:\.\d+)?)(m|minutes?|h|hours?|d|days?)$",
            adjustment_str,
            re.IGNORECASE,
        )
        if not m:
            raise ValueError()

        adjust_amount = float(m.group(1))
        adjust_unit = m.group(2)
    except ValueError:
        raise ValueError("invalid adjustment: %s" % adjustment_str)

    if adjust_unit == "d":
        return 60 * (cfg.work_week / 5) * adjust_amount

    if adjust_unit == "h":
        return 60 * adjust_amount

    return adjust_amount


def format_minutes(minutes):
    # hh:mm
    hours, minutes = divmod(abs(minutes), 60)
    return "%02d:%02d" % (hours, minutes)


def format_minutes_relative(target, minutes):
    if minutes == target:
        return coloured("green", "⦗ %s⦘" % format_minutes(0))
    if minutes < target:
        return coloured("red", "⦗-%s⦘" % format_minutes(target - minutes))
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


def input_ex(prompt, *, required=False, default=None, validator=None, options=None):
    if validator:
        assert callable(validator)

    if options:
        assert not validator

        def _check_options(value):
            value = value.lower()
            if value not in options:
                raise ValueError("")
            return value

        validator = _check_options

    if default:
        prompt = "%s (%s)" % (prompt, default)
    prompt = "%s: " % prompt

    try:
        while True:
            res = input(coloured("green", prompt)).strip()

            if res == "":
                if required:
                    continue
                if default:
                    res = default

            if validator:
                try:
                    res = validator(res)
                except ValueError as e:
                    if str(e):
                        logger.error(e)
                    continue

            return res
    except KeyboardInterrupt:
        print("")
        sys.exit(1)


def plural(count, item, *, suffix="s"):
    return "{:,d} {}{}".format(count, item, "" if count == 1 else suffix)
