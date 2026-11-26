#!/bin/bash
# Daily backup of olymp.oshsu.kg: the database, the problem data and Redis (visit statistics live only there).
# Only the latest good copy of each stays on the server.
#
# A new copy is written to a *.part file and checked. It gets its final name only when the check passes, and
# only when it is on the disk are the older copies of that kind removed. When a new copy has lost much of
# its content (see "shrunk" below), the last good one stays beside it. When making or checking a copy
# fails, the older one stays, the log gets an "ERROR:" line and the script exits with 1. Only files named exactly
# db-YYYYMMDD-HHMM.dump, problems-YYYYMMDD-HHMM.tgz and redis-YYYYMMDD-HHMM.rdb are ever removed; copies
# made by hand live in other folders or under other names.
#
# Nothing here repeats what is in git or can be rebuilt (code, static files, packages, caches): the copy is
# the database dump, problems/ and the Redis file. Restore: docs/OBSLUZHIVANIE-2026-11.md.
set -uo pipefail
shopt -s nullglob
umask 077

D=${OLYMP_BACKUP_DIR:-/var/backups/olymp/daily}
APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
RDB=${OLYMP_REDIS_RDB:-/var/lib/redis/dump.rdb}
ACCEPT_SHRINK=${OLYMP_ACCEPT_SHRINK:-0}
MIN_DB_BYTES=${OLYMP_MIN_DB_BYTES:-1000000}   # the compressed dump was 5.4 MB in November 2026
T=${OLYMP_BACKUP_STAMP:-$(date +%Y%m%d-%H%M)}
status=0

log() { echo "[$(date '+%F %T')] backup: $*"; }
error() { log "ERROR: $*"; status=1; }

# copies KIND EXT: sets COPIES to the finished copies of one kind, oldest first.
copies() {
    COPIES=("$D/$1"-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]."$2")
}

# prune KIND EXT KEEP...: removes every finished copy of one kind except the listed ones.
prune() {
    local kind=$1 ext=$2 f k
    shift 2
    copies "$kind" "$ext"
    for f in "${COPIES[@]}"; do
        for k in "$@"; do
            [ "$f" = "$k" ] && continue 2
        done
        rm -f -- "$f" && log "removed the older copy ${f##*/}"
    done
}

# on_disk: the new copy and its name must be on the disk before anything older is removed.
on_disk() { sync -f "$D"; }

# shrunk WHAT KIND EXT NEW GOOD: a copy that lost much of its content does not replace the last good one.
shrunk() {
    local what=$1 kind=$2 ext=$3 new=$4 good=$5
    on_disk && prune "$kind" "$ext" "$good" "$new"
    error "$what, ${good##*/} is kept. Check the site; if the new copy is right, run: sudo OLYMP_ACCEPT_SHRINK=1 $0"
}

# save_sized WHAT KIND EXT PART NEW: gives a checked copy its name and removes the older ones. A copy less
# than half the size of the biggest older one counts as shrunk; the latest older copy of normal size stays.
save_sized() {
    local what=$1 kind=$2 ext=$3 part=$4 new=$5 size f s biggest=0 good=
    size=$(stat -c %s "$part")
    copies "$kind" "$ext"
    for f in "${COPIES[@]}"; do
        s=$(stat -c %s "$f")
        [ "$s" -gt "$biggest" ] && biggest=$s
    done
    for f in "${COPIES[@]}"; do   # oldest first: the last match is the latest
        [ $(($(stat -c %s "$f") * 2)) -ge "$biggest" ] && good=$f
    done
    if [ -n "$good" ] && [ $((size * 2)) -lt "$biggest" ] && [ "$ACCEPT_SHRINK" != 1 ]; then
        if [ "$good" = "$new" ] || ! mv -f "$part" "$new"; then
            rm -f "$part"; error "$what: the new copy ($size bytes) is less than half of the older one, which is kept"
            return 1
        fi
        shrunk "$what: the new copy ($size bytes) is less than half of the older one ($biggest bytes)" \
            "$kind" "$ext" "$new" "$good"
        return 1
    fi
    if ! mv -f "$part" "$new"; then
        rm -f "$part"; error "$what: could not save ${new##*/}, the older copy is kept"; return 1
    fi
    if ! on_disk; then
        error "$what: ${new##*/} could not be flushed to the disk, the older copy is kept"; return 1
    fi
    log "$what: ${new##*/}, $size bytes, checked"
    prune "$kind" "$ext" "$new"
}

backup_database() {
    local new=$D/db-$T.dump part=$D/db-$T.dump.part size toc
    # The redirect is meant to be done by root: the backup folder is closed to the postgres user.
    # shellcheck disable=SC2024
    if ! sudo -u postgres pg_dump -Fc olymp_oshsu > "$part"; then
        rm -f "$part"; error "database: pg_dump failed, the older copy is kept"; return
    fi
    size=$(stat -c %s "$part")
    if [ "$size" -lt "$MIN_DB_BYTES" ]; then
        rm -f "$part"; error "database: the dump has only $size bytes, the older copy is kept"; return
    fi
    # "-f /dev/null" reads and unpacks the whole archive (a list of contents alone would not notice a
    # truncated file); the users table shows that this is the site's database and not an empty one.
    if ! pg_restore -f /dev/null "$part" || ! toc=$(pg_restore -l "$part") ||
            [[ $toc != *"TABLE DATA public auth_user "* ]]; then
        rm -f "$part"; error "database: the new dump cannot be read or has no site data, the older copy is kept"; return
    fi

    save_sized database db dump "$part" "$new"
}

