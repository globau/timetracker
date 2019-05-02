from command import Command


class Restart(Command):
    @staticmethod
    def add_args(parser):
        command = parser.add_parser("restart", help="restart daemon")
        return command

    @staticmethod
    def execute(args):
        import launchd

        launchd.restart()
