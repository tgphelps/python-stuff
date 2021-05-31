
import hashlib
import sys

# Benchmarking shows that 256K I/O's is good as any
_IO_SIZE = 256 * 1024

def fatal(s):
    print(s, file=sys.stderr)


def hash_block(b):
    assert len(b) > 0
    m = hashlib.sha256()
    m.update(b)
    return m.hexdigest()


def hash_file(f):
    "Returns a sha256 hash, or emtpy string if file is empty."
    m = hashlib.sha256()
    have_data = False
    while True:
        buff = f.read(_IO_SIZE)
        bytes_read = len(buff)
        # print(f'read {bytes_read} bytes')
        if bytes_read == 0:
            break
        m.update(buff)
        have_data = True
        # bytes_left -= bytes_read
    if have_data:
        return m.hexdigest()
    else:
        return b''


if __name__ == '__main__':
    "Test hashing."
    fname = sys.argv[1]
    with open(fname, 'rb') as f:
        print(hash_file(f))
