import os
import sys
from pathlib import Path

import cfg
from harness import Error, logger
from process import check_call, check_output, check_outputs

NAME = "uno.glob.timetracker"
LAUNCHD_FILE = Path("~/Library/LaunchAgents/%s.plist" % NAME).expanduser()
TEMPLATE = "\n".join(
    [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
        + '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
        '<plist version="1.0">',
        "<dict>",
        "    <key>KeepAlive</key>",
        "    <true/>",
        "    <key>Label</key>",
        "    <string>{name}</string>",
        "    <key>LimitLoadToSessionType</key>",
        "    <string>Aqua</string>",
        "    <key>ProcessType</key>",
        "    <string>Background</string>",
        "    <key>ProgramArguments</key>",
        "    <array>",
        "        <string>{py}</string>",
        "        <string>{tt}</string>",
        "        <string>daemon</string>",
        "    </array>",
        "    <key>RunAtLoad</key>",
        "    <true/>",
        "</dict>",
        "</plist>",
    ]
)


def pid_of():
    # returns pid of running launch agent, None if not installed, 0 if
    # installed but not running

    for line in check_output(
        ["launchctl", "list"], debug_log_output=False
    ).splitlines():
        line = line.split("\t")
        if line[-1] == NAME:
            return int(line[0])
    return None


def _start_daemon():
    check_call(["launchctl", "bootstrap", "gui/%s" % os.getuid(), LAUNCHD_FILE])


def _stop_daemon():
    check_outputs(["launchctl", "unload", LAUNCHD_FILE])


def install():
    tt_file = cfg.src_path.parent / "tt"
    py_file = sys.executable

    xml = TEMPLATE.format(py=py_file, tt=tt_file, name=NAME)

    if not LAUNCHD_FILE.exists():
        # create launchd plist file
        logger.info("installing timetracker daemon")
        LAUNCHD_FILE.write_text(xml)

    if pid_of() is None:
        # not installed - load (and start)
        logger.info("starting timetracker daemon")
        _start_daemon()
        if pid_of() is None:
            logger.error("failed to install launchd config")
            sys.exit(1)

    else:
        # installed - restart
        restart()


def uninstall():
    if pid_of() is not None:
        logger.info("uninstalling timetracker daemon")
        _stop_daemon()

    if LAUNCHD_FILE.exists():
        LAUNCHD_FILE.unlink()


def restart():
    if pid_of() is None:
        raise Error("timetracker daemon is not installed")

    logger.info("restarting timetracker daemon")
    _stop_daemon()
    _start_daemon()
