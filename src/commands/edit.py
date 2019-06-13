import database
import ui
from harness import Error
from main import cli, click, invoke


@click.argument("reason", nargs=-1)
@click.argument("adjust")
@click.argument("date")
@cli.command(
    aliases=["e"],
    short_help="adjust hours",
    help="""
adjust hours, where DATE is the date to adjust (eg. 'today'),
ADJUST is the amount (eg. '+1d' or '-2h'), and REASON is brief
description (eg. 'pto').
""",
)
def edit(date, adjust, reason):
    # parse args
    try:
        dt = ui.parse_date(date, context="day")
        adjust_mins = ui.parse_adjustment(adjust)
        reason = (" ".join(reason)).strip()
    except ValueError as e:
        raise Error(e)

    # validate reason
    if not reason:
        raise Error("'reason' must be provided")

    # validate adjustment
    if abs(adjust_mins) > 60 * 24:
        raise Error("adjustment is too large")

    minutes = 0
    for dtr in database.active_ranges(dt, dt.ceil("day")):
        minutes += dtr.minutes

    edits = database.edits(dt)
    minutes = 0
    for e in edits:
        minutes += e.minutes

    if minutes + adjust_mins > 60 * 24:
        raise Error(
            "total adjustments for %s would exceed 24 hours" % dt.format("Do MMM")
        )
    if minutes + adjust_mins < 0:
        raise Error("total adjustments for %s would be negative" % dt.format("Do MMM"))

    # insert into db and show summary
    database.log_edit(dt, adjust_mins, reason)

    invoke(["day"])
