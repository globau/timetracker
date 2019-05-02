import re

import arrow
import cfg
import database
import ui
from command import Command
from terminal import coloured


def _as_month(date_str):
    if re.search(r"^20\d\d[-/]?(?:0\d|1[012])$", date_str):
        return "%s-01" % date_str

    if re.search(r"^20\d\d$", date_str):
        return "%s-01-01" % date_str

    return date_str


class Monthly(Command):
    @staticmethod
    def add_args(parser):
        command = parser.add_parser("month", help="monthly report")
        command.add_argument("start", nargs="?", help="starting month")
        command.add_argument("end", nargs="?", help="ending month")
        return command

    @staticmethod
    def execute(args):
        args.start = (
            arrow.now(tz=cfg.time_zone).format("YYYY-01-01")
            if args.start is None
            else _as_month(args.start)
        )
        start_dt = ui.parse_date(args.start).floor("month")

        args.end = (
            start_dt.format("YYYY-12-31") if args.end is None else _as_month(args.end)
        )
        end_dt = ui.parse_date(args.end).ceil("month")

        today = arrow.now(tz=cfg.time_zone).ceil("day")
        if end_dt > today:
            end_dt = today

        days = {}
        dt = start_dt
        while dt < end_dt:
            days[dt.format("YYYYMMDD")] = dict(dt=dt.clone(), minutes=0)
            dt = dt.shift(days=1)

        minutes = 0
        for dtr in database.active_ranges(start_dt, end_dt):
            days[dtr.start_dt.format("YYYYMMDD")]["minutes"] += dtr.minutes
            minutes += dtr.minutes

        for ymd in sorted(days.keys()):
            for edit in database.edits(days[ymd]["dt"]):
                days[ymd]["minutes"] += edit.minutes
                minutes += edit.minutes

        # group into months
        months = {}
        total = 0
        for ymd in sorted(days.keys()):
            dt = days[ymd]["dt"]
            ym = dt.format("YYYYMM")
            months.setdefault(ym, dict(name=dt.format("YYYY MMM"), minutes=0))
            months[ym]["minutes"] += days[ymd]["minutes"]
            total += days[ymd]["minutes"]

        hour_width = len(ui.format_minutes(total))

        # header
        print(
            coloured(
                "yellow", "%{}s TOTAL".format(hour_width) % ui.format_minutes(total)
            )
        )

        # report
        for month in sorted(months.keys()):
            print(
                "%{}s %s".format(hour_width)
                % (ui.format_minutes(months[month]["minutes"]), months[month]["name"])
            )
