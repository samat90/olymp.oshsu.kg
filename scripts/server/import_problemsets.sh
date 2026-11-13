#!/bin/bash
# Adds the problems of problemsets/<set> that are not on the site yet. Runs on the web server as admin
# at the end of scripts/deploy.sh (the sets in OLYMP_PROBLEMSETS) or by hand:
#
#   bash scripts/server/import_problemsets.sh olymp2026
#
# The tests are not stored in git: they are generated on judge.oshsu.kg (it has g++ and python3) by the
# set's build.py, copied back over the LAN and added with manage.py import_problemset, which never
# changes or deletes existing problems. Problems are added one by one within a time budget; the next run
# (scripts/server/autodeploy.sh calls this every few minutes) continues. When a whole set is on the site,
# a marker file is written and the set is not looked at again (a renamed problem will not come back).
set -uo pipefail

APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
PY=${OLYMP_PY:-$APP/venv/bin/python}
JUDGE=${OLYMP_JUDGE:-admin@10.10.8.227}
SSH=${OLYMP_JUDGE_SSH:-ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new}
WORK=${OLYMP_PROBLEMSET_WORK:-/home/admin/problemsets}
JWORK=${OLYMP_PROBLEMSET_JUDGE_WORK:-/home/admin/problemsets-build}
AUTHOR=${OLYMP_PROBLEMSET_AUTHOR:-samat1}
BUDGET=${OLYMP_PROBLEMSET_BUDGET:-1200}  # seconds per run
BUILD_TIMEOUT=${OLYMP_PROBLEMSET_BUILD_TIMEOUT:-1500}  # seconds for the tests of one problem
# Memory for one build (the judge has 4 GB; a runaway generator once made the kernel kill processes there).
BUILD_MEMORY_KB=${OLYMP_PROBLEMSET_BUILD_MEMORY_KB:-2000000}
START=$(date +%s)

log() { echo "[$(date +%H:%M:%S)] problemsets: $*"; }
free_gb() { df -Pk "$1" 2>/dev/null | awk 'NR == 2 { print int($4 / 1048576) }'; }

mkdir -p "$WORK"
# One import at a time: two imports at once (a manual one and the auto-deploy) broke a build on 2026-11-09.
exec 8> "$WORK/.lock"
flock -n 8 || { log "another import is running, skipped"; exit 0; }
status=0
for set in "$@"; do
    src=$APP/problemsets/$set
    if [ -f "$WORK/$set.done" ]; then continue; fi
    if [ ! -f "$src/build.py" ]; then log "$set: no build.py, skipped"; continue; fi

    missing=$(cd "$APP" && "$PY" manage.py shell -c "
import json, os
from judge.models import Problem
src = '$src'
names = os.path.join(src, 'names.txt')
if os.path.exists(names):  # pure-Python sets: one 'folder<TAB>name' line per problem
    items = [l.rstrip('\n').split('\t') for l in open(names, encoding='utf-8') if l.strip()]
else:
    items = []
    for d in sorted(os.listdir(src)):
        p = os.path.join(src, d, 'problem.json')
        if os.path.exists(p):
            items.append((d, json.load(open(p, encoding='utf-8'))['name']))
have = set(Problem.objects.values_list('name', flat=True))
for d, name in items:
    if name not in have:
        print(d)" 2>/dev/null | tr "\n" ' ')
    if [ -z "${missing// /}" ]; then
        log "$set: every problem is on the site"
        touch "$WORK/$set.done"
        continue
    fi
    log "$set: adding $(echo $missing | wc -w) problems: $missing"

    if [ "$(free_gb "$WORK")" -lt 1 ]; then log "$set: less than 1 GB free in $WORK, skipped"; status=1; continue; fi
    if ! $SSH "$JUDGE" true; then log "$set: no SSH access to $JUDGE, skipped"; status=1; continue; fi
    jfree=$($SSH "$JUDGE" "mkdir -p '$JWORK' && df -Pk '$JWORK' | awk 'NR == 2 { print int(\$4 / 1048576) }'")
    if [ "${jfree:-0}" -lt 1 ]; then log "$set: less than 1 GB free on the judge, skipped"; status=1; continue; fi

    if ! tar cf - --exclude=./build -C "$src" . | $SSH "$JUDGE" "set -e; rm -rf '$JWORK/$set'; mkdir -p '$JWORK/$set'; tar xf - -C '$JWORK/$set'"; then
        log "$set: copying the sources failed"; status=1; continue
    fi
    # One problem at a time, so that an interrupted run keeps what it has added; the next run continues.
    for d in $missing; do
        if [ $(( $(date +%s) - START )) -gt "$BUDGET" ]; then log "$set: time is up, the rest will be added by the next run"; break; fi
        if [ -f "$WORK/$set.$d.failed" ]; then continue; fi
        log "$set/$d: generating the tests on the judge"
        # A build that hangs must not hold the auto-deploy forever: it is stopped after BUILD_TIMEOUT and the
        # problem is marked as failed (delete $WORK/$set.$d.failed to try it again).
        if ! $SSH "$JUDGE" "cd '$JWORK/$set' && ulimit -v $BUILD_MEMORY_KB; timeout -k 30 $BUILD_TIMEOUT python3 build.py $d --no-stress --no-brute > build-$d.log 2>&1"; then
            log "$set/$d: not built: $($SSH "$JUDGE" "tail -c 300 '$JWORK/$set/build-$d.log'")"
            touch "$WORK/$set.$d.failed"; status=1; continue
        fi
        rm -rf "${WORK:?}/$set"
        mkdir -p "$WORK/$set/build"
        if ! $SSH "$JUDGE" "tar cf - -C '$JWORK/$set/build' $d && rm -rf '$JWORK/$set/build/$d'" | tar xf - -C "$WORK/$set/build"; then
            log "$set/$d: copying the tests failed"; status=1; continue
        fi
        (cd "$APP" && "$PY" manage.py import_problemset "$WORK/$set/build" --only $d --public --author "$AUTHOR") | sed 's/^/    /'
        rm -rf "${WORK:?}/$set"
    done
done
exit $status
