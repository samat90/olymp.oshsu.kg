#!/bin/bash
# Precompiles <bits/stdc++.h> for the flags DMOJ uses, so C++ programs compile ~3 times faster
# (on the laptop: 1.0 s -> 0.3 s). GCC picks the matching file by itself.
# Run as root on the judge machine after installing or upgrading g++, then restart the judges.
set -euo pipefail

HEADER=$(echo '#include <bits/stdc++.h>' | g++ -x c++ -E -H - 2>&1 >/dev/null \
    | grep 'bits/stdc++.h' | head -1 | awk '{print $2}')
[ -f "$HEADER" ] || { echo "bits/stdc++.h not found"; exit 1; }

# Must match "-march" in the judge config (DMOJ uses -march=native unless set otherwise).
MARCH=${MARCH:--march=native}

rm -rf "$HEADER.gch"
mkdir -p "$HEADER.gch"
for std in c++11 c++14 c++17 c++20; do
    g++ -x c++-header -DONLINE_JUDGE -O2 $MARCH -std=$std "$HEADER" -o "$HEADER.gch/$std.gch"
done
chmod -R a+rX "$HEADER.gch"
echo "Precompiled headers are in $HEADER.gch"
