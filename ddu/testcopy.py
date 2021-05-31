
"""File copy test program.

   Find out what happens with various corner cases when you try to
   copy a file to a destination.
"""

import os
import shutil
import sys

def main() -> None:
    if len(sys.argv) != 3:
        fatal('usage: testcopy.py src dir')
    src = sys.argv[1]
    dest = sys.argv[2]
    if not os.path.isdir(dest):
        fatal(f'{dest} is not a directory')
    if not os.path.isfile(src):
        fatal(f'{src} is not a file')
    dest_file = os.path.join(dest, src)
    if os.path.exists(dest_file):
        fatal(f'already exists: {dest_file}')
    copy_file(src, dest_file)

def copy_file(src: str, dest_file : str) -> None:
    """Copy file 'src' to file 'dest_file'.

    Assuming permissions are okay, copying the file should fail only if
    not all the intermediate directories are there. If that happend, we
    will make all those directories, and retry it.
    """
    print(f'copy: {src} -> {dest_file}')
    try:
        shutil.copyfile(src, dest_file)
    except FileNotFoundError:
        print('need directories...')
        dest_dir = os.path.dirname(dest_file)
        print('make dir:', dest_dir)
        os.makedirs(dest_dir)
        shutil.copyfile(src, dest_file)

def fatal(msg):
    print('error:', msg, file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    main()
