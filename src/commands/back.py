import state
import ui
from command import Command


class Back(Command):
    @staticmethod
    def add_args(parser):
        command = parser.add_parser("back", aliases=["b"], help="set back now")
        return command

    @staticmethod
    def execute(args):
        state.set_away(back=True, reason="requested")
        ui.notify(back=True)
