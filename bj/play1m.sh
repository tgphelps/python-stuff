#!/bin/sh

# For comparison with Go version

./bj.py        -n 200000 -s 5    data/house.cfg $1
./summary_stats.py
