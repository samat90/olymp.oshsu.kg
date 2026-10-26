#!/bin/bash
# Deploys new commits from GitHub without logging in to the server.
#
# Runs every few minutes from olymp-autodeploy.timer as admin on olymp.oshsu.kg. The server only
# makes outgoing requests to GitHub; nothing is opened to the outside. A new commit on GitHub
# main is deployed when all of these hold:
#   - the commit is signed by a key listed in /etc/olymp/allowed_signers (git SSH signatures);
#   - it continues the deployed history (a rewritten or force-pushed main is refused);
#   - no olympiad is running right now (the deploy waits until it ends).
# Then scripts/deploy.sh makes a backup, updates the code, applies migrations and restarts the site.
# If the site does not come back, the old code is restored (the database stays as it is).
#
# Log: /var/log/olymp/deploy.log. Telegram (optional): /etc/olymp-monitor.env, as healthcheck.sh.
# Deploy by hand now:  sudo systemctl start olymp-autodeploy
# Pause auto-deploy:   sudo touch /etc/olymp/autodeploy.paused
set -uo pipefail

APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
REPO=${OLYMP_REPO:-/home/admin/olymp.git}
REMOTE=${OLYMP_REMOTE:-https://github.com/samat90/olymp.oshsu.kg.git}
SIGNERS=${OLYMP_SIGNERS:-/etc/olymp/allowed_signers}
PAUSED=${OLYMP_PAUSED:-/etc/olymp/autodeploy.paused}
STATE=${OLYMP_AUTODEPLOY_STATE:-/home/admin/.autodeploy}
[ -f /etc/olymp-monitor.env ] && . /etc/olymp-monitor.env

log() { echo "[$(date '+%F %T')] autodeploy: $*"; }
notify() {
    log "$1"
    if [ -n "${TELEGRAM_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT:-}" ]; then
        curl -s -m 15 "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
            --data-urlencode "chat_id=$TELEGRAM_CHAT" --data-urlencode "text=olymp.oshsu.kg: $1" > /dev/null || true
    fi
}

[ -f "$PAUSED" ] && exit 0
mkdir -p "$STATE"
exec 9> "$STATE/lock"
flock -n 9 || exit 0

G="git --git-dir=$REPO"
$G fetch -q "$REMOTE" "+refs/heads/main:refs/remotes/origin/main" || { log "GitHub is not reachable"; exit 0; }
new=$($G rev-parse refs/remotes/origin/main)
current=$(cat "$APP/.deployed-revision" 2>/dev/null || $G rev-parse main)
[ "$new" = "$current" ] && exit 0

short=${new:0:9}
refused="$STATE/refused-$short"
[ -f "$refused" ] && exit 0  # already reported

if ! $G merge-base --is-ancestor "$current" "$new"; then
    notify "коммит $short не продолжает выкаченную историю (main переписан?), не выкатываю"
    touch "$refused"
    exit 1
fi
if ! $G -c gpg.format=ssh -c gpg.ssh.allowedSignersFile="$SIGNERS" verify-commit "$new" 2> "$STATE/verify.txt"; then
    notify "коммит $short не подписан разрешённым ключом, не выкатываю"
    cat "$STATE/verify.txt"
    touch "$refused"
    exit 1
fi

running=$(cd "$APP" && venv/bin/python manage.py shell -c "
from django.utils import timezone
from judge.models import Contest
now = timezone.now()
print(','.join(Contest.objects.filter(start_time__lte=now, end_time__gt=now).values_list('key', flat=True)))" 2>/dev/null)
if [ -n "$running" ]; then
    log "olympiad running ($running), deploy of $short postponed"
    exit 0
fi

subject=$($G log -1 --format=%s "$new")
log "deploying $short: $subject"
# Run copies: deploy.sh replaces the files of the running scripts.
$G show "$new:scripts/deploy.sh" > "$STATE/deploy.sh"
cp "$APP/scripts/rollback.sh" "$STATE/rollback.sh"
$G update-ref refs/heads/main "$new"
if bash "$STATE/deploy.sh" main; then
    notify "выкачено $short: $subject"
else
    backup=$(ls -1d /var/backups/olymp/deploy/*/ | tail -1)
    notify "выкат $short не удался, возвращаю прежний код из $backup"
    $G update-ref refs/heads/main "$current"
    bash "$STATE/rollback.sh" "$backup"
    echo "$current" > "$APP/.deployed-revision"
    touch "$refused"
    exit 1
fi
