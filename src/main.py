import importlib
import sys

import click

import cfg
from click_alias import ClickAliasedGroup
from harness import setup_logger_file

click = click
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(cls=ClickAliasedGroup, context_settings=CONTEXT_SETTINGS)
def cli():
    pass


def main():
    setup_logger_file(cfg.log_file)

    # load commands
    path = cfg.src_path / "commands"
    for name in [f.stem for f in sorted(path.glob("*.py"))]:
        importlib.import_module("commands.%s" % name)

    # default to showing week with status
    if len(sys.argv) == 1:
        sys.argv.extend(["week", "--status"])

    cli()
