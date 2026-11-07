#!/bin/bash
# Draw pictures and build problems inside WSL:  bash b.sh name...
# The sources are copied to a Linux folder first (much faster than building on /mnt/d);
# the tests stay in $WORK/build.
SRC=/mnt/d/projects/olymp.oshsu.kg/problemsets/olymp2026
WORK=${WORK:-/root/olymp2026}
python3 $SRC/pics.py "$@" > /dev/null
mkdir -p $WORK
rsync -a --exclude build $SRC/ $WORK/
cd $WORK
python3 build.py "$@"
