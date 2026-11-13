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

# Keys of the olympiads going on right now. A contest open for longer than OLYMP_LONG_CONTEST_HOURS
# (default 48) is a training or practice contest: it does not hold back updates, otherwise one forgotten
# month-long contest would stop every deploy. If the database cannot be asked, nothing is printed (a
# broken site must still get its fix), only a warning in the log.
running_olympiads() {
    (cd "$APP" && venv/bin/python manage.py shell -c "
from datetime import timedelta
from django.db.models import F
from django.utils import timezone
from judge.models import Contest
now = timezone.now()
qs = Contest.objects.filter(start_time__lte=now, end_time__gt=now,
                            end_time__lte=F('start_time') + timedelta(hours=${OLYMP_LONG_CONTEST_HOURS:-48}))
print(','.join(qs.values_list('key', flat=True)))" 2>/dev/null) || log "WARN: could not check for running olympiads" >&2
}

[ -f "$PAUSED" ] && exit 0
mkdir -p "$STATE"
exec 9> "$STATE/lock"
flock -n 9 || exit 0

G="git --git-dir=$REPO"
# The link into the university network is slow (10-60 KB/s in November 2026) and long downloads are cut
# after about 20 minutes, so keep every push small (scripts/dev/pre-push warns above 5 MB). A bigger push
# is brought in over the university network instead (docs/OBSLUZHIVANIE-2026-11.md, "Большой коммит").
# Give the download its own generous limit, give up when it stalls for 5 minutes, and log how long it took.
fetch_start=$(date +%s)
if ! timeout "${OLYMP_FETCH_TIMEOUT:-7200}" $G -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=300 \
        fetch -q "$REMOTE" "+refs/heads/main:refs/remotes/origin/main"; then
    log "GitHub is not reachable or the download stalled (after $(( $(date +%s) - fetch_start )) s), will retry"
    # An interrupted download leaves its partial pack behind (10-15 MB each time); only this run fetches
    # (flock above), so every leftover is garbage now.
    find "$REPO/objects/pack" -maxdepth 1 -name 'tmp_pack_*' -delete 2>/dev/null
    exit 0
fi
fetch_secs=$(( $(date +%s) - fetch_start ))
[ "$fetch_secs" -gt 60 ] && log "fetch from GitHub took $fetch_secs s"
new=$($G rev-parse refs/remotes/origin/main)
current=$(cat "$APP/.deployed-revision" 2>/dev/null || $G rev-parse main)
if [ "$new" = "$current" ]; then
    # Nothing to deploy: use the quiet time to add new problem sets (only when no olympiad is running,
    # the tests are generated on the judge machine).
    # Files of the judge machine (executors, its systemd units) that waited for a quiet moment.
    bash "$APP/scripts/server/sync_judge.sh" 2>&1 | grep -v "no SSH access" || true
    pending=0
    for set in ${OLYMP_PROBLEMSETS:-olymp2026 train2026}; do
        [ -d "$APP/problemsets/$set" ] && [ ! -f "/home/admin/problemsets/$set.done" ] && pending=1
    done
    if [ "$pending" = 1 ]; then
        busy=$(running_olympiads 2>/dev/null)
        if [ -z "$busy" ]; then
            bash "$APP/scripts/server/import_problemsets.sh" ${OLYMP_PROBLEMSETS:-olymp2026 train2026}
        fi
    fi
    exit 0
fi

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

running=$(running_olympiads)
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
    # A failure can be passing (the slow link broke a download): try the same commit up to 3 times,
    # then wait for a new commit.
    tries=$(( $(cat "$STATE/failed-$short" 2>/dev/null || echo 0) + 1 ))
    echo "$tries" > "$STATE/failed-$short"
    if [ "$tries" -ge "${OLYMP_DEPLOY_TRIES:-3}" ]; then
        notify "коммит $short не выкатился $tries раза, жду нового коммита"
        touch "$refused"
    fi
    exit 1
fi
