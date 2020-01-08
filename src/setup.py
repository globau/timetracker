import os
import site
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
07:38 Thursday  ⦗+00:02⦘ ←
Working for 1h39m

This shows:
- I've worked 33 hours 33 minutes so far this week.
- I have 4 hours 27 minutes left before I hit my hours for the week.
- On Monday I worked for 8 hours 12 minutes, which is 36 minutes over
  the hours for that day.
- I'm currently working, and have been for 1 hour 39 minutes.

You can also see daily (`tt day`) and monthly (`tt month`) breakdowns.
Run `tt -h` to view all available commands.
"""


def _activate_venv():
    if "VIRTUAL_ENV" in os.environ:
        return

    if not venv_path.exists():
        print("timetracker not configured: run 'tt configure'")
        sys.exit(1)

    # setup env
    os.environ["PATH"] = os.pathsep.join(
        [str(bin_path)] + os.environ.get("PATH", "").split(os.pathsep)
    )
    os.environ["VIRTUAL_ENV"] = str(venv_path)
    site.addsitedir(
        str(
            venv_path
            / "lib"
            / "python{}.{}".format(*sys.version_info)
            / "site-packages"
        )
    )

    # setup path
    prev_path = set(sys.path)
    new_path = list(sys.path)
    sys.path[:] = [p for p in new_path if p not in prev_path] + [
        p for p in new_path if p in prev_path
    ]

    # setup sys
    sys.real_prefix = sys.prefix
    sys.prefix = str(venv_path)
    sys.executable = str(bin_path / "python")


def _create_venv():
    if not venv_path.exists():
        # work around py3.3+, homebrew, and virtualenv issue
        # https://bugs.python.org/issue22490
        # https://github.com/pypa/virtualenv/issues/845
        env = os.environ.copy()
        env.pop("__PYVENV_LAUNCHER__", None)

        check_call(["python3", "-m", "venv", "venv"], cwd=root_path, env=env)

    check_call(
        ["%s/pip" % bin_path]
        + ["install", "--no-warn-script-location", "--upgrade", "--quiet"]
        + ["-r", str(root_path / "src/requirements.txt")]
        + ["pip"]
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
            logger.debug("%s -> %s", src_file, dst_file)
            shutil.copy(str(src_file), str(dst_file))


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
    import ui

    from harness import logger

    logger.info("configuring timetracker")
    is_first_run = not cfg.settings_file.exists()

    settings = {
        "work_week": ui.input_ex(
            "Hours of work per week", default=cfg.work_week, validator=_check_int
        ),
        "auto_away_time": ui.input_ex(
            "Auto-away idle time [minutes]",
            default=cfg.auto_away_time,
            validator=_check_int,
        ),
    }

    run_on_login = (
        ui.input_ex(
            "Run timetracker on login?",
            options="yn",
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
