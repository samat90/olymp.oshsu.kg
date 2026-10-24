#!/bin/bash
# Time the reference solution on every test: bash t.sh problem [binary-stem]
cd /mnt/d/projects/olymp.oshsu.kg/problemsets/kg2026
p=$1; stem=${2:-sol}
g++ -O2 -w -std=gnu++17 -o /tmp/t_$p $p/$stem.cpp || exit 1
for f in build/$p/tests/*.in; do
  s=$(date +%s.%N); /tmp/t_$p < $f > /tmp/t_out; e=$(date +%s.%N)
  ok=$(cmp -s /tmp/t_out ${f%.in}.out && echo ok || echo DIFF)
  printf "%s %.2f %s\n" $(basename $f) $(echo "$e - $s" | bc) $ok
done
