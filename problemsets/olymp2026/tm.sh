#!/bin/bash
# Time the reference solution on every test of the given problems (inside WSL): bash tm.sh name...
cd ${WORK:-/root/olymp2026}
for p in "$@"; do
  exe=$(ls -t build/.bin/${p}_sol-* | head -1)
  worst=0; wt=
  for t in build/$p/tests/*.in; do
    s=$(date +%s.%N); $exe < $t > /tmp/tm_out; e=$(date +%s.%N)
    cmp -s /tmp/tm_out ${t%.in}.out || echo "$p $t DIFF"
    d=$(echo "$e - $s" | bc)
    if (( $(echo "$d > $worst" | bc) )); then worst=$d; wt=$t; fi
  done
  printf "%s %.2f %s\n" $p $worst $(basename $wt)
done
