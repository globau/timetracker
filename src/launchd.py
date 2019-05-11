import sys
from pathlib import Path

import cfg
from harness import Error, logger
from process import call, check_call, check_output

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
            return line[0]
    return None


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
        check_call(["launchctl", "load", LAUNCHD_FILE])
        if pid_of() is None:
            logger.error("failed to install launchd config")
            sys.exit(1)

    else:
        # installed - restart
        restart()


def uninstall():
    if pid_of() is not None:
        logger.info("uninstalling timetracker daemon")
        check_call(["launchctl", "unload", LAUNCHD_FILE])
        call(["launchctl", "remove", LAUNCHD_FILE])

    if LAUNCHD_FILE.exists():
        LAUNCHD_FILE.unlink()


def restart():
    if pid_of() is None:
        raise Error("timetracker daemon is not installed")

    logger.info("restarting timetracker daemon")
    check_call(["launchctl", "unload", LAUNCHD_FILE])
    check_call(["launchctl", "load", LAUNCHD_FILE])
