#!/bin/sh

# Backup a VM disk to the local filesystem.

if [ $# != 4 ] ; then
    echo usage: $0 vm-name disk-name repos-path dest-dir
    exit 2
fi

# sample args: jidlcm01 0004fb00012000f5beeb39ef23da11.img /repos/prod1 /backup/

VM=$1
DISK=$2
REPOS=$3
DEST=${4}$VM

if [ ! -d $DEST ] ; then
    mkdir -p $DEST
fi

rm $DEST/$DISK.gz

gzip -c --fast $REPOS/VirtualDisks/$DISK.CLONE >$DEST/$DISK.gz

echo GZIP STATUS: $?

echo RESULT: `ls -l $DEST/$DISK.gz`
