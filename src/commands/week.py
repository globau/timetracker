import arrow

import cfg
import database
import state
import ui
from main import cli, click, invoke
from terminal import coloured


@click.option("--status", "-s", is_flag=True, help="also show curent status")
@click.argument("date", required=False, default="today")
@cli.command(aliases=["w"], help="summary of your week")
def week(date, status):
    start_dt = ui.parse_date(date, context="week")

    # start_dt needs to be a monday
    if start_dt.weekday() != 0:
        start_dt = start_dt.shift(days=-7).shift(weekday=0)

    end_dt = start_dt.shift(days=7).shift(minutes=-1)

    # count days worked
    days = {}
    dt = start_dt.clone()
    while dt < end_dt:
        days[dt.format("YYYYMMDD")] = dict(dt=dt.clone(), minutes=0, edited=False)
        dt = dt.shift(days=1)

    # tally minutes
    total_minutes = 0
    for dtr in database.active_ranges(start_dt, end_dt):
        days[dtr.start_dt.format("YYYYMMDD")]["minutes"] += dtr.minutes
        total_minutes += dtr.minutes

    # process edits
    for ymd in sorted(days.keys()):
        for edit in database.edits(days[ymd]["dt"]):
            days[ymd]["minutes"] += edit.minutes
            days[ymd]["edited"] = True
            total_minutes += edit.minutes

    # header
    print(
        "%s %s %s %s - %s"
        % (
            coloured("yellow", ui.format_minutes(total_minutes)),
            coloured("yellow", "%-9s" % "WEEK"),
            ui.format_minutes_relative(cfg.work_week * 60, total_minutes),
            coloured("yellow", start_dt.format("Do MMM")),
            coloured("yellow", end_dt.format("Do MMM")),
        )
    )

    hours_per_day = (cfg.work_week * 60) / 5
    today = arrow.now(tz=cfg.time_zone).ceil("day")
    today_ymd = today.format("YYYYMMDD")
    is_away = state.is_away()
    for ymd in sorted(days.keys()):
        dt = days[ymd]["dt"]
        minutes = days[ymd]["minutes"]
        edited = days[ymd]["edited"]
        current = not is_away and ymd == today_ymd

        # don't report on the weekend unless there were hours logged
        if dt.weekday() > 4 and minutes == 0:
            continue

        # only report future dates if there's edits
        if dt > today and not edited:
            continue

        print(
            "%s %s %s%s%s"
            % (
                ui.format_minutes(minutes),
                "%-9s" % dt.format("dddd"),
                ui.format_minutes_relative(hours_per_day, minutes),
                " %s" % ui.CHAR_EDITED if edited else "",
                " %s" % ui.CHAR_CURRENT if current else "",
            )
        )

    if status:
        invoke(["status"])
