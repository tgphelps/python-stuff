
import gzip
import hashlib

# WARNING: This all assumes the hashed file is gzip-compressed.
BUF_SIZE = 65536


def hash_file(path: str) -> str:
    """Calculate the 40-char SHA1 checksum of the file."""
    sha1 = hashlib.sha1()

    with open(path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def hash_gzip_file(path: str) -> str:
    """Calculate the 40-char SHA1 checksum of the uncompressed file contents.

    That is, uncompress the file and return the SHA1 checksum of the contents.
    """
    sha1 = hashlib.sha1()

    with gzip.open(path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


# ------------------

def main() -> None:

    h = hash_file('hash.py')
    print(h, 'hash.py')


if __name__ == '__main__':
    main()
