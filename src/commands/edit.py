import commands.day

import database
import ui
from command import Command
from harness import Error


class Edit(Command):
    @staticmethod
    def add_args(parser):
        command = parser.add_parser("edit", aliases=["e"], help="adjust hours")
        command.add_argument("date", help="date to edit")
        command.add_argument("adjust", help="adjustment")
        command.add_argument("reason", nargs="*", help="reason")
        return command

    @staticmethod
    def execute(args):
        try:
            # if the date is an adjustment then work on today
            adjust_mins = ui.parse_adjustment(args.date)
            dt = ui.parse_date("today")
            reason = ("%s %s" % (args.adjust, " ".join(args.reason))).strip()
        except ValueError:
            # otherwise parse args in expected order
            try:
                dt = ui.parse_date(args.date)
                adjust_mins = ui.parse_adjustment(args.adjust)
                reason = (" ".join(args.reason)).strip()
            except ValueError as e:
                raise Error(e)

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
        for edit in edits:
            minutes += edit.minutes

        if minutes + adjust_mins > 60 * 24:
            raise Error(
                "total adjustments for %s would exceed 24 hours" % dt.format("Do MMM")
            )
        if minutes + adjust_mins < 0:
            raise Error(
                "total adjustments for %s would be negative" % dt.format("Do MMM")
            )

        database.log_edit(dt, adjust_mins, reason)

        commands.day.Day.execute(None)
