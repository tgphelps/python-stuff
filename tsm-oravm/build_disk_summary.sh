#!/bin/sh

if [ $# -ne 1 ] ; then
    usage: $0 inv-dir
    exit 1
fi
INV=$1

cat $INV/*/disks >$INV/DISKS
