#!/bin/sh

INV=/opt/tsm-oravm/inventory/

# I want to have the caller supply the inventory location, but since
# root will be running this script, and will be doing 'rm -fr', I am
# afraid of some terrible accident. SO: The caller will supply what
# he thinks is the inventory directory, and but we will verify that
# it is the hard-coded value above. In this way, if the inventory
# location changes, this script will note it and fail, and will need
# modification to match.

if [ $# != 1 ] ; then
    echo 'usage: $0 <inventory-location>'
    exit 2
fi
if [ $1 != $INV ] ; then
    echo $0: ERROR: inventory location invalid
    exit 2
fi

for DIR in $INV/* ; do
    echo rm -fr $DIR
    rm -fr $DIR
done
