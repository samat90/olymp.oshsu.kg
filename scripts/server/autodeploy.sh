#!/bin/bash
# Deploys new commits from GitHub without logging in to the server.
#
# Runs every few minutes from olymp-autodeploy.timer as admin on olymp.oshsu.kg. The server only
# makes outgoing requests to GitHub; nothing is opened to the outside. A new commit on GitHub
# main is deployed when all of these hold:
#   - the commit is signed by a key listed in /etc/olymp/allowed_signers (git SSH signatures);
#   - it continues the deployed history (a rewritten or force-pushed main is refused);
#   - no olympiad is running right now (the deploy waits until it ends);
#   - GitHub Actions has not marked the commit red (a failed CI run skips the commit; "still running" or
#     "GitHub API not reachable" does not hold anything back).
# Then scripts/deploy.sh makes a backup, updates the code, applies migrations and restarts the site.
# If the site does not come back, the old code is restored (the database stays as it is).
#
# Every deploy, rollback and skip is also written as one JSON line to $APP/.deploy-history.jsonl (shown to
# administrators at /<admin>/deploy-status/) and, if GITHUB_STATUS_TOKEN is set in /etc/olymp-monitor.env,
# as a commit status "olymp-deploy" on GitHub.
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
HISTORY=${OLYMP_DEPLOY_HISTORY:-$APP/.deploy-history.jsonl}
GH_REPO=${OLYMP_GH_REPO:-samat90/olymp.oshsu.kg}
GH_API=${OLYMP_GH_API:-https://api.github.com}
BACKUP_ROOT=${OLYMP_BACKUPS:-/var/backups/olymp/deploy}
[ -f /etc/olymp-monitor.env ] && . /etc/olymp-monitor.env

log() { echo "[$(date '+%F %T')] autodeploy: $*"; }
notify() {
    log "$1"
    if [ -n "${TELEGRAM_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT:-}" ]; then
        curl -s -m 15 "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
            --data-urlencode "chat_id=$TELEGRAM_CHAT" --data-urlencode "text=olymp.oshsu.kg: $1" > /dev/null || true
    fi
}

# record RESULT COMMIT SUBJECT SECONDS ERROR: one JSON line into the history file, and a GitHub commit status
# when a token is configured. Never fails the deploy.
record() {
    local result=$1 commit=$2 subject=$3 secs=$4 err=${5:-}
    python3 - "$HISTORY" "$result" "$commit" "$subject" "$secs" "$err" <<'PY' 2>/dev/null || log "WARN: could not write the deploy history"
import json, sys, time
path, result, commit, subject, secs, err = sys.argv[1:7]
row = {'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'commit': commit[:9], 'full_commit': commit,
       'result': result, 'seconds': int(secs or 0), 'subject': subject, 'error': err[-1500:]}
try:
    lines = open(path, encoding='utf-8').read().splitlines()[-199:]
except OSError:
    lines = []
lines.append(json.dumps(row, ensure_ascii=False))
open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
PY
    chmod 644 "$HISTORY" 2>/dev/null || true
    if [ -n "${GITHUB_STATUS_TOKEN:-}" ]; then
        local state=success
        case "$result" in ok) state=success ;; rolled_back|skipped_ci_red|refused) state=failure ;; esac
        local payload
        payload=$(python3 -c 'import json, sys; print(json.dumps({"state": sys.argv[1], "context": "olymp-deploy", "description": sys.argv[2][:140]}))' \
            "$state" "${result}: ${err:-$subject}" 2>/dev/null) || payload=
        if [ -n "$payload" ]; then
            curl -s -m 20 -o /dev/null -X POST -H "Authorization: Bearer $GITHUB_STATUS_TOKEN" \
                -H "Accept: application/vnd.github+json" -d "$payload" \
                "$GH_API/repos/$GH_REPO/statuses/$commit" || true
        fi
    fi
}

# ci_state COMMIT: prints red, green, pending or unknown, from GitHub Actions check runs and commit statuses
# (public repository, no token). Only "red" blocks a deploy; any doubt (API down, rate limit, no CI yet) is "unknown".
# A job that failed without running a single step (account locked for billing, no runners) is not red:
# the code was never tested.
ci_state() {
    python3 - "$GH_API" "$GH_REPO" "$1" <<'PY' 2>/dev/null || echo unknown
import json, sys, urllib.request
api, repo, sha = sys.argv[1:4]
def get(path):
    req = urllib.request.Request(api + path, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'olymp-autodeploy'})
    return json.load(urllib.request.urlopen(req, timeout=20))
