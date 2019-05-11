import json
from datetime import datetime
from pathlib import Path

from dateutil import tz
from harness import logger

# paths
dot_path = Path("~/.timetracker").expanduser()
if not dot_path.exists():
    logger.debug("creating %s" % dot_path)
    dot_path.mkdir()
root_path = Path(__file__).parent.parent.resolve()
src_path = root_path / "src"
settings_file = dot_path / "settings.json"
terminal_notifier = (
    src_path / "time-tracker.app/Contents/Resources/"
    "terminal-notifier.app/Contents/MacOS/terminal-notifier"
)


def _load_settings():
    # load settings, with fallback to default values

    try:
        logger.debug("loading %s" % settings_file)
        with open(settings_file) as f:
            settings = json.load(f)
    except FileNotFoundError:
        logger.debug("settings not found")
        settings = {}

    settings.setdefault("work_week", 40)  # hours
    settings.setdefault("auto_away_time", 30)  # minutes

    return settings


def update_settings(settings, *, write_to_disk=False):
    global work_week
    global auto_away_time

    work_week = int(settings["work_week"])
    auto_away_time = int(settings["auto_away_time"])

    if write_to_disk:
        settings_file.write_text(
            "%s\n"
            % json.dumps(
                dict(work_week=work_week, auto_away_time=auto_away_time),
                indent=2,
                sort_keys=True,
            )
        )


# settings
work_week = None
auto_away_time = None
update_settings(_load_settings())

# state/log files
db_file = dot_path / "timetracker.sqlite"
is_away_file = dot_path / "is-away"
away_now_file = dot_path / "away-now"
log_file = dot_path / "timetracker.log"
pid_file = dot_path / "timetracker.pid"

# state change handlers
on_away_file = dot_path / "on-away"
on_back_file = dot_path / "on-back"

# timing
idle_check_time = 60  # seconds

# time zone
time_zone = tz.tzlocal()
time_zone_name = time_zone.tzname(datetime.now())
