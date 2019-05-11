import cfg
import database
import state
import ui
from main import cli, click
from terminal import coloured


@click.argument("date", required=False, default="today")
@cli.command(aliases=["d"], help="summary of your day")
def day(date):
    start_dt = ui.parse_date(date, context="day")
    end_dt = start_dt.clone().ceil("day")

    ranges = database.active_ranges(start_dt, end_dt)
    edits = database.edits(start_dt)
    current_range = database.current_range() if not state.is_away() else None

    # tally minutes
    minutes = 0
    for dtr in ranges:
        minutes += dtr.minutes
    for edit in edits:
        minutes += edit.minutes

    # header
    print(
        "%s %s %s"
        % (
            coloured("yellow", ui.format_minutes(minutes)),
            coloured("yellow", start_dt.format("ddd Do MMM")),
            ui.format_minutes_relative(cfg.work_week * 60 / 5, minutes),
        )
    )

    # active ranges
    previous_end_dt = None
    for dtr in ranges:
        # ignore zero-minute ranges
        if not dtr.minutes:
            continue

        current = (
            current_range
            and dtr.start_dt == current_range.start_dt
            and dtr.end_dt == current_range.end_dt
        )

        gap = None
        if previous_end_dt:
            delta = dtr.start_dt - previous_end_dt
            gap = ui.format_minutes(delta.total_seconds() / 60)
        previous_end_dt = dtr.end_dt

        print(
            "%5s %s%s%s %s%s"
            % (
                coloured("dark-grey", gap) if gap else "",
                dtr.start_dt.format("HH:mm"),
                coloured("dark-grey", "-"),
                dtr.end_dt.format("HH:mm"),
                coloured("green", ui.format_minutes(dtr.minutes)),
                " %s" % ui.CHAR_CURRENT if current else "",
            )
        )

    # edits
    for edit in edits:
        print("%s %s" % (ui.format_minutes_relative(0, edit.minutes), edit.reason))
