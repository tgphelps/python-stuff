#!/bin/sh

export PATH=$PATH:/usr/local/bin

LOG=/opt/tsm-oravm/getinv.lst
INV=/opt/tsm-oravm/inventory/

HOST=`hostname`
cd /opt/tsm-oravm

echo Calling clear-inventory.sh >$LOG
./clear-inventory.sh $INV      >>$LOG 2>&1

echo Re-creating inventory.db >>$LOG
./create-db.sh inventory.db >>$LOG 2>&1

./getinv.py -r prod1 >>$LOG 2>&1
STATUS=$?

echo '' >>$LOG
echo 'Database contents:' >>$LOG

sqlite3 inventory.db >>$LOG 2>&1 <<EOF
.headers on
.mode column
select 'VM table:';
select * from vm;
select 'VDISK table';
select * from vdisk;
EOF

echo ' ' >>$LOG
echo 'Disks present in repository:' >>$LOG

cat inventory/DISKS >>$LOG

if [ $STATUS = 0 ] ; then
    STAT='OK:'
else
    STAT='ERROR:'
fi
mail -s "$HOST:$STAT TSM-ORAVM get inventory" terry.phelps@aclines.com <$LOG
