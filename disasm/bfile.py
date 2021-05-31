
"Class for reading arbitrary bytes from a binary file."

from typing import List
# XXX: We assume little-endian format!
import struct


class Bfile:
    def __init__(self, fname):
        self.fd = open(fname, 'rb')
        self.offset = 0

    def close(self) -> None:
        self.fd.close()
        self.fd = None

    def seek(self, offset: int) -> None:
        # self.offset = offset
        self.fd.seek(offset)

    def read(self, count: int) -> bytes:
        "Return a byte string."
        return self.fd.read(count)

    def readfrom(self, count: int, offset: int) -> bytes:
        "Return a byte string from specified offset."
        self.seek(offset)
        return self.read(count)

    def readint(self, offset=None) -> int:
        "Return a 4-byte integer."
        if offset:
            self.seek(offset)
        buff = self.read(4)
        return struct.unpack('<I', buff)[0]

    def readlong(self, offset=None) -> int:
        "Return an 8-byte integer."
        if offset:
            self.seek(offset)
        buff = self.read(8)
        return struct.unpack('<Q', buff)[0]

    def readshort(self, offset=None) -> int:
        "Return a 2-byte integer."
        if offset:
            self.seek(offset)
        buff = self.read(2)
        return struct.unpack('<H', buff)[0]

    def readbyte(self, offset=None) -> int:
        "Return a 1-byte integer."
        if offset:
            self.seek(offset)
        buff = self.read(1)
        return ord(buff)

    def readRVA(self, offset=None) -> List[int]:
        "Special purpose. Remove?"
        va = self.readint(offset)
        size = self.readint()
        return [va, size]

    def readstring(self, offset=None) -> str:
        "Return a decoded null-terminated string."
        if offset:
            self.seek(offset)
        b = b''
        while True:
            c = self.read(1)
            if c == b'\00':
                break
            b += c
        return b.decode()


if __name__ == '__main__':
    f = Bfile('hello.o')
    elf_sig = f.read(4)
    ei_class = f.readbyte()
    ei_data = f.readbyte()
    ei_version = f.readbyte()
    ei_osabi = f.readbyte()
    ei_abiversion = f.readbyte()
    print('ELF sig:', elf_sig)
    print('class:', ei_class)
    if ei_class == 2:
        print('64-bit elf')
    print('data:', ei_data)
    if ei_data == 1:
        print('little-endian')
    print('version:', ei_version)
    if ei_version == 1:
        print('version ok')
    print('osabi:', ei_osabi)
    if ei_osabi == 0:
        print('system V')
    print('abiversion:', ei_abiversion)
