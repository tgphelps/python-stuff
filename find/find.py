#!/usr/bin/env python


"""
find.py: find files matching criteria

Usage:
    find.py  [ --type=t ] DIR ...

Options:
    -h --help     Show this message.
    --version     Show version.
"""

import os
import os.path
import stat
from typing import Optional
import docopt  # type: ignore
import util


VERSION = '0.00'


class Globals:
    ftype: Optional[str]
    pass


g = Globals
g.ftype = None


def main() -> None:
    args = docopt.docopt(__doc__, version=VERSION)
    print('args:', args)
    util.validate_args(args)
    g.ftype = args['--type']
    if args['--type']:
        g.ftype = args['--type']
    for dir in args['DIR']:
        do_all_files(dir)


def do_all_files(dir: str) -> None:
    for root, dirs, files in os.walk(dir):
        for name in dirs:
            if g.ftype in (None, 'd'):
                path = os.path.join(root, name)
                print(path)
        for name in files:
            if g.ftype != 'd':
                do_path(root, name)


def do_path(root: str, name: str) -> None:
    # Should check ftype
    path = os.path.join(root, name)
    st = os.lstat(path)
    if g.ftype == 'f' and not stat.S_ISREG(st.st_mode):
        return
    if g.ftype == 'l' and not stat.S_ISLNK(st.st_mode):
        return
    print(path)


if __name__ == '__main__':
    main()
