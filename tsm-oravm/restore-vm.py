#!/usr/bin/env python3

"""Print instructions on restoring a VM."""

import config
import sqlite3
import sys



def main():
    assert len(sys.argv) == 2
    vm = sys.argv[1]
    config.read_config()

    db = sqlite3.connect(config.cfg_database)
    cur = db.cursor()

    vm_row = get_vm_row(cur, vm)
    disks = get_disk_names(cur, vm)

    db.close()

    print('How to restore VM:', vm)
    print_vm_info(vm_row)
    print_disk_info(disks)



def get_disk_names(cur, vm):
    """Return an array of (name, dev) disk info for VM 'vm'."""

    SELECT = """select disk_name, disk_dev from vdisk
                where ovm_simple_name = ?"""
    cur.execute(SELECT, (vm,))
    disks = []
    for row in cur:
        disks.append(row)
    return disks



def get_vm_row(cur, vm):
    """Return the row of VM information for VM 'vm'"""
    SELECT = "select * from vm where ovm_simple_name = ?"
    cur.execute(SELECT, (vm,))
    return cur.fetchone()



def print_disk_info(disks):
    print("Import these virtual disks, if necessary:")
    for row in disks:
        name = row[0]
        if name.endswith('.img'):
            print("  ", name)
    print("")
    print("Attach disks to the VM as follows:")
    for row in disks:
        (name, dev) = row
        if name.startswith('/dev/mapper'):
            name = "LUN  " + name
        elif name.endswith('.img'):
            name = "DISK " + name
        else:
            raise
        print(dev, name)


def print_vm_info(vm_row):
    (vm, simple_name, vcpus, memory, domain_type, os_type, nics) = vm_row
    print("Create a VM named", simple_name)
    print("Set the following attributes:")
    print("   CPUS =", vcpus)
    print("   RAM =", memory, "MB")
    print("   NICs =", nics)
    print("   Domain type =", domain_type)
    print("   OS type =", os_type)



if __name__ == '__main__':
    main()
