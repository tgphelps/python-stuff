#!/bin/sh

export PATH=$PATH:/usr/local/bin

# This LANG setting is mandatory, to make TSM format dates properly.
# export LANG=en_US.UTF-8

HOST=`hostname`
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

echo Refreshing inventory >>$LOG 2>&1
./get_inventory.sh

# echo Calling ovmbackup to do Borg backups >>$LOG 2>&1
./ovmbackup --borg --duration 30 >>$LOG 2>&1

echo  >>$LOG 2>&1
echo Latest backups of each VM >>$LOG 2>&1
./ovmlist -b >>$LOG 2>&1

echo  >>$LOG 2>&1
echo Removing old backups >>$LOG 2>&1
./ovmprune  >>$LOG 2>&1

echo  >>$LOG 2>&1
echo AVAILABLE BACKUP SPACE >>$LOG 2>&1
df -h /backups >>$LOG 2>&1

TOTAL=`grep -c 'Begin BORG backup' $LOG`
GOOD=`grep -c 'STATUS: 0' $LOG`

if [ $GOOD = $TOTAL ] ; then
    STAT=SUCCESS
else
    STAT=ERRORS
fi

SUBJ="$HOST: OVM backups. $STAT:  $GOOD of $TOTAL OK"
mail -s "$SUBJ" terry.phelps@aclines.com <$LOG
mail -s "$SUBJ" system_backups@aclines.com <$LOG
