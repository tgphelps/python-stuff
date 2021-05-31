
import platform
import sys
import os
# from os.path import join, getsize


def main() -> None:
    # It's legal to write paths with either '/' or '\' as the separator.
    # os.walk() uses only the '\', so make sure the start path uses them, too.

    if platform.system() == 'Windows':
        topdir = sys.argv[1].replace('/', '\\')
    else:
        topdir = sys.argv[1]
    for root, _, files in os.walk(topdir):
        for f in files:
            print(os.path.join(root, f))


if __name__ == '__main__':
    main()
