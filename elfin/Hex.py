
import sys


STD_WIDTH = 16


def _toprint(c: int) -> int:
    "Return printable version of a character."
    if 0x20 <= c < 0x7f:
        return c
    else:
        return ord('.')


class Dumper:
    """
    Class for dumping data in the time-honored hex-and-ascii format.
    The offset is mandatory. The ASCII is optional.
    """
    def __init__(self, width=STD_WIDTH, offset=0, hexonly=False):
        self.width = width
        self.offset = offset
        self.hexonly = hexonly

    def dump(self, b: bytes) -> str:
        "Return printable string representing 'bytes' object b."
        size = len(b)
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
            asc = [chr(_toprint(c)) for c in b]
            return addr + hex + '  ' + ''.join(asc)


def dump(buff: bytes, size=0, out=sys.stdout) -> None:
    "Print one buffer of any size, in lines of LINESIZE bytes"
    offset = 0
    if size == 0:
        size = len(buff)
    dumper = Dumper()
    while size:
        this = min(size, 16)
        print(dumper.dump(buff[offset: offset+this]), file=out)
        offset += this
        size -= this
        assert size >= 0


def _print_ascii(buff: bytes, out=sys.stdout) -> None:
    "Print the bytes, using printable characters only."
    printables = [chr(_toprint(c)) for c in buff]
    print(''.join(printables), file=out)


def dump_ascii(buff: bytes, width=64, out=sys.stdout) -> None:
    "Print bytes of any length, using printable chars only."
    chars_left = len(buff)
    offset = 0
    while chars_left:
        this_time = min(chars_left, width)
        print(f'{offset:08x}  ', end='', file=out)
        _print_ascii(buff[offset:offset + this_time], out)
        offset += this_time
        chars_left -= this_time
        assert chars_left >= 0


# --------------------

if __name__ == '__main__':
    dumper = Dumper(offset=0)
    b = b'0\x13234\x1f67\x3e\x3f\x7f9ac'

    print(dumper.dump(b))
    print('00000000  30 13 32 33 34 1f 36 37 3e 3f 7f 39 61 62 63 64  \
0.234.67>?.9abcd')

    dumper = Dumper(offset=16, hexonly=True)
    print(dumper.dump(b))
