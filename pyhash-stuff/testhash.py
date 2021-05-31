#!/usr/bin/env python

"""
testhash.py: test blocksizes for deduplication effect

Usage:
    testhash.py -b SIZES FILE

Options:
    -h --help             Show this screen, and exit.
    -b --blocksize=sizes  Test hashing with this list of block sizes
"""

import sys
import docopt

import util

VERSION = 0.01

def main():
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 8):
        util.fatal("Python 3.8 or above is required.")
    args = docopt.docopt(__doc__, version=VERSION)
    # print(args)
    fname = args['FILE']
    sizes = args['--blocksize'].split(',')
    sizes = [n for n in map(int, sizes)]
    print(f'file = {fname}')
    print(f'block sizes = {sizes}')

    for n in sizes:
        hash_file_with_size(fname, n)


def hash_file_with_size(fname, n):
    bsize = pow(2, n)
    print(f'Hashing file {fname} with block size {bsize}')
    blocks = 0
    uniq_hashes = 0
    hashes = {}
    with open(fname, 'rb') as f:
        while True:
            buff = f.read(bsize)
            if len(buff) == 0:
                break
            h = util.hash_block(buff)
            if h not in hashes:
                hashes[h] = 0
                uniq_hashes += 1
            hashes[h] += 1
            blocks += 1
    dedup_megs = int(uniq_hashes * bsize / 1048576)
    print(f'Block size = {bsize}')
    print(f'Block count = {blocks}')
    print(f'Unique blocks = {uniq_hashes}')
    print(f'Dedup size = {dedup_megs}M')
    # for h in hashes:
        # print(h)

if __name__ == '__main__':
    main()
