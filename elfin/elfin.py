#!/usr/bin/env python

"""
elfin.py: Intel x64 ELF file investigator

Usage:
    elfin.py [-l] ELF

Options:
    -h --help           Show this screen, and exit.
    -l --log            Create debugging log file
"""

from typing import Dict, Any

import docopt  # type: ignore

import log
import util
import sys

import Elf
import commands


# Constants
VERSION = '0.01'
LOG_FILE = 'LOG.txt'


# Global variables

class Globals:
    log:  bool
    file: str


g = Globals()
g.log = False
g.file = ''


def main() -> None:
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 8):
        util.fatal("Python 3.8 or above is required.")
    args = docopt.docopt(__doc__, version=VERSION)
    # print(args)
    parse_cmd_line(args)
    if g.log:
        log.log_open(LOG_FILE)
    ok, err = Elf.is_elf64_file(g.file)
    if not ok:
        util.fatal(f"invalid or unreadable ELF {g.file}. Error: {err}")

    # Parse the ELF file
    elf = Elf.Elf(g.file)

    # commands.run_cmd("p hdr", elf)
    commands.run(elf)

    elf.close()
    if g.log:
        log.log_close()


def parse_cmd_line(args: Dict[str, Any]) -> None:
    if args['--log']:
        g.log = True
    g.file = args['ELF']


if __name__ == '__main__':
    main()
