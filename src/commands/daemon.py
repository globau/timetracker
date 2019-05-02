import os
import time
from commands.update import Update

import cfg
from command import Command
from harness import logger


class Daemon(Command):
    @staticmethod
    def add_args(parser):
        command = parser.add_parser("daemon", help="run as daemon (foreground)")
        return command

    @staticmethod
    def execute(args):
        cfg.pid_file.write_text("%s\n" % os.getpid())
        while True:
            start_time = time.time()
            Update.execute(None)
            delay = 60 - (time.time() - start_time)
            if delay > 0:
                logger.debug("sleeping for %ss" % delay)
                time.sleep(delay)
