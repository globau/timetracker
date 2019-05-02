import cfg
import database
import launchd
import state
from command import Command
from datetime_util import pretty_timedelta


class Status(Command):
    @staticmethod
    def add_args(parser):
        command = parser.add_parser("status", aliases=["st"], help="show status")
        return command

    @staticmethod
    def execute(args):
        idle_time = state.idle_time()

        if state.is_away():
            print("Away for %s" % pretty_timedelta(idle_time, strip_seconds=True))

        elif idle_time < 5:
            dtr = database.current_range()
            if dtr:
                print(
                    "Working for %s"
                    % pretty_timedelta(dtr.minutes * 60, strip_seconds=True)
                )
            else:
                if launchd.pid_of():
                    print("Working for 0s")
                else:
                    print("Working, no daemon")

        else:
            print("Idle for %s" % pretty_timedelta(idle_time, strip_seconds=True))
