#!/bin/bash
# Print the answers to the samples of every built problem (inside WSL)
cd ${WORK:-/root/olymp2026}/build
for d in */; do d=${d%/}; [ -f $d/manifest.json ] || continue
  echo "== $d: $(head -c 160 $d/tests/01.out | tr '\n' ' ')"
done
