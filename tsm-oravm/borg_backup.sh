#!/bin/sh

# Backup all disks for a VM to the borg repository

if [ $# -lt 4 ] ; then
    echo usage: $0 borg-repos vm-name repos-path disks ...
    exit 2
fi

# sample args: /backups/borg-repository jidlcm01 /prod/repos1/VirtualDisks \
#              0004fb00012000f5beeb39ef23da11.img.CLONE

BORG=$1
VM=$2
REPOS=$3
shift 3
DISKS=$*
NOW=`date +%Y%m%d.%H%M%S`

# echo borg = $BORG
# echo vm = $VM
# echo repos = $REPOS
# echo disks = $DISKS

cd $REPOS
borg create -v --list -s -C zlib $BORG::$VM.$NOW $DISKS

echo STATUS: $?
