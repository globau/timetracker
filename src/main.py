import argparse
import sys

import cfg
from command import load_commands
from harness import setup_logger_file


def parse_args():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(help="", metavar="  COMMAND", dest="command")
    commands.required = True
    load_commands(commands)

    return parser.parse_args()


def main():
    setup_logger_file(cfg.log_file)

    if len(sys.argv) == 1:
        sys.argv.append("week")
    args = parse_args()
    args.func(args)
