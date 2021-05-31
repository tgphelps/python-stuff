#!/bin/sh

# This script compares the working direstory to the installed code,
# to see if we have changed something, but not put it into production.
# It is NOT used for any production purpose.

PROD=/opt/tsm-oravm
for x in *.py *.sh ovmbackup ovmlist ovmprune ovmcheck ; do
    # echo
    # echo '****' $x
    diff --brief $x $PROD/$x
done
