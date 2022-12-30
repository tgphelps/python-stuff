#!/usr/bin/env python

"""
test.py: test the filter

Usage:
    test.py [-d] [-n <count>] [<file>...]

Options:
    -h --help     Show this message.
    --version     Show version.
    -d            Enable debugging.
    -n <count>    Set count.
"""

# import docopt  # type:ignore

from filter import filter

VERSION = '0.0'


class myfilter(filter):
    def first(self) -> None:
        # print('myfirst')
        pass

    def last(self) -> None:
        # print('mylast')
        pass

    def foreach(self, info: tuple[str, int, str]) -> None:
        print(info[2])


def main() -> None:
    f = myfilter(__doc__, VERSION)
    f.run()


if __name__ == '__main__':
    main()
