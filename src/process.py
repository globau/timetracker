import logging
import re
import subprocess

from harness import logger


def _command_shell_str(command):
    find_unsafe = re.compile(r"[^\w@%+=:,./-]").search

    def shell_quote(s):
        if not s:
            return "''"
        if not find_unsafe(s):
            return s
        return "'" + s.replace("'", "'\"'\"'") + "'"

    return " ".join(shell_quote(s) for s in command)


def call(command, **kwargs):
    command = [str(el) for el in command]
    logger.debug("$ %s" % _command_shell_str(command))
    kwargs.setdefault("encoding", "UTF-8")

    return subprocess.call(command, **kwargs)


def check_call(command, **kwargs):
    command = [str(el) for el in command]
    logger.debug("$ %s" % _command_shell_str(command))
    kwargs.setdefault("encoding", "UTF-8")

    return subprocess.check_call(command, **kwargs)


def check_output(command, debug_log_output=True, **kwargs):
    command = [str(el) for el in command]
    logger.debug("$ %s" % _command_shell_str(command))
    kwargs.setdefault("encoding", "UTF-8")

    output = subprocess.check_output(command, **kwargs)

    if debug_log_output and logger.level == logging.DEBUG:
        for line in output.splitlines():
            logger.debug("> %s" % line)

    return output
