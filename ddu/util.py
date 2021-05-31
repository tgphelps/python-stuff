
import platform
import sys
from typing import NoReturn

import logging

# os_type = 'Windows' if this is windows

os_is_windows = platform.system() == 'Windows'


def fatal(msg: str) -> NoReturn:
    """Print fatal error message on stderr, log it, and EXIT."""
    s = f'FATAL: {msg}'
    print(s, file=sys.stderr)
    logging.critical(s)
    sys.exit(2)


def msg(s: str) -> None:
    """Print message on stderr, and log it."""
    print(s, file=sys.stderr)
    logging.info(s)


def warning(s: str) -> None:
    """Print warning message on stderr, and log it."""
    msg = 'WARNING: ' + s
    print(msg, file=sys.stderr)
    logging.warning(s)


def error(s: str) -> None:
    """Print error message on stderr, and log it."""
    msg = 'ERROR: ' + s
    print(msg, file=sys.stderr)
    logging.warning(s)
