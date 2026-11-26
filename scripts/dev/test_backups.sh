#!/bin/bash
# Tests of the backup rotation: the daily backup (server-config/web/usr/local/bin/olymp-backup.sh) and
# the deploy backups (scripts/server/prune_deploy_backups.sh). Everything happens in a temporary folder;
# pg_dump, pg_restore, redis-cli and sudo are replaced by stubs. Needs GNU tools (Linux, as on the server).
#
#   bash scripts/dev/test_backups.sh
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
DAILY=$ROOT/server-config/web/usr/local/bin/olymp-backup.sh
PRUNE=$ROOT/scripts/server/prune_deploy_backups.sh
W=$(mktemp -d)
trap 'rm -rf "$W"' EXIT
mkdir -p "$W/bin"

# A fake dump is "PGDMP" plus filler; one that contains BROKEN cannot be read, as a truncated dump.
cat > "$W/bin/sudo" <<'EOF'
#!/bin/bash
[ "$1" = -u ] && shift 2
exec "$@"
EOF
cat > "$W/bin/pg_dump" <<'EOF'
#!/bin/bash
case "${FAKE_DUMP:-ok}" in
    fail) echo "pg_dump: connection refused" >&2; exit 1 ;;
    empty) exit 0 ;;
    broken) printf 'PGDMP BROKEN'; head -c 5000 /dev/zero ;;
    notables) printf 'PGDMP NOTABLES'; head -c 5000 /dev/zero ;;
    small) printf 'PGDMP'; head -c 2000 /dev/zero ;;
    ok) printf 'PGDMP'; head -c 5000 /dev/zero ;;
