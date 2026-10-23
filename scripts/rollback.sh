#!/bin/bash
# Restores code (and, with --database, the database) from a backup made by scripts/deploy.sh.
#
#   scripts/rollback.sh /var/backups/olymp/deploy/20261101-120000             # code only
#   scripts/rollback.sh /var/backups/olymp/deploy/20261101-120000 --database  # code and database
#
# Restoring the database loses everything written after the backup (submissions, users),
# so use --database only when the migration itself broke the site.
set -euo pipefail

BACKUP=${1:?usage: rollback.sh BACKUP_DIR [--database]}
APP=/var/www/olymp.oshsu.kg

[ -f "$BACKUP/code.tgz" ] || { echo "No code.tgz in $BACKUP"; exit 1; }

echo "Restoring code from $BACKUP"
tar xzf "$BACKUP/code.tgz" -C "$APP"
if [ -f "$BACKUP/previous-revision" ]; then
    cp "$BACKUP/previous-revision" "$APP/.deployed-revision"
fi

if [ "${2:-}" = "--database" ]; then
    echo "Restoring the database"
    sudo systemctl stop olymp-web olymp-bridge
    sudo -u postgres pg_restore --clean --if-exists -d olymp_oshsu < "$BACKUP/database.dump"
fi

cd "$APP"
venv/bin/python manage.py collectstatic --noinput -v 0
sudo systemctl restart olymp-web olymp-bridge
echo "Done. Check https://olymp.oshsu.kg/"
