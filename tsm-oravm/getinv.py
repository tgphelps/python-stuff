#!/bin/env python3

"""Fetch inventory information from an Oracle VM repository.

   usage: getinv.py -r repos
          getinv.py -a

   We read all the vm.cfg files from the repository, and write the
   information into the './inventory' directory. This directory will
   contain one file called 'DISKS', which list all virtual disks and
   their owners, and one directory for each VM in the repository,
   named by the VM name. Each VM directory contains 3 files:
      vm.cfg - copied from the repository
      name - contains the VM uuid
      disks - contains the names of the virtual disks in the VM

   Exit status: 0 if okay, else 1
"""

import argparse
import os
import sys

import config
import util

# ----------

class globals:
    pass

g = globals()

g.repos = None
g.option = None
g.status = 0

# ----------



def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repos', '-r')
    parser.add_argument('--all', '-a')

    args = parser.parse_args()
    if args.repos:
        g.option = 'r'
        g.repos = args.repos
    if args.all:
        g.option = 'a'

    if not g.option:
        parser.print_help()
        sys.exit(1)


# r = repository object
# Mount the repository, and find all vm.cfg files.
# For each vm.cfg file:
#    Get vm name
#    Create directory under $INV, named <vm-name>
#    Copy vm.cfg file to the $INV directory.
#    Create file 'name' containing the uuid.
#    Create file 'disks' in $INV directory, containing one disk name per line.

def get_inventory(r):
    """Get inventory information from repository 'r.name'

       First, run repos.py to mount the repository.
       Then run copy_configs.py to fetch inventory information for each
       VM in the repository, and store it into our 'inventory' directory.
    """
    print('Getting inventory for', r.name)
    print('Mount repos', r.name)
    if util.run_shell_command("./repos.py -m {}".format(r.name)):
        util.perror("getinv: error mounting repos {}".format(r.name))
        sys.exit(1)

    stat = util.run_shell_command(
              "./copy_configs.py {}/VirtualMachines/*/vm.cfg".format(r.mount))
    print('copy_config status', stat)



def get_repos_obj(name):
    """Return the repos config object with name 'name'"""

    for r in config.cfg_repos_list:
        if r.name == name:
            return r
    return None


def main():
    config.read_config()

    parse_commandline()

    if g.option == 'r':
        repos = get_repos_obj(g.repos)
        if repos:
            get_inventory(repos)
        else:
            util.perror("getinv: invalid repos name: {}".format(g.repos))
            g.status = 1
    elif g.option == 'a':
        for r in config.cfg_repos_list:
            get_inventory(r)
    else:
        raise

    # The following just concatenates all the vm 'disk' files into
    # one big file called 'DISKS'.
    dummy = util.run_shell_command('./build_disk_summary.sh {}'.format(config.cfg_inventory))

    print('exit', g.status)
    sys.exit(g.status)


if __name__ == '__main__':
    main()
