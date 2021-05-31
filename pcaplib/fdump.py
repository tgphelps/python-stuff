
# *** IMPORTS ***

import argparse
from typing import BinaryIO

from dumper import Hexdump


# *** CONSTANTS ***

BUFFSIZE = 1024
LINESIZE = 16
A_BILLION = 1024 * 1024 * 1024


# *** GLOBAL VARIABLES ***

class Globals:
    path: str
    offset: int
    length: int


g = Globals()


# *** FUNCTIONS ***

def parse_arguments() -> None:
    "Parse arguments, and store in global vars."
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='file to dump')
    parser.add_argument('--verbose', '-v', help='increase verbosity',
                        action='store_true')
    parser.add_argument('--offset', '-o', type=int, default=0,
                        help='start at file offset')
    parser.add_argument('--length', '-l', type=int, default=A_BILLION,
                        help='bytes to dump')
    args = parser.parse_args()

    g.path = args.path
    g.offset = args.offset
    g.length = args.length

    if args.verbose:
        print('path =', g.path)
        print('offset =', g.offset)
        print('length =', g.length)


def print_buff(buff: bytes, size: int, dump: Hexdump) -> None:
    "Print one buffer of the file, in lines of LINESIZE bytes."
    offset = 0
    while size:
        this = min(size, LINESIZE)
        print(dump.dump(buff[offset:offset+this]))
        offset += this
        size -= this
        assert size >= 0


def dump_file(f: BinaryIO) -> None:
    "Dump the file starting at 'offset' for a length of 'length' bytes."
    buff = bytes()
    dump = Hexdump(offset=g.offset)
    assert g.offset >= 0
    assert g.length >= 0
    if g.offset > 0:
        f.seek(g.offset, 0)
    while g.length > 0:
        buff = f.read(BUFFSIZE)
        size = min(len(buff), g.length)
        if len(buff) > 0:
            print_buff(buff, size, dump)
            g.length -= size
        else:
            break


def process_file(path: str) -> None:
    "Dump contents of the file."
    try:
        f = open(path, 'rb')
    except IOError:
        # We don't note the exact reason for the open failure
        print('Error opening file', path)
        return
    try:
        dump_file(f)
    finally:
        f.close()


def main():
    parse_arguments()
    # parse_arguments() will not return if there is an error
    process_file(g.path)


if __name__ == '__main__':
    main()
