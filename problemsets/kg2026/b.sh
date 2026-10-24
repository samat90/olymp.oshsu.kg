#!/bin/bash
# Build problems inside WSL and print answer statistics.  Usage: bash b.sh name...
cd /mnt/d/projects/olymp.oshsu.kg/problemsets/kg2026
python3 build.py "$@" 2>&1 | grep -v ': group '
for p in "$@"; do
  [ "${p#--}" != "$p" ] && continue
  for f in build/$p/tests/*.out; do
    echo "$(basename $f) lines=$(wc -l < $f) neg=$(grep -c '^-1' $f) uniq=$(sort -u $f | wc -l) $(head -c 60 $f | tr '\n' ' ')"
  done
done
