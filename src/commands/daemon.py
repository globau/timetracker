import atexit
import errno
import fcntl
import os
import time
import types

import cfg
from harness import Error, logger
from main import cli, invoke

G = types.SimpleNamespace(lock_fh=0)


def exit_handler():
    logger.info("daemon stopped (pid %s)", os.getpid())


@cli.command(help="run as daemon (foreground)")
def daemon():
    G.lock_fh = open(cfg.lock_file, "w")
    try:
        fcntl.lockf(G.lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError as e:
        if e.errno not in (errno.EACCES, errno.EAGAIN):
            raise
        raise Error("daemon already running")

    logger.info("daemon started (pid %s)", os.getpid())
    atexit.register(exit_handler)

    cfg.pid_file.write_text("%s\n" % os.getpid())
    while True:
        start_time = time.time()
        invoke(["update"])
        delay = 60 - (time.time() - start_time)
        if delay > 0:
            logger.debug("sleeping for %ss", delay)
            time.sleep(delay)
