#!/bin/sh

if [ $# != 1 ] ; then
    echo 'usage: $0 <db-path>'
    exit 2
fi

DB=$1

if [ -f $DB ] ; then
    rm $DB
fi
sqlite3 $DB ".read create-tables.sql"
