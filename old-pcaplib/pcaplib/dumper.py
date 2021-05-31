#!/usr/bin/env python3


def toprint(c: int) -> int:
    "Return printable version of a character."
    if 0x20 <= c < 0x7f:
        return c
    else:
        return ord('.')


class Hexdump:
    """
    Class for dumping data in the time-honored hex-and-ascii format.
    The offset is mandatory. The ASCII is optional.
    """
    def __init__(self, width=16, offset=0, hexonly=False):
        # offset can be None, too
        self.width = width
        self.offset = offset
        self.hexonly = hexonly
        if offset is None:
            self.no_offset = True
        else:
            self.no_offset = False

    def dump(self, b: bytes) -> str:
        "Return printable string representing 'bytes' object b."
        size = len(b)
        if self.no_offset:
            addr = ''
        else:
            addr = '%08x  ' % (self.offset)
            self.offset += size
        bh = [('%02x' % (x,)) for x in b]
        hex = ' '.join(bh)
        if self.hexonly:
            return addr + hex
        else:
            if size < self.width:
                pad = (self.width - size)
                hex += pad * '   '
            asc = [chr(toprint(c)) for c in b]
            return addr + hex + '  ' + ''.join(asc)


def dump_bytes(buff: bytes, size: int):
    "Print one buffer of the file, in lines of LINESIZE bytes"
    offset = 0
    dumper = Hexdump()
    while size:
        this = min(size, 16)
        print(dumper.dump(buff[offset: offset+this]))
        offset += this
        size -= this
        assert size >= 0


def print_ascii(buff: bytes) -> None:
    "Print the bytes, using printable characters only."
    printables = [chr(toprint(c)) for c in buff]
    print(''.join(printables))


def dump_ascii(buff: bytes, width=64):
    "Print bytes of any length, using printable chars only."
    chars_left = len(buff)
    offset = 0
    while chars_left:
        this_time = min(chars_left, width)
        print(f'{offset:08x}  ', end='')
        print_ascii(buff[offset:offset + this_time])
        offset += this_time
        chars_left -= this_time
        assert chars_left >= 0


# --------------------

if __name__ == '__main__':
    dumper = Hexdump(offset=0)
    b = b'0\x13234\x1f67\x3e\x3f\x7f9ac'

    print(dumper.dump(b))
    print('00000000  30 13 32 33 34 1f 36 37 3e 3f 7f 39 61 62 63 64  \
0.234.67>?.9abcd')

    dumper = Hexdump(offset=16, hexonly=True)
    print(dumper.dump(b))