try:
    runs = get('/repos/%s/commits/%s/check-runs?per_page=100' % (repo, sha)).get('check_runs')
    try:
        state = get('/repos/%s/commits/%s/status' % (repo, sha)).get('state')
    except Exception:
        state = None
    if runs is None:
        print('unknown'); sys.exit()
    red = state in ('failure', 'error')
    for r in runs:
        if r.get('conclusion') in ('failure', 'timed_out', 'startup_failure'):
            try:
                steps = get('/repos/%s/actions/jobs/%s' % (repo, r['id'])).get('steps') or []
            except Exception:
                steps = []  # cannot tell: do not block
            if any(st.get('conclusion') == 'failure' for st in steps) or r.get('conclusion') == 'timed_out':
                red = True
    if red:
        print('red')
    elif any(r.get('status') != 'completed' for r in runs):
        print('pending')
    elif runs:
        print('green')
    else:
        print('unknown')
except Exception:
    print('unknown')
PY
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
    record refused "$new" "$($G log -1 --format=%s "$new")" 0 "not a continuation of the deployed history"
    touch "$refused"
    exit 1
fi
if ! $G -c gpg.format=ssh -c gpg.ssh.allowedSignersFile="$SIGNERS" verify-commit "$new" 2> "$STATE/verify.txt"; then
    notify "коммит $short не подписан разрешённым ключом, не выкатываю"
    cat "$STATE/verify.txt"
    record refused "$new" "$($G log -1 --format=%s "$new")" 0 "not signed by an allowed key"
    touch "$refused"
    exit 1
fi

running=$(running_olympiads)
if [ -n "$running" ]; then
    log "olympiad running ($running), deploy of $short postponed"
    exit 0
fi

subject=$($G log -1 --format=%s "$new")
ci=$(ci_state "$new")
if [ "$ci" = red ]; then
    # Looked at again every run: re-running the failed CI jobs to green (or a newer commit) lets the deploy through.
    if [ ! -f "$STATE/ci-red-$short" ]; then
        notify "CI для коммита $short красный, не выкатываю (ждём исправления): $subject"
        record skipped_ci_red "$new" "$subject" 0 "GitHub Actions failed for this commit"
        touch "$STATE/ci-red-$short"
    fi
    exit 0
fi
log "CI of $short: $ci"

log "deploying $short: $subject"
# Run copies: deploy.sh replaces the files of the running scripts.
$G show "$new:scripts/deploy.sh" > "$STATE/deploy.sh"
cp "$APP/scripts/rollback.sh" "$STATE/rollback.sh"
$G update-ref refs/heads/main "$new"
deploy_start=$(date +%s)
bash "$STATE/deploy.sh" main 2>&1 | tee "$STATE/deploy-last.log"
rc=${PIPESTATUS[0]}
deploy_secs=$(( $(date +%s) - deploy_start ))
if [ "$rc" = 0 ]; then
    rm -f "$STATE"/failed-"$short" "$STATE/ci-red-$short"
    notify "выкачено $short: $subject"
    record ok "$new" "$subject" "$deploy_secs" ""
else
    # What went wrong, for the history: the last lines of the deploy output (a failed migration says so).
    err=$(tail -n 12 "$STATE/deploy-last.log" | tr -d '\r' | tr '\n' '|')
    backup=$(ls -1d "$BACKUP_ROOT"/*/ | tail -1)
    if grep -q "MIGRATION FAILED" "$STATE/deploy-last.log"; then
        notify "миграции $short не применились, возвращаю прежний код из $backup (упавшая миграция откатилась транзакцией, ранее применённые остались; базу целиком не трогаю)"
    else
        notify "выкат $short не удался, возвращаю прежний код из $backup"
    fi
    $G update-ref refs/heads/main "$current"
    bash "$STATE/rollback.sh" "$backup"
    echo "$current" > "$APP/.deployed-revision"
    record rolled_back "$new" "$subject" "$(( $(date +%s) - deploy_start ))" "$err"
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
