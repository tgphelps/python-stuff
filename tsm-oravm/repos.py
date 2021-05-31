#!/bin/env python3

"""Handle OVM repository mounting.
   usage: repos.py [-h] [--mount MOUNT] [--umount UMOUNT] [--list] [--all]

   optional arguments:
     -h, --help            show this help message and exit
     --mount MOUNT, -m MOUNT
                           mount a repository
     --umount UMOUNT, -u UMOUNT
                           unmount a repository
     --list, -l            list mounted repository
     --all, -a             process all known repositories

   Exit status: 0 if okay, else 1.
"""


import argparse
import sys

import config
import util


class globals:
    pass

g = globals()

g.repos = None
g.option = None
g.okay = 0
g.status = 0


def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mount', '-m', help='mount a repository')
    parser.add_argument('--umount', '-u', help='unmount a repository')
    parser.add_argument('--list', '-l', action='store_true',
                        help='list mounted repository')
    parser.add_argument('--all', '-a', action='store_true',
                        help='process all known repositories')

    args = parser.parse_args()
    if args.list:
        g.option = 'l'
    if args.all:
        g.option = 'a'
    if args.mount:
        g.option = 'm'
        g.repos = args.mount
    if args.umount:
        g.option = 'u'
        g.repos = args.umount
    if not g.option:
        parser.print_help()
        sys.exit(2)



# r = repository object
# func = 'mount' or 'umount'

def do_repos(r, func):
    """Mount or unmount a repository.

       r = repository object
       func = 'm' or 'u'
    """
    assert func in ('m', 'u')
    if func == 'm':
        cmd = './mount.sh {} {} {}'.format(r.server, r.share, r.mount)
        g.status = util.run_shell_command(cmd)
    if func == 'u':
        g.status = util.run_shell_command('./umount.sh {}'.format(r.mount))


def do_cmd(func):
    if func == 'a':
        for r in config.cfg_repos_list:
            do_repos(r, 'm')
    elif func == 'l':
        x = util.run_shell_command("mount|grep /OVS/")
    else:
        raise


def main():
    config.read_config()

    parse_commandline()

    if g.option in ('a', 'l'):
        do_cmd(g.option)
    else:
        okay = 0
        for r in config.cfg_repos_list:
            if r.name == g.repos:
                do_repos(r, g.option)
                okay = 1
                break
        # XXX I think I just need a for...else here.
        if not okay:
            print('error: respository "{}" not found'.format(g.repos))
            sys.exit(1)

    sys.exit(g.status)


if __name__ == '__main__':
    main()
