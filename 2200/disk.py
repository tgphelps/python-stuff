
"""
Class to model a 2200 disk, and provide methods to read it.
"""


from typing import Tuple, List

import util

WORDS_PER_SECTOR = 112
BYTES_PER_SECTOR = 512
USED_BYTES = WORDS_PER_SECTOR * 9 / 2


class Disk:
    def __init__(self, dname: str, debug=False):
        self.debug = debug
        self.fd = open(dname, 'rb')
        self.fd.seek(0, 2)
        self.byte_size = self.fd.tell()

    def close(self) -> None:
        self.fd.close()

    def read_sector(self, sector: int) -> List[int]:
        seek_to = sector * BYTES_PER_SECTOR
        if self.debug:
            print('seek to:', seek_to)
        self.fd.seek(seek_to)
        data = self.fd.read(BYTES_PER_SECTOR)
        sect: List[int] = []
        n = 0
        while n < USED_BYTES:
            # print('n =', n)
            b9 = data[n: n + 9]
            w1, w2 = unpack_2_words(b9)
            sect.append(w1)
            sect.append(w2)
            n += 9
        assert len(sect) == 112
        return sect


def unpack_2_words(b: bytes) -> Tuple[int, int]:
    if len(b) != 9:
        print('len(b)', len(b))
    assert len(b) == 9
    word0 = (b[0] << 24) + (b[1] << 16) + (b[2] << 8) + b[3]
    word0 = (word0 << 4) + (b[4] >> 4)
    word1 = ((b[4] & 0x0f) << 32) + (b[5] << 24) + (b[6] << 16) + \
            (b[7] << 8) + b[8]
    return word0, word1


DISK = 'data/vd_DS0.bin'


def main() -> None:
    d = Disk(DISK)
    print('disk size is', d.byte_size)
    buff = d.read_sector(2)
    d.close()

    print('sector 2')
    # print(buff)
    # v = buff[0:9]
    # assert len(v) == 9
    # print(v)
    # word0 = (v[0] << 24) + (v[1] << 16) + (v[2] << 8) + v[3]
    # word0 = (word0 << 4) + (v[4] >>4)
    # word0, word1 = unpack_2_words(v)
    w0 = buff[0]
    # w1 = buff[1]
    n1 = (w0 >> 27) & 0o777
    n2 = (w0 >> 18) & 0o777
    n3 = (w0 >> 9) & 0o777
    n4 = w0 & 0o777
    c1 = util.qw_to_ascii(n1)
    c2 = util.qw_to_ascii(n2)
    c3 = util.qw_to_ascii(n3)
    c4 = util.qw_to_ascii(n4)
    print('chars:', c1, c2, c3, c4)


if __name__ == '__main__':
    main()
