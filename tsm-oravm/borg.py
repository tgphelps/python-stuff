#!/usr/bin/env python3

"""Almost all borg-unique code lives here."""

import subprocess
import time

import logging
import util



class Backup:
    """Structure that represents a backup that has been done."""
    def __init__(self, fld):
        """Create object from 'fld' list

           'fld' is a split() line from 'borg list repo' output
        """
        assert len(fld) == 4
        self.name = fld[0]
        self.date_time = fld[2] + '-' + fld[3]
        a = self.name.split('.')
        # Try to get the VM name from the backup name
        if len(a) == 3 and len(a[1]) == 8 and len(a[2]) == 6:
            self.vm = a[0]
        else:
            self.vm = 'UNKNOWN'

    def __repr__(self):
        return 'Backup vm: {} date-time: {}'.format(self.vm, self.date_time)



def build_backup_cmd(vm, disks, config):
    """Return shell command to borg backup this VM."""

    repos = util.get_repos_for_vm(vm)
    cmd = './borg_backup.sh {} {} {}/VirtualDisks '.format( \
          config.cfg_borg_repos, vm, repos.mount)
    clones = [ disk + '.CLONE' for disk in disks]
    cmd += ' '.join(clones)
    return cmd



def backup_vm(vm, disks, config, outfile):
    """Run the borg command to backup all disks for a VM."""

    print('Begin BORG backup of', vm)
    cmd = build_backup_cmd(vm, disks, config)
    cmd += ' >{} 2>&1'.format(outfile,)
    # print('shell cmd =', cmd)
    logging.info('Backup cmd: ' + cmd)
    cmd_status = util.run_shell_command(cmd)
    logging.info('Shell cmd status = ' + str(cmd_status))



def check_backup(vm, fname):
    """Return MBs backed up if successful, else zero."""

    megs = 0
    status = None
    with open(fname, 'rt') as fp:
        for line in fp:
            line = line.rstrip()
            if line.startswith('STATUS:'):
                f = line.split()
                status = f[1]
                logging.info(line)
                print(line)
            if line.startswith('This archive:'):
                logging.info(line)
                print(line)
                f = line.split()
                assert f[3] == 'GB'
                gigs = float(f[2])
                megs = int(gigs * 1024)
            if line.startswith('Chunk index:'):
                logging.info(line)
                print(line)

    if status == '0':
        return megs
    else:
        print('ERROR: borg status =', status)
        return 0



def latest_backups(backups):
    """Return a list of only the latest backup for each VM."""

    newest = {}
    for bk in backups:
        if bk.vm not in newest:
            newest[bk.vm] = bk
        else:
            if bk.date_time > newest[bk.vm].date_time:
                newest[bk.vm] = bk
    new_backups = []
    for k in newest:
        new_backups.append(newest[k])
    # print('backup count =', len(new_backups))
    return new_backups



def print_backups(backups, sort='name'):

    assert sort in ('name', 'age')
    if sort == 'name':
        sorted_backups = sorted(backups, key=lambda bk: bk.name)
    else:
        sorted_backups = sorted(backups, key=lambda bk: bk.date_time, reverse=True)
    for b in sorted_backups:
        print('{:30} {}'.format(b.name, b.date_time))



def get_backups(repos, show_all):
    """Return a list of all (or latest) backups that we have."""

    backups = []
    proc = subprocess.Popen(['borg', 'list', repos], stdout=subprocess.PIPE)
    data = proc.communicate()[0]
    data = data.decode()
    lines = data.split('\n')
    for l in lines:
        if l == '': continue
        fld = l.split()
        backups.append(Backup(fld))
    # print('show_all =', show_all)
    if not show_all:
        return latest_backups(backups)
    else:
        return backups



def get_latest_backup(vm, backups):
    """Return the backup for the given VM from the list supplied."""

    for b in backups:
        if b.vm == vm.name:
            return b
    return None



def create_work_queue(config):
    """Create a list of VMs that need backups, with most urgent at the top."""

    now = time.mktime(time.localtime())
    backups = get_backups(config.cfg_borg_repos, show_all=False)
    # backups = list of latest backup for each VM
    for b in backups:
        # Fill in the date/time and age fields
        t = time.strptime(b.date_time, '%Y-%m-%d-%H:%M:%S')
        b.dt = time.mktime(t)
        b.age = now - b.dt
        # print('date_time', b.date_time, 'age', b.age)
    # For each vm, fill in the age of the latest backup.
    vms = []
    for vm in config.cfg_vm_list:
        latest = get_latest_backup(vm, backups)
        if not latest:
            vm.age = 1000.0 * 86400
        else:
            vm.age = latest.age
        if vm.local <= int(vm.age / 86400 + 0.5):
            vm.days_late = (vm.age - vm.local * 86400) / 86400
            vms.append(vm)
    
    return sorted(vms, key = lambda vm: (vm.priority, -vm.days_late))



def print_work_queue(wq):
    """Print the list of backups that we need to do."""

    print('')
    print('')
    print('  VM name            PRI B INT   AGE   OVERDUE    SCHED')
    print('-------------------- --- -----  ------ ------- ------------')
    for vm in wq:
        print('{:20} {:3} {:5.0f} {:7.1f} {:7.1f} {}'.format( \
              vm.name, vm.priority, vm.local, vm.age / 86400, \
               vm.days_late, vm.schedule))



if __name__ == '__main__':
    print('borg test')
    backup_vm('vm1', ['d1', 'd2'], 'listing')
    megs = check_backup('vm1', 'listing')
    print('megs =', megs)
