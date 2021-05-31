#!/bin/sh

DIR=$1

if [ $# != 1 ] ; then
    echo 'usage: $0 <dir>'
    exit 2
fi

ls -l1 $DIR |grep -v lost+found
# for d in $DIR/* ; do
    # if [ $d != $DIR/lost+found ] ; then
        # echo $d
        # ls -l $d
    # fi
# done
