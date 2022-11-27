import os
import config

# Create and return an array of the VMs that need backups,
# sorted in descending order of importance.
#
# Method:
# Iterate over the list of configured VMs, and check the list of active
# backups to see whether the age of the active backup is over the
# threshold of being too old. If it is, add this VM to the work queue.
# Finally, sort the work queue, first by priority and then by days overdue
# for a backup.
#
# To make the search for a backup faster, we'll build a dictionary of the
# backups, keyed on the VM name.

def create_tsm_work_queue(backup_list, now):
    bkup = {}
    bk_count = 0
    for b in backup_list:
        bk_count += 1
        assert b.status == 'A'

        # XXX We'll be simple and take the first disk backup we come to, for each VM
        if not b.owner in bkup:
            bkup[b.owner] = b
    print('active backup count =', bk_count)
    assert bk_count > 0

    # Iterate through the configured VMs, and see if they need backups
    wq = []
    # Verbose debugging in this loop
    for vm in config.cfg_vm_list:
        if vm.name in bkup:
            # print('   there IS a backup')
            b = bkup[vm.name]
            vm.age = now - b.dt
            # print('   AGE of backup =', vm.age / 86400.0)
            # Now we compare the age of the active backup to
            # the configured backup interval for this VM,
            # rounding the age to an integer.
            if vm.interval <= int(vm.age / 86400.0 + 0.5):
                # print('   age is TOO HIGH. Needs backup.')
                vm.days_late = vm.age - vm.interval * 86400.0
                vm.days_late /= 86400.0
                wq.append(vm)
            else:
                pass
                # print('   age is OKAY. No backup needed')
        else:
            # print('   NO backup exists. Needs backup.')
            # b = bkup[vm.name]
            vm.age = 86400000
            vm.days_late = vm.age - vm.interval * 86400.0
            vm.days_late /= 86400.0
            # print('   AGE of backup =', vm.age / 86400.0)
            wq.append(vm)

    # Work queue has been built. Sort it into the order backups
    # should be done.

    wq.sort(key = lambda vm: (vm.priority, -vm.days_late))

    return wq

def print_tsm_work_queue(wq):
    print('')
    print('')
    print('  VM name            PRI INTVL   AGE   OVERDUE    SCHED')
    print('-------------------- --- -----  ------ ------- ------------')
    for vm in wq:
        print('{:20} {:3} {:5.0f} {:7.1f} {:7.1f} {}'.format( \
              vm.name, vm.priority, vm.interval, vm.age / 86400, \
              vm.days_late, vm.schedule))



# Return modification time of the directory that should contain
# the local backup of VM 'name'. If the directory isn't there, return 0.

def local_backup_mtime(name):
    dir_name = config.cfg_local_dir + name
    if os.path.isdir(dir_name):
        return os.path.getmtime(dir_name)
    else:
        return 0



def create_local_work_queue(now):
    wq = []
    for vm in config.cfg_vm_list:
        if vm.local > 0:
            mtime  = local_backup_mtime(vm.name)
            if mtime == 0:
                # There was NO local backup of this VM
                vm.age = 1000 * 86400
            else:
                vm.age = now - mtime
            print('DBG: vm = {}  age = {} local = {:f}'.format(vm.name, vm.age, vm.local))
            if vm.local <= vm.age /86400.0 + 0.5:
                vm.days_late = (vm.age - vm.local * 86400) / 86400
                wq.append(vm)
    wq.sort(key = lambda vm: (vm.priority, -vm.days_late))
    return wq



def print_local_work_queue(wq):
    print('')
    print('')
    print('  VM name            PRI L INT   AGE   OVERDUE    SCHED')
    print('-------------------- --- -----  ------ ------- ------------')
    for vm in wq:
        print('{:20} {:3} {:5.0f} {:7.1f} {:7.1f} {}'.format( \
              vm.name, vm.priority, vm.local, vm.age / 86400, \
              vm.days_late, vm.schedule))
