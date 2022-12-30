#!/usr/bin/env python

"""
wc.py: print count of total lines

Usage:
    wc.py [<file>...]

Options:
    -h --help     Show this message.
    --version     Show version.
"""

# import docopt  # type:ignore

from filter import filter

VERSION = '0.0'


class myfilter(filter):
    def first(self):
        self.lines = 0

    def foreach(self, info: tuple[str, int, str]) -> None:
        self.lines += 1

    def last(self):
        print(self.lines)


def main() -> None:
    f = myfilter(__doc__, VERSION)
    f.run()


if __name__ == '__main__':
    main()
