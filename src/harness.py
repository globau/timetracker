import contextlib
import logging
import os
import sys
import traceback

from terminal import HAS_ANSI, coloured

logger = logging.getLogger("timetracker")

DEBUG = bool(os.getenv("DEBUG"))


class Error(Exception):
    """internal error"""


class SimpleFormatter(logging.Formatter):
    def __init__(self):
        super().__init__("%(message)s")


class ColourFormatter(SimpleFormatter):
    def __init__(self):
        super().__init__()
        self.log_colours = {"WARNING": "blue", "ERROR": "red", "DEBUG": "dark-grey"}

    def format(self, record):
        result = super().format(record)
        if record.levelname in self.log_colours:
            result = coloured(self.log_colours[record.levelname], result)
        return result


def setup_logger(lgr=None):
    if not lgr:
        lgr = logger
    handler = logging.StreamHandler(sys.stdout)
    if HAS_ANSI:
        handler.setFormatter(ColourFormatter())
    else:
        handler.setFormatter(SimpleFormatter())
    lgr.addHandler(handler)
    lgr.setLevel(logging.DEBUG if DEBUG else logging.INFO)


def setup_logger_file(
    filename, lgr=None, *, when="d", interval=1, backups=7, force=False
):
    import logging.handlers

    if not force:
        if sys.stdout.isatty():
            logger.debug("disabling logging to %s: connected to a tty" % filename)
            return
        elif DEBUG:
            logger.debug("disabling logging to %s: debugging" % filename)
            return

    if not lgr:
        lgr = logger
    handler = logging.handlers.TimedRotatingFileHandler(
        filename, when=when, interval=interval, backupCount=backups
    )
    handler.setFormatter(
        logging.Formatter(fmt="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    lgr.addHandler(handler)
    lgr.setLevel(logging.INFO)


class MainWrapper(object):
    def __init__(self, main):
        setup_logger(logger)

        try:
            main()

        except KeyboardInterrupt:
            # ^C should just exit
            sys.exit(1)

        except BrokenPipeError:
            # while technically an abnormal condition, it's expected (eg. piping to
            # `head` will close stdout).
            # need to flush and close handles as flush_std_files runs during python
            # shutdown, triggering another BrokenPipeError we won't be able to catch
            with contextlib.suppress(BrokenPipeError):
                sys.stdout.flush()
                sys.stdout.close()
            with contextlib.suppress(BrokenPipeError):
                sys.stderr.flush()
                sys.stderr.close()
            sys.exit(0)

        except Error as e:
            # never show stack for our error messages
            logger.error(e)
            sys.exit(1)

        except (AssertionError, KeyError, NameError, TypeError) as e:
            # always show stack for coding issues
            logger.exception(e)
            sys.exit(1)

        except OSError as e:
            if e.filename:
                # include filename in i/o errors
                logger.error("%s: %s" % (e.strerror, e.filename))
            else:
                logger.error(e.strerror or e)
            sys.exit(1)

        except Exception as e:
            # only show stack when debugging
            if logger.level == logging.DEBUG:
                logger.error(traceback.format_exc())
            else:
                logger.error("%s: %s" % (e.__class__.__name__, e))
            sys.exit(1)
