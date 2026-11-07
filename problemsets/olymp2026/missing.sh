#!/bin/bash
# List problems that have no built manifest yet (inside WSL)
cd ${WORK:-/root/olymp2026}
for d in */; do d=${d%/}; [ -f $d/problem.json ] && [ ! -f build/$d/manifest.json ] && echo -n "$d "; done; echo
