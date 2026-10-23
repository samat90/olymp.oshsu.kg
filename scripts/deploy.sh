#!/bin/bash
# Deploys a git revision to olymp.oshsu.kg. Runs on the web server as admin.
#
#   scripts/deploy.sh [ref]          # default ref: main
#
# Called by the git hook in /home/admin/olymp.git (see docs/DEPLOY-2026-10.md),
# or by hand. Every run first makes a backup; scripts/rollback.sh restores it.
set -euo pipefail

APP=/var/www/olymp.oshsu.kg
REPO=${OLYMP_REPO:-/home/admin/olymp.git}
REF=${1:-main}
STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_ROOT=/var/backups/olymp/deploy
BACKUP=$BACKUP_ROOT/$STAMP
PY=$APP/venv/bin/python
SERVICES="olymp-web olymp-bridge"

log() { echo "[$(date +%H:%M:%S)] $*"; }

log "Deploying $REF"
mkdir -p "$BACKUP"

log "Backup: database"
pg_dump -Fc olymp_oshsu > "$BACKUP/database.dump"

log "Backup: code"
tar czf "$BACKUP/code.tgz" -C "$APP" \
    --exclude=./venv --exclude=./problems --exclude=./media --exclude=./static \
    --exclude=./resources/vendor --exclude='*.pyc' .
git --git-dir="$REPO" rev-parse "$REF" > "$BACKUP/revision"
if [ -f "$APP/.deployed-revision" ]; then
    cp "$APP/.deployed-revision" "$BACKUP/previous-revision"
fi

log "Checkout"
git --git-dir="$REPO" --work-tree="$APP" checkout -f "$REF" -- .
git --git-dir="$REPO" rev-parse "$REF" > "$APP/.deployed-revision"

cd "$APP"

log "Python packages"
"$APP/venv/bin/pip" install -q -r requirements.txt

log "Front-end libraries"
bash scripts/fetch_vendor.sh

log "Database migrations"
"$PY" manage.py migrate --noinput

log "Translations"
"$PY" - <<'PYEOF'
import os
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
for lang in ('ru', 'en', 'ky'):
    for name in ('django.po', 'djangojs.po', 'dmoj-user.po'):
        path = os.path.join('locale', lang, 'LC_MESSAGES', name)
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                catalog = read_po(f)
            with open(path[:-3] + '.mo', 'wb') as f:
                write_mo(f, catalog)
PYEOF

if command -v sass >/dev/null 2>&1 && command -v postcss >/dev/null 2>&1; then
    log "Stylesheets"
    sh make_style.sh
fi

log "Static files"
"$PY" manage.py collectstatic --noinput -v 0
"$PY" manage.py compilejsi18n -v 0 || true

log "Restart"
sudo systemctl restart $SERVICES

log "Health check"
for i in $(seq 1 30); do
    code=$(curl -s -o /dev/null -w '%{http_code}' -H 'Host: olymp.oshsu.kg' http://127.0.0.1:8000/ || true)
    if [ "$code" = "200" ]; then
        log "OK: site answers 200. Backup: $BACKUP"
        exit 0
    fi
    sleep 2
done

log "The site does not answer after the deploy (last code: $code)."
log "Roll back with: scripts/rollback.sh $BACKUP"
exit 1
