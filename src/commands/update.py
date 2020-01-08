import cfg
import database
import state
import ui
from datetime_util import mmss
from harness import logger
from main import cli


@cli.command(hidden=True)
def update():
    idle_time = state.idle_time()
    away_now_file = state.away_now_file()
    is_away = state.is_away()

    logger.debug("idle time: %ss", idle_time)
    logger.debug("is away: %s", is_away)

    # check if there's a request to manually set as away
    if away_now_file:
        logger.debug("found away_now file")

        # if we're already away we can delete the away-now file to enable auto-back
        if is_away:
            if idle_time >= cfg.auto_away_time * 60:
                logger.debug("removing away_now file")
                away_now_file.unlink()
            else:
                logger.debug("nothing to do")

        # otherwise mark as away
        else:
            ui.notify(away=True)
            state.set_away(away=True, reason="away-now requested")

        return

    # auto-back
    if is_away and idle_time <= cfg.idle_check_time:
        logger.debug("state: auto back")

        # must be back
        state.set_away(back=True, reason="idle for %s" % mmss(idle_time))
        ui.notify(back=True)

        database.log_active()

    # auto-away
    elif idle_time >= cfg.auto_away_time * 60:
        logger.debug("state: auto away")
        if not is_away:
            state.set_away(away=True, reason="idle for %s" % mmss(idle_time))
            ui.notify(away=True)

        # away-now file is stale
        if away_now_file:
            away_now_file.unlink()

    # not away
    else:
        logger.debug("state: not away")
        database.log_active()
