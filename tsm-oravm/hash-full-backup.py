#!/usr/bin/env python3

"""Read a gzipped disk image, and create a file of its block SHA1 sums."""

import argparse
import gzip
import hashlib

# 72e9a8f8e994600f77ea8cd0ab0a48ce724e9325  unzipped



VERSION = 1

class Globals:
    pass

g = Globals()
g.disk_img = None
g.digest = None
g.block_size = None


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('disk_img')
    parser.add_argument('digest')
    parser.add_argument('--block_size', '-b', type=int, default=20)
    args = parser.parse_args()
    g.disk_img = args.disk_img
    g.digest = args.digest
    assert 12 <= args.block_size <= 22
    g.block_size = pow(2, args.block_size)
    print('block size =', g.block_size)


def write_header(out):
    print('H1', VERSION, file=out)
    print('HF', g.disk_img, file=out)
    print('HH', 'SHA1', file=out)
    print('HB', g.block_size, file=out)
    print('HE', file=out)

def write_trailer(out, hash, size):
    print('T1', file=out)
    print('TH', hash, file=out)
    print('TS', size, file=out)
    print('TE', file=out)

def main():
    parse_arguments()
    bytes_read = 0
    short_blocks = 0
    # Because the first one will be block 0
    block = -1
    h = hashlib.new('sha1')
    with gzip.open(g.disk_img, 'rb') as f:
        with open(g.digest, 'wt') as out:
            write_header(out)
            while 1:
                data = f.read(g.block_size)
                blen = len(data)
                if blen == 0: break
                if blen < g.block_size:
                    short_blocks += 1
                block += 1
                h.update(data)
                bh = hashlib.new('sha1')
                bh.update(data)
                print('B {} {}'.format(block, bh.hexdigest()),file=out)
                bytes_read += len(data)
            print('BE', file=out)
            assert short_blocks <= 1
            write_trailer(out, h.hexdigest(), bytes_read)

if __name__ == '__main__':
    main()

