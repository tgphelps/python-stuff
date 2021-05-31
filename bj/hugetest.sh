#!/bin/sh

rm stats.txt
make hugetest

echo Test differences:
diff stats.txt data/std_hugetest.txt
