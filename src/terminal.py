import os
import sys

IS_PYCHARM = os.getenv("PYCHARM_HOSTED") == "1"
HAS_ANSI = (
    (hasattr(sys.stdout, "isatty") and sys.stdout.isatty())
    or os.getenv("TERM", "") == "ANSI"
    or IS_PYCHARM
)
if os.getenv("NOANSI") or os.getenv("NO_ANSI"):
    HAS_ANSI = False


def coloured(colour, s):
    if not HAS_ANSI:
        return s

    if colour.startswith("bright-"):
        intensity = "1"
        colour = colour[len("bright-") :]
    else:
        intensity = "0"

    if colour == "red":
        code = "31"
    elif colour == "green":
        code = "32"
    elif colour == "yellow":
        code = "33"
    elif colour == "blue":
        code = "34"
    elif colour == "white":
        code = "37"
    elif colour == "dark-grey":
        code = "90"
    else:
        raise NotImplementedError(colour)

    return "\033[%s;%sm%s\033[0m" % (intensity, code, s)
