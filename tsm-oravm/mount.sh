#!/bin/sh

# usage: mount.sh server share mount-point

if [ $# != 3 ] ; then
    echo Bad arg count
    exit 1
fi

SERVER=$1
SHARE=$2
MNT=$3

if [ ! -d $MNT ] ; then
    echo error: $MNT is not a directory
    exit 1
fi
if [ ! -d $MNT/VirtualDisks ] ; then
    mount $SERVER:$SHARE $MNT
fi
