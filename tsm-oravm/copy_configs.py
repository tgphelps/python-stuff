#!/bin/env python3

"""Fetch config informatio from each vm.cfg file in a repository.

   Usage: copy_configs.py vm1 vm2 ...

   Each argument is the full path name of a vm.cfg file. We read each one,
   and store the information into various files in a subdirectory of
   'inventory', named by the VM name. And we insert rows into inventory.db
   to save several VM parameters which will be required for VM restores.
"""

import sys
import os
import shutil
import sqlite3

import config



class Globals:
    pass

g = Globals()
g.cursor = None



def create_name_file(dir, name):
    """Create 'name' file, containing the VM name, in directory 'dir'."""

    with open(dir + 'name', 'wt') as fp:
        fp.write(name + '\n')



def insert_disk_row(disk_name, disk_dev, disk_type, vm_name, ovm_simple_name):
    """Insert a row into the 'vdisk' table."""

    INSERT = """insert into vdisk (disk_name, disk_dev, disk_type, vm_name, ovm_simple_name)
                       values (?, ?, ?, ?, ?)"""
    g.cursor.execute(INSERT, (disk_name, disk_dev, disk_type, vm_name, ovm_simple_name))



def create_disks_file(dir, disks, vm_name, ovm_simple_name):
    """Create 'disks' file in directory 'dir'.

       Write one line to the file for each disk in the 'disks' array,
       containing: (1) disk name, (2) VM uuid, (3) VM name.
       Items in the 'disks' array look like this:
           file:/OVS/Rep/004/VirtualDisks/0004.img,xvda,w
           phy:/dev/mapper/ab12,xvdb,w
    """

    with open(dir + 'disks', 'wt') as fp:
        for d in disks:
            f1 = d.split(':')
            disk_type = f1[0]
            assert disk_type in ('file', 'phy')

            f2 = f1[1].split(',')
            disk_dev = f2[1]
            assert disk_dev.startswith('xvd')

            disk_path = f2[0]
            assert disk_path.startswith('/')
            if disk_type == 'file':
                f3 = disk_path.split('/')
                disk_name = f3[-1]
                assert disk_name.endswith('.img')
                fp.write("{}  {}  {}\n".format(disk_name, vm_name, ovm_simple_name))
            else:
                disk_name = disk_path
            insert_disk_row(disk_name, disk_dev, disk_type, vm_name, ovm_simple_name)



def get_vm_name(vm):
    """Return the 'OVM_simple_name' value from the file 'vm'."""

    vm_name = ''
    with open(vm, 'rt') as fp:
        for line in fp:
            line = line.strip()
            f = line.split()
            if len(f) < 3:
                continue
            if f[0] == 'OVM_simple_name':
                vm_name = f[2].split("'")[1]
                break

    assert vm_name != ''
    return vm_name



def insert_vm_row(vm, simple, cpu, mem, dom, os_type, nic_count):
    """Insert a row into the 'vm' table"""

    INSERT = """insert into vm (vm_name, ovm_simple_name, vcpus, memory,
                                ovm_domain_type, ovm_os_type, nic_count)
                       values (?, ?, ?, ?, ?, ?, ?)"""
    g.cursor.execute(INSERT, (vm, simple, cpu, mem, dom, os_type, nic_count))



def extract_params(dir):
    """Extract info from the 'vm.cfg' file in directory 'dir'.

       From that information, create the 'name' and 'disks' files
       in that same directory.
       Also, insert rows into inventory.db, to save various parameters
       needed for restores.
    """

    # WARNING: This codes assumes that the vm.cfg file contains valid
    # Python code, and uses eval() on strings read from that file.
    # If the file contains non-valid Python code, terrible things
    # can happen.
    vm_name = ''
    ovm_simple_name = ''
    ovm_domain_type = ''
    ovm_os_type = ''
    vcpus = 0
    memory = 0
    disks = []
    with open(dir + 'vm.cfg', 'rt') as fp:
        for line in fp:
            line = line.strip()
            f = line.split()
            if len(f) < 3:
                continue
            if f[0] == 'name':
                vm_name = eval(f[2])
            elif f[0] == 'OVM_simple_name':
                ovm_simple_name = eval(f[2])
            elif f[0] == 'vcpus':
                vcpus = int(eval(f[2]))
            elif f[0] == 'memory':
                memory = int(eval(f[2]))
            elif f[0] == 'OVM_domain_type':
                ovm_domain_type = eval(f[2])
            elif f[0] == 'OVM_os_type':
                # f[2] has embedded spaces, so we have to be careful
                ovm_os_type = eval(line.replace('OVM_os_type = ', ''))
            elif f[0] == 'disk':
                f2 = line.split('=')
                disks = eval(f2[1])
            elif f[0] == 'vif':
                f2 = line.split('=', 1)
                nics = eval(f2[1])
                assert type(nics) == type([])
                nic_count = len(nics)
                

    assert len(vm_name) > 0
    assert len(ovm_simple_name) > 0
    assert len(ovm_domain_type) > 0
    assert len(ovm_os_type) > 0
    assert len(disks) > 0
    assert vcpus > 0
    assert memory > 0

    create_name_file(dir, vm_name)
    insert_vm_row(vm_name, ovm_simple_name, vcpus, memory,
                  ovm_domain_type, ovm_os_type, nic_count)
    create_disks_file(dir, disks, vm_name, ovm_simple_name)



if __name__ == '__main__':
    config.read_config()

    db = sqlite3.connect(config.cfg_database)
    g.cursor = db.cursor()

    for vm in sys.argv[1:]:
        print(vm)
        vm_name = get_vm_name(vm)

        dest = config.cfg_inventory + vm_name + '/'
        try:
            os.mkdir(dest)
        except: # needs more checking
            pass
        shutil.copy(vm, dest);
        os.chmod(dest + 'vm.cfg', 0o644)
        extract_params(dest)

    db.commit()
    db.close()
