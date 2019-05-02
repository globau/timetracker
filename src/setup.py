import os
import sys
from pathlib import Path
from subprocess import check_call

root_path = Path(__file__).parent.parent.resolve()
venv_path = root_path / "venv"
bin_path = venv_path / "bin"
activate_file = bin_path / "activate_this.py"


FIRST_RUN_HELP = """
Use `tt week` (or just `tt`) to view your current hours.
The output will look like:

33:33 WEEK      ⦗-04:27⦘ 29th Apr - 5th May
08:12 Monday    ⦗+00:36⦘
09:42 Tuesday   ⦗+02:06⦘
08:01 Wednesday ⦗+00:25⦘
07:38 Thursday  ⦗+00:02⦘
Away for 2h28m

This shows:
- I've worked 33 hours 33 minutes so far this week.
- I have 4 hours 27 minutes left before I hit my hours for the week.
- On Monday I worked for 8 hours 12 minutes, which is 36 minutes over
  the hours for that day.
- I'm currently away from my computer, and have been for almost 2.5 hours.

You can also see daily (`tt day`) and monthly (`tt month`) breakdowns.
Run `tt -h` to view all available commands.
"""


def _activate_venv():
    if "VIRTUAL_ENV" in os.environ:
        return

    if not venv_path.exists():
        print("timetracker not configured: run 'tt configure'")
        sys.exit(1)

    with open(activate_file) as f:
        code = compile(f.read(), activate_file, "exec")
    exec(code, dict(__file__=activate_file))
    sys.executable = str(bin_path / "python")


def _create_venv():
    if not venv_path.exists():
        check_call(["virtualenv", "-p", "python3", "venv", "--quiet"], cwd=root_path)

    check_call(
        ["%s/pip" % bin_path]
        + ["install", "--no-warn-script-location", "--upgrade", "--quiet"]
        + ["-r", str(root_path / "src/requirements.txt")]
    )


def _install_state_scripts():
    import cfg
    from harness import logger
    import shutil

    if cfg.on_away_file.exists() or cfg.on_back_file.exists():
        return

    logger.info("creating on-away and on-back scripts in ~/.timetracker")
    scripts_path = cfg.src_path / "scripts"
    for src_file in scripts_path.glob("*"):
        dst_file = cfg.dot_path / src_file.name
        if not dst_file.exists():
            logger.debug("%s -> %s" % (src_file, dst_file))
            shutil.copy(str(src_file), str(dst_file))


def _prompt(prompt, *, required=False, default=None, validator=None):
    from harness import logger
    from terminal import coloured

    assert callable(validator)

    if default:
        prompt = "%s (%s)" % (prompt, default)
    prompt = "%s: " % prompt

    try:
        while True:
            res = input(coloured("green", prompt)).strip()

            if res == "":
                if required:
                    continue
                if default:
                    res = default

            if validator:
                try:
                    res = validator(res)
                except ValueError as e:
                    if str(e):
                        logger.error(e)
                    continue

            return res
    except KeyboardInterrupt:
        print("")
        sys.exit(1)


def _ask(prompt, options, *, default=None):
    def _check(value):
        value = value.lower()
        if value not in options:
            raise ValueError("")
        return value

    return _prompt(prompt, default=default, required=not default, validator=_check)


def _check_tz(value):
    from dateutil import tz

    if "/" not in value:
        value = value.upper()

    if not tz.gettz(value):
        raise ValueError("'%s' is not a valid timezone" % value)
    return value


def _check_int(value):
    try:
        return int(value)
    except ValueError:
        raise ValueError("'%s' is not an integer" % value)


def configure():
    print("configuring python")
    _create_venv()
    _activate_venv()

    from harness import MainWrapper

    MainWrapper(_configure_main)


def _configure_main():
    import cfg
    import database
    import launchd

    from harness import logger

    logger.info("configuring timetracker")
    is_first_run = not cfg.settings_file.exists()

    settings = {
        "work_week": _prompt(
            "Hours of work per week", default=cfg.work_week, validator=_check_int
        ),
        "auto_away_time": _prompt(
            "Auto-away idle time [minutes]",
            default=cfg.auto_away_time,
            validator=_check_int,
        ),
    }

    run_on_login = (
        _ask(
            "Run timetracker on login?",
            "yn",
            default="y" if launchd.pid_of() is not None else "n",
        )
        == "y"
    )

    cfg.update_settings(settings, write_to_disk=True)

    if not cfg.db_file.exists():
        logger.info("initialising database")
    else:
        logger.info("updating database")
    database.init_schema()

    _install_state_scripts()

    if run_on_login:
        launchd.install()
    else:
        launchd.uninstall()

    logger.info("done")

    if not launchd.pid_of():
        logger.warning("timetracker daemon is not running")

    if is_first_run:
        logger.info(FIRST_RUN_HELP)


def init():
    if len(sys.argv) > 1 and sys.argv[1] == "configure":
        configure()
        sys.exit(0)

    _activate_venv()
