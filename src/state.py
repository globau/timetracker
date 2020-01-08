import subprocess
from contextlib import suppress

import cfg
import database
from harness import logger
from process import check_output


def away_now_file():
    return cfg.away_now_file if cfg.away_now_file.exists() else None


def is_away():
    return cfg.is_away_file.exists()


def set_away(*, away=False, back=False, reason=None):
    assert away or back
    assert reason

    if away:
        logger.debug("setting away: %s" % reason)
        database.log_state_change("away", reason)
        database.remove_empty_ranges()

        cfg.away_now_file.touch(exist_ok=True)
        cfg.is_away_file.touch(exist_ok=True)

        if cfg.on_away_file.exists():
            logger.debug("executing: %s" % cfg.on_away_file)
            subprocess.Popen([str(cfg.on_away_file)], cwd=cfg.dot_path)

    else:
        logger.debug("setting back: %s" % reason)
        database.log_state_change("back", reason)

        with suppress(FileNotFoundError):
            cfg.is_away_file.unlink()
        with suppress(FileNotFoundError):
            cfg.away_now_file.unlink()

        if cfg.on_back_file.exists():
            logger.debug("executing: %s" % cfg.on_back_file)
            subprocess.Popen([str(cfg.on_back_file)], cwd=cfg.dot_path)


def idle_time():
    # osx idle time, in seconds
    ioreg = check_output(["ioreg", "-c", "IOHIDSystem"], debug_log_output=False)
    for line in ioreg.splitlines():
        #       | |   "HIDIdleTime" = 63319375
        if line.strip(" |").startswith('"HIDIdleTime"'):
            return round(int(line.split("=")[-1]) / 10 ** 9)
    return 0
