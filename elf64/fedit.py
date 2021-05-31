#!/usr/bin/env python

"""
fedit.py: Interactively edit a binary file

Usage:
    fedit.py [ -d ] [ -r ] FILE VA-FIRST OFFSET

Options:
    -h --help           Show this screen, and exit.
    -d --debug          Turn on debug mode
    -r --readonly       Prevent attempts to change file.
"""


# TODO:
# 1. If the file is changed, delete the in-RAM copy, that is now wrong.
# 2. Enable searching files larger than MAX_READ.

import sys
import docopt  # type: ignore

from dumper import Hexdump


# Constants
VERSION = '0.01'
MAX_READ = 3 * 1024 * 1024  # sanity check


# Global variables

class Globals:
    debug: bool
    va_first: int
    offset: int
    readonly: bool
    file_size: int
    entire_file: bytes
    pass


g = Globals()
g.debug = False
g.va_first = 0
g.offset = 0
g.readonly = False
# g.dumper = None
g.file_size = 0
g.entire_file = b''
g.debug = False


def main():
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 8):
        print("Python 3.8 or above is required.")
        sys.exit(1)
    args = docopt.docopt(__doc__, version=VERSION)
    # print(f'args: {args}')
    if args['--debug']:
        g.debug = True
    if args['--readonly']:
        g.readonly = True
        print('READ-ONLY mode')

    g.va_first = to_num(args['VA-FIRST'])
    g.offset = to_num(args['OFFSET'])

    # g.dumper = Hexdump(offset=g.va_first)
    with open(args['FILE'], 'rb+') as f:
        g.file_size = file_size(f)
        print('file size =', g.file_size)
        process(f)


def process(f):
    test_code(g.va_first)
    while True:
        cmd = read_command()
        fld = cmd.split()
        if len(fld) == 0:
            continue
        print(fld)
        if fld[0] == 'exit':  # exit
            break
        elif fld[0] == 'd':  # dump
            dump(fld, f)
        elif fld[0] == 'cb':  # change bytes
            if not g.readonly:
                change_bytes(fld, f)
            else:
                print('File is read-only.')
        elif fld[0] in ('s', 'sa'):  # search, search all
            search(fld, f)
        elif fld[0] == 'p':  # print last command
            # print(last_cmd)
            pass
        elif fld[0] == 'help':  # print help msg
            print_help()
        elif fld[0] == 'debug':  # debug on/off
            if fld[1] == 'on':
                g.debug = True
            else:
                g.debug = False
            print(f'debug = {g.debug}')
        else:
            print('bad command')
        # last_cmd = cmd


def dump(fld, f):
    if len(fld) != 3:
        print('bad command:', fld)
    else:
        offset = to_num(fld[1])
        dumper = Hexdump(offset=offset)
        count = to_num(fld[2])
        seek_to = to_raw(offset)
        if seek_to < 0:
            print('invalid va given')
            return
        f.seek(seek_to)
        while count > 0:
            next = min(count, 16)
            b = f.read(next)
            print(dumper.dump(b))
            count -= next
            assert count >= 0


def change_bytes(fld, f):
    va = to_num(fld[1])
    offset = to_raw(va)
    if offset >= g.file_size:
        print('cannot change file size')
        return
    data = read_bytes(fld[2:])
    if len(data) == 0:
        print('invalid byte given')
        return
    print(f'offset {offset:0x}: data: {data}')

    invalidate_cache()
    f.seek(offset)
    for b in data:
        f.write(bytes([b]))
    f.flush()


def search(fld, f):
    "s offset b b b ..."
    if fld[0] == 'sa':
        s_all = True
    else:
        s_all = False

    va = to_num(fld[1])
    offset = to_raw(va)
    if g.debug:
        print(f'start: va = {va:#0x} offset = {offset:#0x}')
    if g.file_size > MAX_READ:
        print('file is too big to search.')
        return
    data = read_bytes(fld[2:])
    if len(data) == 0:
        print('invalid byte given')
        return
    if g.entire_file == b'':
        f.seek(0)
        g.entire_file = f.read(MAX_READ)
    print('searching for:', bytes(data))
    while True:
        if g.debug:
            print(f'start at va {to_va(offset):#0x}  offset {offset:#0x}')
        match = g.entire_file.find(bytes(data), offset)
        if match != -1:
            print(f'found at VA {to_va(match):#0x}')
            if not s_all:
                break
            if g.debug:
                print(f'match = {match:#0x}')
                print('len(data)', len(data))
            offset = match + len(data)
            if offset >= g.file_size:
                break
            # and try again...
        else:
            break


def read_bytes(bs):
    "convert a list of strings into a list of bytes."
    data = []
    for b in bs:
        # d = int(b, 16)
        data.append(int(b, 16))
    return data


def read_command():
    "Get next command. On EOF, retrun 'exit'."
    try:
        return input('cmd ->')
    except EOFError:
        return 'exit'


def test_code(va):
    assert to_va(to_raw(va)) == va


def to_raw(va):
    "Convert a file address to a virtual address."
    return va - g.va_first + g.offset


def to_va(raw):
    "Convert a virtual address to a file address."
    return raw + g.va_first - g.offset


def file_size(f):
    f.seek(0, 2)
    return f.tell()


def to_num(s):
    "If s starts with 0, it's hex, otherwise it's decimal."
    if s.startswith('0'):
        return int(s, 16)
    else:
        return int(s)


def invalidate_cache():
    g.entire_file = b''


def print_help():
    print('d  va  count')
    print('cb va  hex-byte ...')
    print('s  va  hex-byte ...')
    print('sa va  hex-byte ...')
    print('exit')


if __name__ == '__main__':
    main()
