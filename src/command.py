import abc
import importlib

import cfg


class Command(object):
    # base class for commands

    @staticmethod
    @abc.abstractmethod
    def add_args(parser):
        pass

    @staticmethod
    @abc.abstractmethod
    def execute(args):
        pass


def load_commands(parser):
    # load all commands
    path = cfg.src_path / "commands"
    for name in [f.stem for f in sorted(path.glob("*.py"))]:
        importlib.import_module("commands.%s" % name)

    # add args
    for cls in Command.__subclasses__():
        assert isinstance(cls, Command)
        command = cls.add_args(parser)
        if command:
            command.set_defaults(func=cls.execute)
