#!/bin/bash
# Adds the problems of problemsets/<set> that are not on the site yet. Runs on the web server as admin
# at the end of scripts/deploy.sh (the sets in OLYMP_PROBLEMSETS) or by hand:
#
#   bash scripts/server/import_problemsets.sh olymp2026
#
# The tests are not stored in git: they are generated on judge.oshsu.kg (it has g++ and python3) by the
# set's build.py, copied back over the LAN and added with manage.py import_problemset, which never
# changes or deletes existing problems. When a whole set is on the site, a marker file is written and
# the set is not looked at again (renaming a problem later will not bring the old copy back).
set -uo pipefail

APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
PY=${OLYMP_PY:-$APP/venv/bin/python}
JUDGE=${OLYMP_JUDGE:-admin@10.10.8.227}
SSH=${OLYMP_JUDGE_SSH:-ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new}
WORK=${OLYMP_PROBLEMSET_WORK:-/home/admin/problemsets}
JWORK=${OLYMP_PROBLEMSET_JUDGE_WORK:-/home/admin/problemsets-build}
AUTHOR=${OLYMP_PROBLEMSET_AUTHOR:-samat1}
JOBS=${OLYMP_PROBLEMSET_JOBS:-6}

log() { echo "[$(date +%H:%M:%S)] problemsets: $*"; }
free_gb() { df -Pk "$1" 2>/dev/null | awk 'NR == 2 { print int($4 / 1048576) }'; }

mkdir -p "$WORK"
status=0
for set in "$@"; do
    src=$APP/problemsets/$set
    if [ -f "$WORK/$set.done" ]; then continue; fi
    if [ ! -f "$src/build.py" ]; then log "$set: no build.py, skipped"; continue; fi

    missing=$(cd "$APP" && "$PY" manage.py shell -c "
import json, os
from judge.models import Problem
src = '$src'
for d in sorted(os.listdir(src)):
    p = os.path.join(src, d, 'problem.json')
    if os.path.exists(p) and not Problem.objects.filter(name=json.load(open(p, encoding='utf-8'))['name']).exists():
        print(d)" 2>/dev/null | tr '\n' ' ')
    if [ -z "${missing// /}" ]; then
        log "$set: every problem is on the site"
        touch "$WORK/$set.done"
        continue
    fi
    log "$set: adding $(echo $missing | wc -w) problems: $missing"

    if [ "$(free_gb "$WORK")" -lt 4 ]; then log "$set: less than 4 GB free in $WORK, skipped"; status=1; continue; fi
    if ! $SSH "$JUDGE" true; then log "$set: no SSH access to $JUDGE, skipped"; status=1; continue; fi
    jfree=$($SSH "$JUDGE" "mkdir -p '$JWORK' && df -Pk '$JWORK' | awk 'NR == 2 { print int(\$4 / 1048576) }'")
    if [ "${jfree:-0}" -lt 4 ]; then log "$set: less than 4 GB free on the judge, skipped"; status=1; continue; fi

    log "$set: generating the tests on the judge"
    if ! tar cf - --exclude=./build -C "$src" . | $SSH "$JUDGE" "set -e; rm -rf '$JWORK/$set'; mkdir -p '$JWORK/$set'; tar xf - -C '$JWORK/$set'"; then
        log "$set: copying the sources failed"; status=1; continue
    fi
    $SSH "$JUDGE" "cd '$JWORK/$set' && printf '%s\n' $missing | xargs -P $JOBS -I{} python3 build.py {} --no-stress > build.log 2>&1; \
        grep -E '^(FAILED|[a-z0-9]+: [0-9]+ tests)' build.log" | sed 's/^/    /'
    if $SSH "$JUDGE" "grep -q '^FAILED' '$JWORK/$set/build.log'"; then
        log "$set: some problems were not built (see $JWORK/$set/build.log on the judge), nothing imported"
        status=1; continue
    fi

    log "$set: copying the tests"
    rm -rf "$WORK/$set"
    mkdir -p "$WORK/$set"
    if ! $SSH "$JUDGE" "tar cf - --exclude=build/.bin -C '$JWORK/$set' build" | tar xf - -C "$WORK/$set"; then
        log "$set: copying the tests failed"; status=1; continue
    fi

    log "$set: import"
    if (cd "$APP" && "$PY" manage.py import_problemset "$WORK/$set/build" --only $missing --public --author "$AUTHOR"); then
        touch "$WORK/$set.done"
        rm -rf "$WORK/$set"
        $SSH "$JUDGE" "rm -rf '$JWORK/$set/build'" || true
        log "$set: done"
    else
        log "$set: import failed (the tests stay in $WORK/$set/build)"
        status=1
    fi
done
exit $status
