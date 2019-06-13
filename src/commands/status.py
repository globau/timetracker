import database
import launchd
import state
from datetime_util import pretty_timedelta
from main import cli, click


@click.option("--no-daemon", is_flag=True, help="don't show daemon status")
@cli.command(aliases=["st"], help="show status")
def status(no_daemon):
    idle_time = state.idle_time()
    pid = launchd.pid_of()

    if state.is_away():
        print("Away for %s" % pretty_timedelta(idle_time, strip_seconds=True))

    elif idle_time < 5:
        dtr = database.current_range()
        if dtr:
            print(
                "Working for %s"
                % pretty_timedelta(dtr.minutes * 60, strip_seconds=True)
            )

        elif pid is not None:
            print("Working for 0s")

    else:
        print("Idle for %s" % pretty_timedelta(idle_time, strip_seconds=True))

    if not no_daemon:
        if pid is None:
            print("Daemon is not running")
        else:
            print("Daemon running (pid %s)" % pid)
