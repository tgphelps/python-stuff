
"""
Elf.py is a module for reading and decoding Intel x64 ELF files,
both executable and relocatable.
"""

from typing import Tuple, List

import struct
import sys
from Phent import Phent
from Shent import Shent

# Constants
HDR_SIZE = 64

EI_CLASS = 4
EI_DATA = 5
EI_VERSION = 6
EI_OSABI = 7
EI_ABIVERSION = 8


def is_elf64_file(fname: str) -> Tuple[bool, int]:
    """
    Determines whether fname is an ELF file or not.

    Returns (True, 0) if it is, and (False, <err>) if not.
    We verify that: the file is readable, it is at least HDR_SIZE bytes in
    length, and the interesting fields in e_ident are good.
    """
    try:
        with open(fname, 'rb') as f:
            hdr = f.read(HDR_SIZE)
            if len(hdr) != HDR_SIZE:
                return False, 2  # header read was short
            else:
                magic = hdr[0:4]
                if magic != b'\x7fELF':
                    return False, 3
                if hdr[EI_CLASS] != 2:
                    return False, 4
                if hdr[EI_DATA] != 1:
                    return False, 5
                if hdr[EI_VERSION] != 1:
                    return False, 6
                # The "3" below means "GNU"
                if hdr[EI_OSABI] not in (0, 3) or hdr[EI_ABIVERSION] != 0:
                    return False, 7
                return True, 0
    except IOError:
        return False, 1  # failed to read file


class Elf:
    """
    Elf is an object that represents an Intel x64 ELF file. Creating one
    will throw an exception if the file passed to __init__ isn't a proper ELF.
    """
    def __init__(self, fname: str):
        self.sht = b''
        self.pht = b''
        self.str_tbl = b''
        self.shent: List[Shent] = []
        self.phent: List[Phent] = []
        self.parse_complete = False
        self.elf = open(fname, 'rb')
        self.hdr = self.elf.read(HDR_SIZE)
        self.e_ident = self.hdr[0:16]
        assert len(self.hdr) == HDR_SIZE

        assert self.hdr[0:4] == b'\x7fELF'
        self.ei_class = self.hdr[EI_CLASS]
        self.ei_data = self.hdr[EI_DATA]
        self.ei_version = self.hdr[EI_VERSION]
        self.ei_osabi = self.hdr[EI_OSABI]
        self.ei_abiversion = self.hdr[EI_ABIVERSION]

        assert self.ei_class == 2
        assert self.ei_data == 1
        assert self.ei_version == 1
        assert self.ei_osabi in (0, 3)
        assert self.ei_abiversion == 0

        fields = self.hdr[16:]
        a, b, c, d, e, f, g, h, i, j, k, l, m = \
            struct.unpack('<HHIQQQIHHHHHH', fields)
        self.e_type = a
        self.e_machine = b
        self.e_version = c
        self.e_entry = d
        self.e_phoff = e
        self.e_shoff = f
        self.e_flags = g
        self.e_ehsize = h
        self.e_phentsize = i
        self.e_phnum = j
        self.e_shentsize = k
        self.e_shnum = l
        self.e_shstrndx = m

    def parse(self) -> None:
        " Read the pht, sht, and string table for future use."
        print("read sht")
        sht_size = self.e_shnum * self.e_shentsize
        assert sht_size > 0
        self.elf.seek(self.e_shoff, 0)
        self.sht = self.elf.read(sht_size)
        assert len(self.sht) == sht_size

        for n in range(self.e_shnum):
            self.shent.append(Shent(self.get_shent(n)))

        print("read pht")
        if self.e_phnum > 0:
            pht_size = self.e_phnum * self.e_phentsize
            self.elf.seek(self.e_phoff, 0)
            self.pht = self.elf.read(pht_size)
            assert len(self.pht) == pht_size
        else:
            print("NO PHT")

        for n in range(self.e_phnum):
            self.phent.append(Phent(self.get_phent(n)))

        self.read_string_table()
        self.parse_complete = True

        # Use the string table to get section names.
        for ent in self.shent:
            ent.name = self.get_string(ent.sh_name)

    def read_string_table(self) -> None:
        st = self.e_shstrndx
        sh = self.shent[st]
        self.elf.seek(sh.sh_offset)
        self.str_tbl = self.elf.read(sh.sh_size)
        assert len(self.str_tbl) == sh.sh_size

    def get_shent(self, n: int) -> bytes:
        size = self.e_shentsize
        offset = n * size
        return self.sht[offset: offset + size]

    def get_phent(self, n: int) -> bytes:
        size = self.e_phentsize
        offset = n * size
        return self.pht[offset: offset + size]

    def print_elf_hdr(self, out=sys.stdout) -> None:
        print(f"{self.ei_class=}")
        print(f"{self.ei_data=}")
        print(f"{self.ei_version=}")
        print(f"{self.ei_osabi=}")
        print(f"{self.ei_abiversion=}")
        print(f"{self.e_type=}")
        print(f"{self.e_machine=}")
        print(f"{self.e_version=}")
        print(f"{self.e_entry=:#010x}")
        print(f"{self.e_phoff=:#010x}")
        print(f"{self.e_shoff=:#010x}")
        print(f"{self.e_flags=:#06x}")
        print(f"{self.e_ehsize=}")
        print(f"{self.e_phentsize=}")
        print(f"{self.e_phnum=}")
        print(f"{self.e_shentsize=}")
        print(f"{self.e_shnum=}")
        print(f"{self.e_shstrndx=}")

    def get_string(self, n: int) -> str:
        "Return the string from the string table at index n."
        # print(f"sh_name = {n}")
        s = []
        while True:
            c = self.str_tbl[n]
            if c:
                s.append(chr(c))
                n += 1
            else:
                return ''.join(s)

    def close(self) -> None:
        self.elf.close()
        # self.elf = None (type error)


if __name__ == '__main__':
    good, reason = is_elf64_file('bad')
    print(f'status = {good}, reason = {reason}')
    good, reason = is_elf64_file('tests/hello')
    print(f'status = {good}, reason = {reason}')
