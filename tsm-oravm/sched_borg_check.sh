#!/bin/sh

export PATH=$PATH:/usr/local/bin

HOST=`hostname`
LOG=/opt/tsm-oravm/check_backups.lst
cd /opt/tsm-oravm
rm $LOG

echo Calling ovmcheck to check all Borg backups >>$LOG 2>&1
./ovmcheck  >>$LOG 2>&1

mail -s "$HOST: OVM check of Borg backups" terry.phelps@aclines.com <$LOG
