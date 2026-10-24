#!/bin/bash
# Time one generator run: bash g.sh problem args...
cd /mnt/d/projects/olymp.oshsu.kg/problemsets/kg2026
p=$1; shift
time (python3 $p/gen.py "$@" > /tmp/g.txt); wc -c /tmp/g.txt; head -c 300 /tmp/g.txt
