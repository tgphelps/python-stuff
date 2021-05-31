#!/usr/bin/env python

"""
dumpsections.py: Hex dump all sections from an Elf64.

Usage:
    dumpsections.py [ -d ] ELF

Options:
    -h --help           Show this screen, and exit.
    -d --debug          Turn on debug mode
"""


import sys
import struct
import docopt  # type: ignore

from Elf64 import Elf64, Shent
from dumper import Hexdump


# Constants
VERSION = '0.01'
LINESIZE = 16

SHT_PROGBITS = 1
SHT_SYMTAB = 2
SHT_RELA = 4
SHT_REL = 9
SHT_NOBITS = 8

# Global variables


class Globals:
    debug: bool
    pass


g = Globals()
g.debug = False


def main() -> None:
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 8):
        print("Python 3.8 or above is required.")
        sys.exit(1)
    args = docopt.docopt(__doc__, version=VERSION)
    # print(f'args: {args}')
    if args['--debug']:
        g.debug = True

    elf = Elf64(args['ELF'])

    for n, s in enumerate(elf.shent):
        print('section:', n, s.name, s.sh_type)
        if s.sh_type == SHT_NOBITS:
            dump_nobits(elf, s)
        else:
            dump_section(elf, s)


def dump_section(elf: Elf64, s: Shent) -> None:
    print('section section', s.name)
    assert s.sh_type != SHT_REL
    buff = elf.b[s.sh_offset: s.sh_offset + s.sh_size]
    if len(buff) > 0:
        dump_buff(buff)
    else:
        print("size = 0")
    if s.sh_type == SHT_RELA:
        dump_rela_section(elf, s)
    elif s.sh_type == SHT_SYMTAB:
        dump_symtab_section(elf, s)
    print('')


def dump_nobits(elf: Elf64, s: Shent) -> None:
    print('nobits section', s.name)
    print('size =', s.sh_size)
    print('')


def dump_rela_section(elf: Elf64, s: Shent) -> None:
    print('dump RELA section')
    print('sh_link =', s.sh_link)
    print('sh_info =', s.sh_info)
    print('sh_entsize =', s.sh_entsize)
    num_rels = s.sh_size // s.sh_entsize
    offset = s.sh_offset
    print('count =', num_rels)
    for i in range(num_rels):
        r_offset, r_sym, r_type, r_add = \
                struct.unpack('<QIIq', elf.b[offset: offset + s.sh_entsize])
        print(
          f'offs: {r_offset}, r_sym: {r_sym}, r_typ: {r_type} r_add: {r_add}')
        offset += s.sh_entsize


def dump_symtab_section(elf: Elf64, s: Shent) -> None:
    print('dump SYMTAB section')
    print('sh_link =', s.sh_link)
    print('sh_info =', s.sh_info)
    print('sh_entsize =', s.sh_entsize)


def dump_buff(buff: bytes) -> None:
    dumper = Hexdump()
    offset = 0
    size = len(buff)
    print('size =', size)
    while size:
        this = min(size, LINESIZE)
        print(dumper.dump(buff[offset: offset+this]))
        offset += this
        size -= this
        assert size >= 0


if __name__ == '__main__':
    main()
