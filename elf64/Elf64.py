
"""
Elf64.py reads and parses a System V little-endian elf64 file.

It returns an Elf64 instance that contains all the interesting things
from the elf. As a sanity check, it will not process a file greater
than MAX_ELF_SIXE in size.
"""

from typing import Tuple, List

import os
import struct
import sys

# Constants
MAX_ELF_SIZE = 10_000_000
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
                    # Not an elf64
                    return False, 4
                if hdr[EI_DATA] != 1:
                    # Not little-endian
                    return False, 5
                if hdr[EI_VERSION] != 1:
                    # Unknow version
                    return False, 6
                # The "3" below means "GNU"
                if hdr[EI_OSABI] not in (0, 3) or hdr[EI_ABIVERSION] != 0:
                    # Not a System V elf
                    return False, 7
                return True, 0
    except IOError:
        return False, 1  # failed to read file


class Elf64:
    """
    An Elf64 is an object that represents an Intel x64 ELF file. Creating one
    will throw an exception if the file passed to __init__ isn't a proper ELF.
    """
    def __init__(self, fname: str, debug=False):
        self.debug = debug
        self.b = b''    # will hold entire file contents
        self.sht = b''  # will hold the SHT
        self.pht = b''  # will hold the PHT
        self.str_tbl = b''
        self.shent: List[Shent] = []
        self.phent: List[Phent] = []
        self.parse_complete = False
        ok, reason = is_elf64_file(fname)
        assert ok

        self.read_entire_file(fname)    # self.b == file data
        self.hdr = self.b[0:HDR_SIZE]
        self.e_ident = self.hdr[0:16]
        assert len(self.hdr) == HDR_SIZE

        assert self.hdr[0:4] == b'\x7fELF'
        self.ei_class = self.hdr[EI_CLASS]
        self.ei_data = self.hdr[EI_DATA]
        self.ei_version = self.hdr[EI_VERSION]
        self.ei_osabi = self.hdr[EI_OSABI]
        self.ei_abiversion = self.hdr[EI_ABIVERSION]

        # All these should pass if we should proceed
        assert self.ei_class == 2       # 2 => 64-bit ELF
        assert self.ei_data == 1        # 1 => little-endian
        assert self.ei_version == 1
        assert self.ei_osabi == 0       # System V
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

        self.parse()

    def read_entire_file(self, fname):
        s = os.stat(fname)
        assert s.st_size <= MAX_ELF_SIZE
        fp = open(fname, 'rb')
        self.b = fp.read()
        if self.debug:
            print('Elf size:', len(self.b))

    def parse(self) -> None:
        " Read the pht, sht, and string table for future use."
        sht_size = self.e_shnum * self.e_shentsize
        assert sht_size > 0
        self.sht = self.get_byte_range(self.e_shoff, sht_size)
        assert len(self.sht) == sht_size

        for n in range(self.e_shnum):
            self.shent.append(Shent(self.get_shent(n)))

        if self.e_phnum > 0:
            pht_size = self.e_phnum * self.e_phentsize
            # self.elf.seek(self.e_phoff, 0)
            # elf.pht = self.elf.read(pht_size)
            self.pht = self.get_byte_range(self.e_phoff, pht_size)
            assert len(self.pht) == pht_size
            for n in range(self.e_phnum):
                self.phent.append(Phent(self.get_phent(n)))
        # else:
            # relocatable ELFs have no PHT
            # print("NO PHT")

        self.read_string_table()
        self.parse_complete = True

        # Use the string table to get section names.
        for ent in self.shent:
            ent.name = self.get_string(ent.sh_name)

    def get_byte_range(self, start, count):
        return self.b[start: start + count]

    def read_string_table(self) -> None:
        st = self.e_shstrndx
        sh = self.shent[st]
        # self.elf.seek(sh.sh_offset)
        # self.str_tbl = self.elf.read(sh.sh_size)
        self.str_tbl = self.b[sh.sh_offset: sh.sh_offset + sh.sh_size]
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


# ------------------

class Phent:
    "Program header table entry"
    def __init__(self, ent: bytes):
        a, b, c, d, e, f, g, h = \
            struct.unpack("<IIQQQQQQ", ent)
        self.data = ent
        self.p_type = a
        self.p_flags = b
        self.p_offset = c
        self.p_vaddr = d
        _ = e
        self.p_filesz = f
        self.p_memsz = g
        self.p_align = h

    def __str__(self):
        return f"type={self.p_type:#0x} flags={self.p_flags:#010x} " \
               f"off={self.p_offset:#010x} vaddr={self.p_vaddr:#010x} " \
               f"memsz={self.p_memsz:#010x}"

# ----------------


class Shent:
    "Section header table entry"
    def __init__(self, ent: bytes):
        self.name: str
        a, b, c, d, e, f, g, h, i, j = \
            struct.unpack('<IIQQQQIIQQ', ent)
        self.data = ent
        self.sh_name = a
        self.sh_type = b
        self.sh_flags = c
        self.sh_addr = d
        self.sh_offset = e
        self.sh_size = f
        self.sh_link = g
        self.sh_info = h
        self.sh_addralign = i
        self.sh_entsize = j

    def __str__(self):
        return f"name={self.name} type={self.sh_type:#0x} " \
               f"size={self.sh_size} flags={self.sh_flags:#010x} " \
               f'offset={self.sh_offset} addr={self.sh_addr} ' \
               f'info={self.sh_info} ent={self.sh_entsize}'

# ----------


def main() -> None:
    assert len(sys.argv) == 2
    fname = sys.argv[1]

    good, reason = is_elf64_file(fname)
    print(f'status = {good}, reason = {reason}')

    elf = Elf64(fname, True)
    elf.print_elf_hdr()
    print('Sections:')
    for n, s in enumerate(elf.shent):
        print(n, s)
    print('Segments:')
    for n, p in enumerate(elf.phent):
        print(n, p)


if __name__ == '__main__':
    main()
