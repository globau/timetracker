import database
import ui
from command import Command


class Log(Command):
    @staticmethod
    def add_args(parser):
        command = parser.add_parser("log", help="logs for a day")
        command.add_argument(
            "date", nargs="?", default="today", help="date to report on"
        )
        return command

    @staticmethod
    def execute(args):
        dt = ui.parse_date(args.date)

        print(dt.format("ddd Do MMM"))
        logs = database.logs(dt)
        if logs:
            for log in logs:
                print(
                    "%s %s %s"
                    % (log.dt.format("HH:mm:ss"), log.state.upper(), log.reason)
                )
        else:
            print("(empty)")
