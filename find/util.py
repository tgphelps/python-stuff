
import sys
from typing import Dict, NoReturn


def fatal(msg: str) -> NoReturn:
    print('ERROR:', msg, file=sys.stderr)
    sys.exit(1)


def validate_args(args: Dict[str, str]):
    ftype = args['--type']
    if ftype:
        if ftype in ('d', 'f', 'l'):
            pass
        else:
            fatal('bad --type value')