backup_problems() {
    local new=$D/problems-$T.tgz part=$D/problems-$T.tgz.part expected list found previous
    if [ -L "$APP/problems" ]; then
        error "problems: $APP/problems is a link, only the link would be saved; the older copy is kept"; return
    fi
    expected=$(find "$APP/problems" ! -type d 2>/dev/null | wc -l)
    if [ "$expected" -eq 0 ]; then
        error "problems: no files in $APP/problems, the older copy is kept"; return
    fi
    if ! tar --sort=name -czf "$part" -C "$APP" problems; then
        rm -f "$part"; error "problems: tar failed, the older copy is kept"; return
    fi
    # Listing the whole archive unpacks all of it, so a damaged file does not pass.
    if ! list=$(tar -tzf "$part"); then
        rm -f "$part"; error "problems: the new archive cannot be read, the older copy is kept"; return
    fi
    found=$(grep -vc '/$' <<< "$list")
    if [ "$found" -lt "$expected" ]; then
        rm -f "$part"; error "problems: the archive has $found files of $expected, the older copy is kept"; return
    fi

    # Problem data rarely changes: an archive equal to the previous one becomes a second name of the same
    # file, so the 1.6 GB are never stored twice. The older name is removed right after.
    copies problems tgz
    previous=
    [ ${#COPIES[@]} -gt 0 ] && previous=${COPIES[${#COPIES[@]} - 1]}
    if [ -n "$previous" ] && [ "$previous" != "$new" ] && cmp -s "$previous" "$part" &&
            ln "$previous" "$part.link" 2>/dev/null; then
        mv -f "$part.link" "$part"
    fi
    log "problems: $found files in the new archive"
    # The file time is the time of this backup: the copy on the judge is removed by age.
    save_sized problems problems tgz "$part" "$new" && touch "$new"
}

# visit_keys: how many visit statistics keys (judge/utils/visit_stats.py) Redis holds, in any database.
visit_keys() {
    local db total=0
    for db in 0 1 2 3; do
        total=$((total + $(redis-cli -n "$db" --scan --pattern 'olst:*' 2>/dev/null | grep -c '^olst:')))
    done
    echo "$total"
}

backup_redis() {
    local new=$D/redis-$T.rdb part=$D/redis-$T.rdb.part reply keys
    # "<keys> <file>": the visit statistics in the last good copy. The size of the file says nothing here,
    # it also holds the cache, which every deploy clears.
    local note=$D/redis-visit-keys old_keys=0 good=
    reply=$(redis-cli save 2>&1)
    if [ "$reply" != OK ]; then
        error "redis: save failed ($reply), the older copy is kept"; return
    fi
    if ! cp "$RDB" "$part" || [ "$(head -c 5 "$part")" != REDIS ] ||
            { command -v redis-check-rdb > /dev/null && ! redis-check-rdb "$part" > /dev/null 2>&1; }; then
        rm -f "$part"; error "redis: the copy is missing or damaged, the older copy is kept"; return
    fi
    keys=$(visit_keys)
    if [ -f "$note" ]; then
        read -r old_keys good < "$note"
        good=$D/$good
    fi
    if [ -f "$good" ] && [ "$good" != "$new" ] && [ $((keys * 2)) -lt "$old_keys" ] && [ "$ACCEPT_SHRINK" != 1 ]; then
        if ! mv -f "$part" "$new"; then
            rm -f "$part"; error "redis: could not save ${new##*/}, the older copy is kept"; return
        fi
        shrunk "redis: only $keys visit statistics keys, there were $old_keys" redis rdb "$new" "$good"
        return
    fi
    if ! mv -f "$part" "$new"; then
        rm -f "$part"; error "redis: could not save ${new##*/}, the older copy is kept"; return
    fi
    if ! on_disk; then
        error "redis: ${new##*/} could not be flushed to the disk, the older copy is kept"; return
    fi
    echo "$keys ${new##*/}" > "$note"
    log "redis: ${new##*/}, $keys visit statistics keys, checked"
    prune redis rdb "$new"
}

mkdir -p "$D" || exit 1
if command -v flock > /dev/null; then
    exec 9< "$D"
    flock -n 9 || { log "another backup is running"; exit 1; }
fi
rm -f -- "$D"/db-*.dump.part "$D"/problems-*.tgz.part "$D"/problems-*.tgz.part.link "$D"/redis-*.rdb.part   # interrupted runs

# Independent of each other: a problem with one kind does not stop the others.
backup_database
backup_problems
backup_redis

if [ "$status" = 0 ]; then log "done"; else log "finished with errors"; fi
exit "$status"
