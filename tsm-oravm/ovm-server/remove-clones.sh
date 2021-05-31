#!/bin/sh

# This script clones all virtual disks in all repository,
# via reflink, changing the suffix from ".img" to ".img.CLONE".
# Surely this is harmless, unless we leave the clones lying around so
# long that the disk fills up.

LOG=/root/CLONE.LOG
NOW=`date`
echo $NOW START REMOVE >>$LOG

for REPOS in /OVS/Repositories/* ; do
	echo Repository: $REPOS >>$LOG
	cd $REPOS/VirtualDisks
	for VMDISK in *.img.CLONE ; do
		if [ $VMDISK != '*.img.CLONE' ] ; then
			echo '    ' remove $VMDISK >>$LOG
			rm $VMDISK
		else
			echo no clone files >>$LOG
		fi
	done
done
echo END REMOVE >>$LOG