esac
EOF
cat > "$W/bin/pg_restore" <<'EOF'
#!/bin/bash
file=${!#}
head -c 5 "$file" | grep -q PGDMP || exit 1
if [ "$1" = -l ]; then
    grep -aq NOTABLES "$file" || echo "3000; 0 16400 TABLE DATA public auth_user olymp"
    exit 0
fi
! grep -aq BROKEN "$file"
EOF
cat > "$W/bin/redis-cli" <<'EOF'
#!/bin/bash
if [ "$1" = save ]; then echo "${FAKE_REDIS:-OK}"; exit 0; fi
# redis-cli -n <db> --scan --pattern 'olst:*': the visit statistics live in database 1
[ "$2" = 1 ] && for ((i = 0; i < ${FAKE_KEYS:-100}; i++)); do echo "olst:key$i"; done
exit 0
EOF
cat > "$W/bin/sync" <<'EOF'
#!/bin/bash
exit "${FAKE_SYNC:-0}"
EOF
cat > "$W/bin/redis-check-rdb" <<'EOF'
#!/bin/bash
exit 0
EOF
chmod +x "$W"/bin/*
export PATH="$W/bin:$PATH"

failures=0
check() { # check <description> <command...>
    local what=$1; shift
    if "$@" > /dev/null 2>&1; then
        echo "  ok    $what"
    else
        echo "  FAIL  $what"; failures=$((failures + 1))
    fi
}
files() { # names in the daily folder, one line
    find "$D" -mindepth 1 -maxdepth 1 -printf '%f\n' | sort | tr '\n' ' '
}
check_is() { # check_is <description> <got> <expected>
    if [ "$2" = "$3" ]; then
        echo "  ok    $1"
    else
        echo "  FAIL  $1"; printf '        got:      %s
        expected: %s
' "$2" "$3"; failures=$((failures + 1))
    fi
}
run_daily() { # run_daily <stamp> ; extra settings come from the environment
    OLYMP_BACKUP_DIR=$D OLYMP_APP=$W/app OLYMP_REDIS_RDB=$W/dump.rdb OLYMP_MIN_DB_BYTES=1000 \
        OLYMP_BACKUP_STAMP=$1 bash "$DAILY" > "$W/log" 2>&1
}
fresh() { # a daily folder with three old good copies and a few files that must never be touched
    rm -rf "$W/app" "$W/olymp"
    D=$W/olymp/daily
    mkdir -p "$D" "$W/app/problems/aplusb" "$W/app/media/avatars" "$W/olymp/20261021-preolymp" "$W/olymp/20261126-premaint"
    echo tests > "$W/app/problems/aplusb/tests.zip"
    echo picture > "$W/app/media/avatars/1.jpg"
    printf 'REDIS0011data' > "$W/dump.rdb"
    echo keep > "$W/olymp/20261021-preolymp/database.dump"
    echo keep > "$W/olymp/20261126-premaint/db-20261126-0519.dump"
    local day
    for day in 20261101 20261102 20261103; do
        { printf 'PGDMP'; head -c 5000 /dev/zero; } > "$D/db-$day-0330.dump"
        echo old > "$D/problems-$day-0330.tgz"
        echo old > "$D/media-$day-0330.tgz"
        echo old > "$D/redis-$day-0330.rdb"
    done
    echo mine > "$D/db-before-import.dump"
    echo mine > "$D/db-20261102-0330.dump.keep"
}
KEPT="db-20261102-0330.dump.keep"
OLD_DB="db-20261101-0330.dump db-20261102-0330.dump"
manual_untouched() {
    [ -f "$W/olymp/20261021-preolymp/database.dump" ] && [ -f "$W/olymp/20261126-premaint/db-20261126-0519.dump" ] &&
        [ -f "$D/db-before-import.dump" ] && [ -f "$D/db-20261102-0330.dump.keep" ]
}
no_parts() { [ -z "$(find "$D" -name '*.part')" ]; }

echo "daily: success keeps only the new copy"
fresh
check "exit status 0" run_daily 20261104-0330
check_is "files" "$(files)" "$KEPT db-20261104-0330.dump db-before-import.dump media-20261104-0330.tgz problems-20261104-0330.tgz redis-20261104-0330.rdb redis-visit-keys "
check "manual copies untouched" manual_untouched
check "problem archive is readable" tar -tzf "$D/problems-20261104-0330.tgz"

echo "daily: unchanged problem archive is the same file on disk"
inode=$(stat -c %i "$D/problems-20261104-0330.tgz")
check "exit status 0" run_daily 20261105-0330
check_is "same inode" "$(stat -c %i "$D/problems-20261105-0330.tgz")" "$inode"
check_is "one problem archive" "$(find "$D" -name 'problems-*' | wc -l)" 1

for mode in fail empty broken notables; do
    echo "daily: database dump '$mode' keeps the old database copies"
    fresh
    export FAKE_DUMP=$mode
    run_daily 20261104-0330; check_is "exit status" "$?" 1
    unset FAKE_DUMP
    check_is "files" "$(files)" "$OLD_DB $KEPT db-20261103-0330.dump db-before-import.dump media-20261104-0330.tgz problems-20261104-0330.tgz redis-20261104-0330.rdb redis-visit-keys "
    check "error in the log" grep -q 'ERROR: database' "$W/log"
    check "no .part left" no_parts
done

echo "daily: problem data missing or empty keeps the old archives"
fresh
rm -rf "$W/app/problems"
run_daily 20261104-0330; check_is "exit status" "$?" 1
check_is "old archives kept" "$(find "$D" -name 'problems-*' | wc -l)" 3
check_is "database still rotated" "$(find "$D" -name 'db-2026????-????.dump' -printf '%f ')" "db-20261104-0330.dump "
fresh
rm -rf "$W/app/problems/aplusb"
run_daily 20261104-0330; check_is "exit status" "$?" 1
check_is "old archives kept" "$(find "$D" -name 'problems-*' | wc -l)" 3
check "no .part left" no_parts

echo "daily: Redis that does not save keeps the old Redis copies"
fresh
export FAKE_REDIS='NOAUTH Authentication required.'
run_daily 20261104-0330; check_is "exit status" "$?" 1
unset FAKE_REDIS
check_is "old Redis copies kept" "$(find "$D" -name 'redis-*' | wc -l)" 3
check_is "database still rotated" "$(find "$D" -name 'db-2026????-????.dump' -printf '%f ')" "db-20261104-0330.dump "

echo "daily: a database dump less than half the size of the kept one does not replace it"
fresh
{ printf 'PGDMP'; head -c 9000 /dev/zero; } > "$D/db-20261103-0330.dump"
export FAKE_DUMP=small
run_daily 20261104-0330; check_is "exit status" "$?" 1
check "big copy kept" test -f "$D/db-20261103-0330.dump"
run_daily 20261105-0330; check_is "exit status next day" "$?" 1
check_is "big and newest only" "$(find "$D" -name 'db-2026????-????.dump' -printf '%f\n' | sort | tr '\n' ' ')" "db-20261103-0330.dump db-20261105-0330.dump "
OLYMP_ACCEPT_SHRINK=1 run_daily 20261106-0330; check_is "accepted by hand" "$?" 0
check_is "only the newest" "$(find "$D" -name 'db-2026????-????.dump' -printf '%f ')" "db-20261106-0330.dump "
unset FAKE_DUMP

echo "daily: leftovers of an interrupted run are removed"
fresh
echo half > "$D/problems-20261103-0330.tgz.part"
run_daily 20261104-0330
check "no .part left" no_parts

names() { find "$D" -name "$1" -printf '%f
' | sort | tr '
' ' '; }

echo "daily: problem data that lost most of its size does not replace the full archive"
fresh
head -c 200000 /dev/urandom > "$W/app/problems/aplusb/big.bin"
run_daily 20261104-0330
rm "$W/app/problems/aplusb/big.bin"
run_daily 20261105-0330; check_is "exit status" "$?" 1
run_daily 20261106-0330; check_is "exit status next day" "$?" 1
check_is "full and newest" "$(names 'problems-*')" "problems-20261104-0330.tgz problems-20261106-0330.tgz "
OLYMP_ACCEPT_SHRINK=1 run_daily 20261107-0330; check_is "accepted by hand" "$?" 0
check_is "only the newest" "$(names 'problems-*')" "problems-20261107-0330.tgz "

echo "daily: Redis that lost the visit statistics does not replace the good copy"
fresh
run_daily 20261104-0330; check_is "exit status" "$?" 0
export FAKE_KEYS=0
run_daily 20261105-0330; check_is "exit status" "$?" 1
run_daily 20261106-0330; check_is "exit status next day" "$?" 1
check_is "good and newest" "$(names 'redis-2*')" "redis-20261104-0330.rdb redis-20261106-0330.rdb "
OLYMP_ACCEPT_SHRINK=1 run_daily 20261107-0330; check_is "accepted by hand" "$?" 0
check_is "only the newest" "$(names 'redis-2*')" "redis-20261107-0330.rdb "
unset FAKE_KEYS

echo "daily: nothing is removed when the new copy cannot be written to the disk"
fresh
export FAKE_SYNC=1
run_daily 20261104-0330; check_is "exit status" "$?" 1
unset FAKE_SYNC
check_is "database copies" "$(find "$D" -name 'db-2026????-????.dump' | wc -l)" 4
check_is "problem archives" "$(find "$D" -name 'problems-*' | wc -l)" 4
check_is "media archives" "$(find "$D" -name 'media-*' | wc -l)" 4
check_is "Redis copies" "$(find "$D" -name 'redis-2*.rdb' | wc -l)" 4

echo "daily: with a shrunken dump the latest good copy is kept, not only the biggest"
fresh
{ printf 'PGDMP'; head -c 6000 /dev/zero; } > "$D/db-20261101-0330.dump"
export FAKE_DUMP=small
run_daily 20261104-0330
unset FAKE_DUMP
check_is "database copies" "$(names 'db-2026????-????.dump')" "db-20261103-0330.dump db-20261104-0330.dump "

echo "daily: uploaded files are in the copy, unchanged ones are stored once"
fresh
check "exit status 0" run_daily 20261104-0330
check "the picture is in the archive" bash -c "tar -tzf '$D/media-20261104-0330.tgz' | grep -qx media/avatars/1.jpg"
inode=$(stat -c %i "$D/media-20261104-0330.tgz")
run_daily 20261105-0330; check_is "exit status" "$?" 0
check_is "same inode" "$(stat -c %i "$D/media-20261105-0330.tgz")" "$inode"
check_is "one media archive" "$(names 'media-*')" "media-20261105-0330.tgz "

echo "daily: media that lost most of its content does not replace the full archive"
fresh
head -c 200000 /dev/urandom > "$W/app/media/big.bin"
run_daily 20261104-0330
rm "$W/app/media/big.bin"
run_daily 20261105-0330; check_is "exit status" "$?" 1
run_daily 20261106-0330; check_is "exit status next day" "$?" 1
check_is "full and newest" "$(names 'media-*')" "media-20261104-0330.tgz media-20261106-0330.tgz "
OLYMP_ACCEPT_SHRINK=1 run_daily 20261107-0330; check_is "accepted by hand" "$?" 0
check_is "only the newest" "$(names 'media-*')" "media-20261107-0330.tgz "

echo "daily: an emptied or missing media folder keeps the old archives"
for gone in "$W/app/media/avatars" "$W/app/media"; do
    fresh
    rm -rf "$gone"
    run_daily 20261104-0330; check_is "exit status" "$?" 1
    check_is "old media archives kept" "$(find "$D" -name 'media-*' | wc -l)" 3
    check "error in the log" grep -q 'ERROR: media' "$W/log"
    check_is "database still rotated" "$(names 'db-2026????-????.dump')" "db-20261104-0330.dump "
done

echo "daily: a site without uploaded files is not an error"
fresh
rm -rf "$W/app/media/avatars" "$D"/media-*
run_daily 20261104-0330; check_is "exit status" "$?" 0
check_is "no media archive" "$(names 'media-*')" ""
check "no .part left" no_parts

# --- deploy backups ----------------------------------------------------------------------------
deploy_fresh() {
    rm -rf "$W/deploy"
    B=$W/deploy
    local s
    for s in 20261101-100000 20261102-100000 20261103-100000; do
        mkdir -p "$B/$s"
        { printf 'PGDMP'; head -c 5000 /dev/zero; } > "$B/$s/database.dump"
        tar -czf "$B/$s/code.tgz" -C "$W/bin" sudo
    done
    mkdir -p "$B/20261026-predeploy" "$B/20261104-100000-manual" "$B/20261105-100000"
}
dirs() { find "$B" -mindepth 1 -maxdepth 1 -printf '%f\n' | sort | tr '\n' ' '; }
ALL="20261026-predeploy 20261101-100000 20261102-100000 20261103-100000 20261104-100000-manual 20261105-100000 "

echo "deploy: only the kept backup stays; manual and newer folders are not touched"
deploy_fresh
check "dry run succeeds" env OLYMP_PRUNE_DRY_RUN=1 bash "$PRUNE" "$B" "$B/20261103-100000"
check_is "dry run removes nothing" "$(dirs)" "$ALL"
check "exit status 0" bash "$PRUNE" "$B" "$B/20261103-100000"
check_is "folders" "$(dirs)" "20261026-predeploy 20261103-100000 20261104-100000-manual 20261105-100000 "

for broken in dump nodump notables code manual outside; do
    echo "deploy: kept backup '$broken' removes nothing"
    deploy_fresh
    keep=$B/20261103-100000
    case "$broken" in
        dump) printf 'PGDMP BROKEN' > "$keep/database.dump" ;;
        nodump) : > "$keep/database.dump" ;;
        notables) printf 'PGDMP NOTABLES' > "$keep/database.dump" ;;
        code) echo junk > "$keep/code.tgz" ;;
        manual) keep=$B/20261026-predeploy ;;
        outside) keep=$W/bin ;;
    esac
    check "exit status 1" bash -c "! bash '$PRUNE' '$B' '$keep'"
    check_is "folders" "$(dirs)" "$ALL"
done

echo "deploy: a much smaller database dump does not remove the last big one"
deploy_fresh
{ printf 'PGDMP'; head -c 20000 /dev/zero; } > "$B/20261102-100000/database.dump"
check "exit status 0" bash "$PRUNE" "$B" "$B/20261103-100000"
check_is "folders" "$(dirs)" "20261026-predeploy 20261102-100000 20261103-100000 20261104-100000-manual 20261105-100000 "
check "dry run with the same rule" env OLYMP_PRUNE_DRY_RUN=1 bash "$PRUNE" "$B" "$B/20261103-100000"

echo
if [ "$failures" = 0 ]; then echo "All backup tests passed."; else echo "$failures check(s) failed."; exit 1; fi
