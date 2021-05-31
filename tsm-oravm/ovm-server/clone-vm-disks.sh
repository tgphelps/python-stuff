#!/bin/sh

# This script clones all virtual disks in our ONE repository,
# via reflink, changing the suffix from ".img" to ".img.CLONE".
# Surely this is harmless, unless we leave the clones lying around so
# long that the disk fills up.

LOG=/root/CLONE.LOG
NOW=`date`

echo START CREATE >>$LOG

for REPOS in /OVS/Repositories/* ; do
	echo Repository: $REPOS >>$LOG
	cd $REPOS/VirtualDisks
	for VMDISK in *.img ; do
		if [ -f $VMDISK.CLONE ] ; then
			echo '    ' clone exists: $VMDISK >>$LOG
		else
			echo '    ' make clone: $VMDISK.CLONE >>$LOG
			reflink $VMDISK $VMDISK.CLONE
		fi
	done
done
echo END CREATE >>$LOG
