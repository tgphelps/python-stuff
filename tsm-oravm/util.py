import sys
import os
import subprocess
import time

import config

# ----- DATA -----

backups = []
owner = {}


# ----- CLASSES -----

class Backup:
    # a[] is an array of fields from a "q vm" command
    def __init__(self, a):
        global owner
        self.date = a[2]
        self.time = a[3]

        # WARNING: The following assumes that the date looks like
        # mm/dd/yyyy. I found that 'dsmc' formats dates in accordance
        # with the setting of the LANG variable. A setting that works is:
        # LANG=en_US.UTF-8
        t = time.strptime(self.date + ' ' + self.time, "%m/%d/%Y %H:%M:%S")
        self.dt = time.mktime(t)

        self.status = a[5]
        assert self.status in ['A', 'I']

        path = a[6]
        assert path.endswith('.CLONE')
        # Strip off the '.CLONE'.
        path = path[0:-6]
        c = path.split('/')

        self.repos = c[2]
        self.disk = c[4]
        # If the disk/owner dict is empty, populate it
        if len(owner) == 0:
            build_disk_hash()
        if self.disk in owner:
            self.owner = owner[self.disk]
        else:
            self.owner = 'NONE'



# ----- FUNCTIONS -----


def perror(s):
    print(s, file=sys.stderr)



# Find the Vm object with this name, get the repos name, and then
# return the Repos object for that name.

def get_repos_for_vm(vm):
    for v in config.cfg_vm_list:
        if v.name == vm:
            repos = v.repos
            for r in config.cfg_repos_list:
                if r.name == repos:
                    return r
    # Abort if we didn't find it
    raise



# Run the shell command given by the string 'cmd'. Return the exit status.
# If you want to provide stdin, or capture stdout/stderr, you have
# to handle that yourself.

def run_shell_command(cmd):
    return subprocess.call(cmd, shell=True)



# Read the file $(cfg_inventory)/DISKS, and read the disk names and owners.
# Insert them into the dictionary 'owner'. NOTE: This dict is available
# ONLY inside this module.

def build_disk_hash():
    global owner
    with open(config.cfg_inventory + 'DISKS', 'rt') as f:
        for line in f:
            fld = line.strip().split()
            disk = fld[0]
            vm = fld[2]
            owner[disk] = vm


# Call 'dsmc' to get a list of (all, or only active) VM disk image backups.
# Put the output of 'dsmc' into config.cfg_tmpout).

def get_tsm_backup_list(active_only):
    if not active_only:
        s_ina = '-ina'
    else:
        s_ina = ''

    # We have to clear the temp file, because we're going to append to it.
    try:
        os.remove(config.cfg_tmpout)
    except OSError:
        pass

    for r in config.cfg_repos_list:
        cmd = "/usr/bin/dsmc q b '{}/VirtualDisks/' -sub=yes ".format(r.mount) \
            + s_ina + ">>{} 2>&1".format(config.cfg_tmpout)
        status = run_shell_command(cmd)
        if status != 0:
            perror('ERROR running command:')
            perror(cmd)
            sys.exit(1)



# Read the temp file created by get_vm_backup_list, create an
# array of Backup objects, and return it.

def read_backup_list():
    backups = []
    with open(config.cfg_tmpout, 'rt') as f:
        for line in f:
            # See if this line looks like a backup description
            fld = line.strip().split()
            # Sanity checks
            if len(fld) != 7: continue
            if fld[1] != 'B': continue
            if fld[5] not in ['A', 'I']: continue
            if len(fld[2]) != 10 or len(fld[3]) != 8: continue
            if not fld[6].endswith('.CLONE'): continue

            # Well, it sure looks like one to me.
            # Now create a backup object and save it 
            b = Backup(fld)

            # If this backup is for a disk that is not now attached to
            # a virtual machine, don't include it in the list.
            if b.owner != 'NONE':
                backups.append(b)
            else:
                print('Backup of', b.disk, 'is obsolete.')

    return backups

# Parse a config line, and create a standard structure that
# represents it. The structure will be a dictionary with one key
# called 'label' which is the first field of the line, and then
# one key for each attribute on the line. The value of each
# attribute key will be either a single value or an array,
# depending on whether the attribut looked like "attr=123" or
# "attr=12,23,34". We will truncate all attribute names to THREE
# characters, so the user need not type the entire name.
# We do NO checking of attribute values, or missing or duplicated
# attributes.
# The argument to this function comes from "line.split()".

def parse_config_line(fields):
    d = {}
    d['label'] = fields[0]

    for f in fields[1:]:
        # f looks like 'attr=...'
        a = f.split('=')
        # For consistency, truncate the attribute name to 3 chars.
        k = a[0][0:3]

        # The attribute may have multiple values. We do a simple check
        # for that (look for a comma). If there is a comma there,
        # split on comma, and store the array as the value of the key.
        # WARNING: We would be fooled by, say, "attr=','"
        if ',' in a[1]:
            d[k] = a[1].split(',')
        else:
            d[k] = a[1]

    return d
