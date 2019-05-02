import state
import ui
from command import Command


class Away(Command):
    @staticmethod
    def add_args(parser):
        command = parser.add_parser("away", aliases=["a"], help="set away now")
        return command

    @staticmethod
    def execute(args):
        state.set_away(away=True, reason="requested")
        ui.notify(away=True)
