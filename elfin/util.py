
from typing import NoReturn
import sys


def fatal(s: str) -> NoReturn:
    print("FATAL: " + s, file=sys.stderr)
    sys.exit(1)


def error(s: str) -> None:
    print("ERROR: " + s, file=sys.stderr)
