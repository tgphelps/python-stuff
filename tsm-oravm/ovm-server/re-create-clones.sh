#!/bin/sh

PATH=/usr/bin:/bin
export PATH

cd /root/bin

./remove-clones.sh
sync
sleep 5
./clone-vm-disks.sh

# Mail results
./smtp.py
