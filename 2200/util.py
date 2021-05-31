
from typing import NoReturn
import sys


def fatal(s: str) -> NoReturn:
    print("FATAL: " + s, file=sys.stderr)
    sys.exit(1)


def error(s: str) -> None:
    print("ERROR: " + s, file=sys.stderr)


def qw_to_ascii(n: int) -> str:
    if n >= 0x7f:
        return '.'
    else:
        return chr(n)


def toprint(n: int) -> str:
    if n < 32 or n > 126:
        return '.'
    else:
        return chr(n)
