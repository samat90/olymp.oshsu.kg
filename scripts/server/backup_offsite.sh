#!/bin/bash
# Copy the daily database backups of olymp.oshsu.kg to the judge machine, so a dead disk on
# the web machine does not take the backups with it. Run from cron after olymp-backup.sh.
#   /etc/cron.d/olymp-backup-offsite:
#   15 4 * * * root /var/www/olymp.oshsu.kg/scripts/server/backup_offsite.sh >> /var/log/olymp/backup-offsite.log 2>&1
set -euo pipefail

SRC=${OLYMP_BACKUPS:-/var/backups/olymp/daily}
DEST=${OLYMP_BACKUP_DEST:-admin@10.10.8.227:/home/admin/olymp-backups/daily}
KEY=${OLYMP_BACKUP_KEY:-/root/.ssh/olymp_backup}

echo "[$(date '+%F %T')] copying $SRC to $DEST"
SSH="ssh -i $KEY -o BatchMode=yes -o StrictHostKeyChecking=accept-new"
# No --delete: if the web machine loses its backups, the copies on the judge must survive.
rsync -a -e "$SSH" "$SRC/" "$DEST/"
# Copies older than 30 days are removed on the judge side.
$SSH "${DEST%%:*}" "find '${DEST#*:}' -mindepth 1 -maxdepth 1 -mtime +30 -exec rm -rf {} +"
echo "[$(date '+%F %T')] done: $(ls -1 "$SRC" | wc -l) item(s)"
