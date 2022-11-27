#!/usr/bin/env python3

"""Create differential backup of a disk image, using full-backup digest."""

import argparse
import gzip
import hashlib



VERSION = 1

class Globals:
    pass

g = Globals()
g.disk_image = None
g.digest = None
g.backup_file = None
g.dry_run = False
dry_run = False
g.block_size = 0
g.blocks_equal = 0
g.block_num = None
g.blocks_diff = 0



def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('disk_img')
    parser.add_argument('digest')
    parser.add_argument('backup_file')
    parser.add_argument('--dry_run', '-d', action='store_true')
    args = parser.parse_args()
    g.disk_image = args.disk_img
    g.digest = args.digest
    g.backup_file = args.backup_file
    if args.dry_run:
        g.dry_run = True



def do_digest_header(f):
    s = f.readline().split()
    assert s[0] == 'H1'
    assert s[1] == str(VERSION)

    s = f.readline().split()
    assert s[0] == 'HF'

    s = f.readline().split()
    assert s[0] == 'HH'
    assert s[1] == 'SHA1'

    s = f.readline().split()
    assert s[0] == 'HB'
    g.block_size = int(s[1])
    assert 4096 <= g.block_size <= 4096*1024
    # print('block size =', g.block_size)

    s = f.readline().split()
    assert s[0] == 'HE'



def write_control(f, rec_type, detail):
    length = len(detail)
    # s = '%s%03d%s\n'%(rec_type, length, detail)
    s = '{}{03}{}\n'.format(rec_type, length, detail)
    # print(s, end='')
    f.write(s.encode())



def write_backup_header(f):
    if not g.dry_run:
        write_control(f, 'H1', str(VERSION))
        write_control(f, 'HF', g.disk_image)
        write_control(f, 'HB', str(g.block_size))
        write_control(f, 'HE', '')



def write_backup_trailer(f):
    if not g.dry_run:
        write_control(f, 'T1', '')
        write_control(f, 'TC', str(g.block_num + 1))
        write_control(f, 'TE', '')



def write_backup_block(f, block_num, hash, data):
    chunk = gzip.compress(data)
    size = len(chunk)
    write_control(f, 'B1', str(block_num))
    write_control(f, 'BH', hash)
    write_control(f, 'BS', str(size))
    write_control(f, 'BE', '')
    # Write the compressed block
    f.write(chunk)



def do_diff_backup(fdigest, fdisk):
    with open(g.backup_file, 'wb') as bkup:
        g.block_num = -1
        write_backup_header(bkup)
        while 1:
            s = fdigest.readline().split()
            assert s[0][0] == 'B'
            if s[0] == 'BE':
                # No more entries in the digest. We better be at the EOF
                # in the file we're comparing to it. Make sure we are.
                data = fdisk.read(g.block_size)
                assert len(data) == 0
                break
            orig_block = s[1]
            orig_hash = s[2]
            g.block_num += 1
            assert g.block_num == int(orig_block)

            data = fdisk.read(g.block_size)
            assert len(data) != 0

            h = hashlib.new('SHA1')
            h.update(data)
            hash = h.hexdigest()

            if hash == orig_hash:
                # print('Block', g.block_num, file=bkup)
                g.blocks_equal += 1
            else:
                # This block is different. Write it to the backup file.
                if not g.dry_run:
                    write_backup_block(bkup, g.block_num, hash, data)
                    print('Block', g.block_num, 'DIFFERENT')
                g.blocks_diff += 1
        write_backup_trailer(bkup)



def do_digest_trailer(fdigest):
    s = fdigest.readline().split()
    assert s[0] == 'T1'
    s = fdigest.readline().split()
    assert s[0] == 'TH'
    s = fdigest.readline().split()
    assert s[0] == 'TS'
    s = fdigest.readline().split()
    assert s[0] == 'TE'



def main():
    parse_arguments()
    with open(g.digest, 'rt') as fdigest:
        with open(g.disk_image, 'rb') as fdisk:
            do_digest_header(fdigest)
            do_diff_backup(fdigest, fdisk)
            do_digest_trailer(fdigest)
    print('Blocks equal', g.blocks_equal)
    print('Blocks diff ', g.blocks_diff)
    print('% different =', g.blocks_diff * 100.0 / (g.block_num + 1))


if __name__ == '__main__':
    main()
