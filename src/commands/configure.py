from command import Command


class Configure(Command):
    @staticmethod
    def add_args(parser):
        command = parser.add_parser("configure", help="install/configure timetracker")
        return command

    @staticmethod
    def execute(args):
        # implemented in src/setup.py::configure()
        pass
