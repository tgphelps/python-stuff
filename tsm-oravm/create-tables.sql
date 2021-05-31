
--- TODO: Document NICs

create table if not exists
vm (
    vm_name text primary key,
    OVM_simple_name text,
    vcpus integer,
    memory integer,
    OVM_domain_type text,
    OVM_os_type text,
    nic_count integer
);

create table if not exists
vdisk (
    vm_name text,
    disk_dev text,
    disk_name text,
    disk_type text,
    ovm_simple_name,
    primary key (vm_name, disk_dev)
);
