#!/bin/sh

# usage: umount.sh  mount-point

if [ $# != 1 ] ; then
    echo Bad arg count
    exit 1
fi

MNT=$1

if [ ! -d $MNT ] ; then
    echo error: $MNT is not a directory
    exit 1
fi
if [ ! -d $MNT/VirtualDisks ] ; then
    echo $MNT is not a repository
    exit 1
fi
umount $MNT
