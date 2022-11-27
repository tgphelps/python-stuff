#!/usr/bin/env python

"""
diskedit.py: Interactively edit a 2200 disk

Usage:
    fedit.py [ -d ] [ -r ] FILE

Options:
    -h --help           Show this screen, and exit.
    -d --debug          Turn on debug mode
    -r --readonly       Prevent attempts to change file.
"""


import sys
from typing import List

import docopt  # type: ignore

from disk import Disk
from fdata import fd
import util
from u2200 import *


# Constants
VERSION = '0.01'
PREP_FACTOR = 4  # 4 2200 sectors per disk sector
WPS = 28  # words per 2200 sector


class Cache:
    "Class to read disk sectors and provide 2200 sectors."
    def __init__(self, d: Disk):
        self.disk = d
        self.cur_sector: int = -1  # no sector loaded
        self.buffer: List[int] = []

    def load_sector(self, n: int) -> None:
        "Return pointer to a 2200 sector."
        needed_sector = n // PREP_FACTOR
        if self.cur_sector != needed_sector:
            if g.debug:
                print('reading disk sector:', needed_sector)
            self.buffer = self.disk.read_sector(needed_sector)
            self.cur_sector = needed_sector
            if g.debug:
                print('buff:', self.buffer[0:4])

    def get_sector(self, n: int) -> List[int]:
        "Return the requested 28-word sector."
        self.load_sector(n)
        offset = (n % PREP_FACTOR) * WPS
        if g.debug:
            print('buffer offset:', offset)
        return self.buffer[offset: offset + WPS]


# Global variables

class Globals:
    debug: bool
    readonly: bool
    char_mode: str
    disk: Disk
    cache: Cache
    cur_sector: int


g = Globals()
g.debug = False
g.readonly = False
g.char_mode = 'f'  # fieldata
g.cur_sector = -1  # None yet


def main() -> None:
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 8):
        util.fatal("Python 3.8 or above is required.")
    args = docopt.docopt(__doc__, version=VERSION)
    # print(f'args: {args}')
    if args['--debug']:
        g.debug = True
    if args['--readonly']:
        g.readonly = True
        print('READ-ONLY mode')

    g.disk = Disk(args['FILE'], g.debug)
    g.cache = Cache(g.disk)
    process()


def process() -> None:
    goto_sector(['go', '0'])
    last_cmd = 'go 0'
    while True:
        cmd = read_command()
        fld = cmd.split()
        if len(fld) == 0:
            continue
        if g.debug:
            print(fld)
        if fld[0] == 'exit':  # exit
            break
        elif fld[0] == 'g':  # go to sector
            goto_sector(fld)
        elif fld[0] == 'track':  # go to track
            goto_track(fld)
        elif fld[0] == 'd':  # dump
            dump(fld)
        elif fld[0] == 'vol1':  # print VOL1 header
            print_vol1(fld)
        elif fld[0] == 'p':  # print last command
            print(last_cmd)
        elif fld[0] == 'help':  # print help msg
            print_help()
        elif fld[0] == 'fdata':
            g.char_mode = 'f'
        elif fld[0] == 'ascii':
            g.char_mode = 'a'
        elif fld[0] == 'debug':  # debug on/off
            if fld[1] == 'on':
                g.debug = True
            else:
                g.debug = False
            print(f'debug = {g.debug}')
        else:
            print('bad command')
        last_cmd = cmd


def goto_sector(fld: List[str]) -> None:
    if not params_okay(fld, 1):
        return
    g.cur_sector = int(fld[1])
    g.cache.load_sector(g.cur_sector)


def goto_track(fld: List[str]) -> None:
    if not params_okay(fld, 1):
        return
    g.cur_sector = int(fld[1]) * 64
    g.cache.load_sector(g.cur_sector)


def print_vol1(fld: List[str]) -> None:
    if not params_okay(fld, 0):
        return
    sec = g.cache.get_sector(g.cur_sector)
    assert len(sec) == WPS
    # octal_dump(sec)
    vol1 = w2ascii(sec[0])
    print('vol1 =', vol1)
    packid = w2ascii(sec[1])
    x = w2ascii(sec[2])[0:2]
    packid += x
    print('pack-id =', packid)
    # 'first dir track' is the sector address of sector 0 of that track
    # The NEXT sector is the interesting one.
    print('first dir track =', sec[3])
    print('recs/track =', h1(sec[4]))
    print('words/rec =', h2(sec[4]))
    print('s0+s1+hmbt+pad =', h1(sec[9]))
    print('mbt len =', h2(sec[9]))
    print('tracks on device =', sec[14])
    print('words/phys rec =', h1(sec[15]))


def dump(fld: List[str]) -> None:
    "Dump a disk sector in octal and ASCII."
    if len(fld) > 2:
        print('bad command')
        return
    if len(fld) == 2:
        count = int(fld[1])
    else:
        count = 1
    for i in range(count):
        print('Sector', g.cur_sector)
        data = g.cache.get_sector(g.cur_sector)
        assert len(data) == WPS
        octal_dump(data)
        g.cur_sector += 1


def read_command():
    "Get next command. On EOF, retrun 'exit'."
    try:
        return input('cmd ->')
    except EOFError:
        return 'exit'


def print_help() -> None:
    print('g sector')
    print('ascii')
    print('fdata')
    print('d  sector-count')
    print('exit')


def params_okay(fld: List[str], n: int) -> bool:
    "True if len(fld) == n + 1. Print msg otherwise."
    if len(fld) == n + 1:
        return True
    else:
        print('bad command')
        return False


def print_octal_and_char(offset: int, b: List[int]) -> None:
    print(f'{offset:03}  ', end='')
    for i in range(4):
        print(f'{b[i]:012o} ', end='')
    print('  ', end='')
    if g.char_mode == 'a':
        print_ascii(b)
    elif g.char_mode == 'f':
        print_fdata(b)
    else:
        assert False


def print_ascii(b: List[int]):
    for i in range(4):
        n1 = b[i] >> 27
        n2 = (b[i] >> 18) & 0o777
        n3 = (b[i] >> 9) & 0o777
        n4 = b[i] & 0o777
        c1 = util.toprint(n1)
        c2 = util.toprint(n2)
        c3 = util.toprint(n3)
        c4 = util.toprint(n4)
        print(f'{c1}{c2}{c3}{c4}', end='')


def print_fdata(b: List[int]):
    for i in range(4):
        n1 = b[i] >> 30
        n2 = (b[i] >> 24) & 0o77
        n3 = (b[i] >> 18) & 0o77
        n4 = (b[i] >> 12) & 0o77
        n5 = (b[i] >> 6) & 0o77
        n6 = b[i] & 0o77
        c1 = fd[n1]
        c2 = fd[n2]
        c3 = fd[n3]
        c4 = fd[n4]
        c5 = fd[n5]
        c6 = fd[n6]
        print(f'{c1}{c2}{c3}{c4}{c5}{c6}', end='')


def octal_dump(buff: List[int]) -> None:
    n = 0
    buffsize = len(buff)
    while n < buffsize:
        print_octal_and_char(n, buff[n: n + 4])
        n += 4
        print('')


if __name__ == '__main__':
    main()
