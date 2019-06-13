import os
import time

import cfg
from harness import logger
from main import cli, invoke


@cli.command(help="run as daemon (foreground)")
def daemon():
    cfg.pid_file.write_text("%s\n" % os.getpid())
    while True:
        start_time = time.time()
        invoke(["update"])
        delay = 60 - (time.time() - start_time)
        if delay > 0:
            logger.debug("sleeping for %ss" % delay)
            time.sleep(delay)
