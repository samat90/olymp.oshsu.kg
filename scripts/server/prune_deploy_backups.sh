#!/bin/bash
# Keeps only one deploy backup (made by scripts/deploy.sh) for rollback.
#
#   scripts/server/prune_deploy_backups.sh /var/backups/olymp/deploy /var/backups/olymp/deploy/<stamp>
#
# The backup to keep is checked first; when it is not complete, nothing is removed. Only folders named
# exactly YYYYMMDD-HHMMSS and older than the kept one are removed: copies made by hand and a newer backup
# (of another deploy that may be running) stay. OLYMP_PRUNE_DRY_RUN=1 only shows what would be removed.
set -uo pipefail
shopt -s nullglob

ROOT=${1:?usage: prune_deploy_backups.sh BACKUP_ROOT KEEP_DIR}
KEEP=${2:?usage: prune_deploy_backups.sh BACKUP_ROOT KEEP_DIR}
ROOT=${ROOT%/}
KEEP=${KEEP%/}
name=${KEEP##*/}

log() { echo "[$(date +%H:%M:%S)] deploy backups: $*"; }
refuse() { log "ERROR: $*; the older backups are kept"; exit 1; }

[[ $name =~ ^[0-9]{8}-[0-9]{6}$ && $KEEP = "$ROOT/$name" ]] || refuse "$KEEP is not a deploy backup in $ROOT"
if [ ! -s "$KEEP/database.dump" ] || ! pg_restore -f /dev/null "$KEEP/database.dump"; then
    refuse "$KEEP/database.dump is missing or cannot be read"
fi
if [ ! -s "$KEEP/code.tgz" ] || ! tar -tzf "$KEEP/code.tgz" > /dev/null; then
    refuse "$KEEP/code.tgz is missing or damaged"
fi

toc=$(pg_restore -l "$KEEP/database.dump")
[[ $toc = *"TABLE DATA public auth_user "* ]] || refuse "$KEEP/database.dump has no site data"
# The new backup must be on the disk before an older one goes.
sync -f "$KEEP" || refuse "$KEEP could not be flushed to the disk"

# A database that suddenly lost much of its data: the latest big dump stays as well.
dump_size() { stat -c %s "$1/database.dump" 2>/dev/null || echo 0; }
older=()
biggest=0
for dir in "$ROOT"/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]; do
    if [ -d "$dir" ] && [ ! -L "$dir" ] && [[ ${dir##*/} < $name ]]; then
        older+=("$dir")
        size=$(dump_size "$dir")
        [ "$size" -gt "$biggest" ] && biggest=$size
    fi
done
spare=
if [ $(($(dump_size "$KEEP") * 2)) -lt "$biggest" ]; then
    for dir in "${older[@]}"; do   # oldest first: the last match is the latest
        [ $(($(dump_size "$dir") * 2)) -ge "$biggest" ] && spare=$dir
    done
    log "WARNING: the new database dump is less than half of an older one, ${spare##*/} is kept too"
fi

status=0
for dir in "${older[@]}"; do
    old=${dir##*/}
    [ "$dir" = "$spare" ] && continue
    if [ "${OLYMP_PRUNE_DRY_RUN:-0}" = 1 ]; then
        log "would remove $old"
    elif rm -rf -- "$dir"; then
        log "removed $old"
    else
        log "could not remove $old"; status=1
    fi
done
log "kept for rollback: $name"
exit $status
