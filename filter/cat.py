#!/usr/bin/env python

"""
cat.py: print all lines

Usage:
    cat.py [<file>...]

Options:
    -h --help     Show this message.
    --version     Show version.
"""

# import docopt  # type:ignore

from typing import Tuple

from filter import filter

VERSION = '0.0'


class myfilter(filter):
    def foreach(self, info: Tuple[str, int, str]) -> None:
        try:
            print(info[2])
        except BrokenPipeError:
            pass


def main() -> None:
    f = myfilter(__doc__, VERSION)
    f.run()


if __name__ == '__main__':
    main()
