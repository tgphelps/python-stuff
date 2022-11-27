#!/usr/bin/env python

"""
disasm.py: Disassemble an x64 relocatable ELF file

Usage:
    disasm.py [ -d ] ELF

Options:
    -h --help           Show this screen, and exit.
    -d --debug          Turn on debug mode
"""


import sys
import docopt  # type: ignore
from tracing import trace_open, trace_close


# Constants
VERSION = '0.01'


# Global variables

class Globals:
    debug: bool
    pass


g = Globals()
g.debug = False


def main():
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 8):
        print("Python 3.8 or above is required.")
        sys.exit(1)
    args = docopt.docopt(__doc__, version=VERSION)
    # print(args)
    if args['--debug']:
        g.debug = True
    if g.debug:
        trace_open('TRACE.txt')
    # Insert real work here.
    trace_close()


if __name__ == '__main__':
    main()
