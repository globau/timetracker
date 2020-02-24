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


def _prepare_subprocess_args(command, kwargs):
    command = [str(el) for el in command]
    if kwargs.get("cwd", ".") != ".":
        logger.debug("$ cd '%s'", kwargs["cwd"])
    logger.debug("$ %s", _command_shell_str(command))
    kwargs.setdefault("encoding", "UTF-8")

    return command, kwargs


def call(command, **kwargs):
    command, kwargs = _prepare_subprocess_args(command, kwargs)
    return subprocess.call(command, **kwargs)


def check_call(command, **kwargs):
    command, kwargs = _prepare_subprocess_args(command, kwargs)
    return subprocess.check_call(command, **kwargs)


def check_output(command, debug_log_output=True, **kwargs):
    command, kwargs = _prepare_subprocess_args(command, kwargs)
    output = subprocess.check_output(command, **kwargs)

    if debug_log_output and logger.level == logging.DEBUG:
        for line in output.splitlines():
            logger.debug("> %s", line)

    return output


def check_outputs(command, **kwargs):
    assert "stdout" not in kwargs
    assert "stderr" not in kwargs

    command, kwargs = _prepare_subprocess_args(command, kwargs)
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs
    )
    stdout, stderr = process.communicate()

    if logger.level == logging.DEBUG:
        for line in stdout.splitlines():
            logger.debug("out> %s", line)
        for line in stderr.splitlines():
            logger.debug("err> %s", line)

    retcode = process.poll()
    if retcode:
        stdout = "%s\n%s" % (stdout.rstrip(), stderr.rstrip())
        raise subprocess.CalledProcessError(retcode, command, output=stdout)

    return stdout, stderr
