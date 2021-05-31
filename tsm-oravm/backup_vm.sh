#!/bin/sh

export PATH=$PATH:/usr/local/bin

# This LANG setting is mandatory, to make TSM format dates properly.
export LANG=en_US.UTF-8

LOG=/opt/tsm-oravm/backup_vm.lst
cd /opt/tsm-oravm
rm $LOG

# Make sure the production repository is mounted
./repos.py -m prod1
if [ $? != 0 ] ; then
    echo ERROR mounting prod repository >>$LOG 2>&1
    exit 1
else
    echo prod repository is mounted >>$LOG 2>&1
fi

echo Calling get_inventory.sh >>$LOG 2>&1
./get_inventory.sh

# This will backup at most ONE VM
./ovmbackup -d 1 >>$LOG 2>&1

# Show all current backups
./ovmlist >>$LOG 2>&1

grep -q 'NO backups needed' $LOG
if [ $? != 0 ] ; then
    mail -s 'Oracle VM backup' terry.phelps@aclines.com <$LOG
else
    mail -s 'Oracle VM backup: NOTHING TO DO' terry.phelps@aclines.com <$LOG
fi
