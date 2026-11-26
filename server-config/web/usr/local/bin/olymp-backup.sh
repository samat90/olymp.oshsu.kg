#!/bin/sh
# Daily dump of the olymp database, problem data and Redis (visit statistics live only there); keeps 14 days.
set -e
umask 077
D=${OLYMP_BACKUP_DIR:-/var/backups/olymp/daily}
APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
KEEP_DAYS=14
mkdir -p "$D"
T=$(date +%Y%m%d-%H%M)
sudo -u postgres pg_dump -Fc olymp_oshsu > "$D/db-$T.dump"

# Problem data rarely changes: an archive equal to the previous one is stored as a hard link to it,
# so every day still has its own file name but the 1.6 GB are on disk once.
previous=$(ls -1 "$D"/problems-*.tgz 2>/dev/null | tail -n 1)
new="$D/problems-$T.tgz"
tar -czf "$new.part" -C "$APP" problems
if [ -n "$previous" ] && cmp -s "$previous" "$new.part" && ln "$previous" "$new"; then
    rm "$new.part"
else
    mv "$new.part" "$new"
fi

# Age is taken from the date in the name: hard links share one modification time.
limit=$(date -d "$KEEP_DAYS days ago" +%Y%m%d)
for f in "$D"/db-*.dump "$D"/problems-*.tgz "$D"/redis-*.rdb; do
    [ -f "$f" ] || continue
    day=${f##*/}; day=${day#*-}; day=${day%%[-.]*}
    if [ "$day" -lt "$limit" ]; then rm -f "$f"; fi
done

# Last, so that a Redis problem cannot stop the database backup.
if redis-cli save > /dev/null; then cp /var/lib/redis/dump.rdb "$D/redis-$T.rdb"; fi
