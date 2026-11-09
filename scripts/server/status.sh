#!/bin/bash
# Read-only report of one machine: what runs, what is broken, what waits. Changes nothing.
# Use it before maintenance, after a reboot, or whenever something looks wrong.
#
#   sudo bash scripts/server/status.sh web       # on olymp.oshsu.kg
#   sudo bash /tmp/olymp/status.sh judge         # on judge.oshsu.kg
#
# Lines start with OK, WARN or INFO; the last line counts the WARNs.
set -u
ROLE=${1:-web}
APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
REPO=${OLYMP_REPO:-/home/admin/olymp.git}
warn=0
ok() { echo "OK    $*"; }
bad() { echo "WARN  $*"; warn=$((warn + 1)); }
info() { echo "INFO  $*"; }
active() { systemctl is-active --quiet "$1"; }
as_admin() { if [ "$(id -u)" = 0 ]; then runuser -u admin -- "$@"; else "$@"; fi; }

echo "== $(hostname) ($ROLE), $(date '+%F %T %Z'), up $(uptime -p 2>/dev/null)"
info "load: $(cut -d' ' -f1-3 /proc/loadavg), cores: $(nproc), memory free: $(free -m | awk '/Mem:/ {print $7}') MB of $(free -m | awk '/Mem:/ {print $2}') MB"
use=$(df -P / | awk 'NR==2 {gsub("%", "", $5); print $5}')
if [ "$use" -ge 85 ]; then bad "disk / is ${use}% full"; else ok "disk / is ${use}% full ($(df -h / | awk 'NR==2 {print $4}') free)"; fi
if [ -f /var/run/reboot-required ]; then info "a reboot is pending (system updates): $(tr '\n' ' ' < /var/run/reboot-required.pkgs 2>/dev/null | cut -c1-120)"; fi
failed=$(systemctl list-units --failed --plain --no-legend 2>/dev/null | awk '{print $1}' | tr '\n' ' ')
if [ -n "$failed" ]; then bad "failed systemd units: $failed"; else ok "no failed systemd units"; fi
if as_admin sudo -n true 2>/dev/null; then ok "admin has sudo without a password"; else info "admin has no full sudo without a password (sync_system.sh / sync_judge.sh need it)"; fi

if [ "$ROLE" = web ]; then
    for s in nginx postgresql redis-server olymp-web olymp-bridge; do
        if active "$s"; then ok "service $s is running"; else bad "service $s is NOT running"; fi
    done
    for t in olymp-autodeploy.timer olymp-publish-problems.timer; do
        if active "$t"; then ok "timer $t is on (next: $(systemctl show "$t" -p NextElapseUSecRealtime --value 2>/dev/null))"; else bad "timer $t is off"; fi
    done
    for c in /etc/cron.d/olymp-*; do [ -f "$c" ] && info "cron: $(basename "$c"): $(grep -v '^#' "$c" | grep -v '^$' | head -1 | cut -c1-110)"; done
    [ -f /etc/olymp/autodeploy.paused ] && bad "auto-deploy is PAUSED (/etc/olymp/autodeploy.paused)"

    code=$(curl -s -o /dev/null -m 15 -w '%{http_code}' -H 'Host: olymp.oshsu.kg' http://127.0.0.1:8000/)
    [ "$code" = 200 ] && ok "site answers 200 (gunicorn)" || bad "site answers $code (gunicorn)"
    code=$(curl -s -o /dev/null -m 15 -w '%{http_code}' -H 'Host: olymp.oshsu.kg' http://127.0.0.1/)
    [ "$code" = 200 ] && ok "site answers 200 (nginx)" || bad "site answers $code (nginx)"
    rh=$(curl -s -m 8 http://10.10.8.227:9910/health)
    echo "$rh" | grep -q '"ok": *true' && ok "code runner on the judge: $rh" || bad "code runner does not answer: ${rh:-no answer}"

    deployed=$(cat "$APP/.deployed-revision" 2>/dev/null)
    remote=$(as_admin git --git-dir="$REPO" rev-parse refs/remotes/origin/main 2>/dev/null)
    if [ "$deployed" = "$remote" ]; then ok "deployed = last fetched GitHub main (${deployed:0:9})"
    else bad "deployed ${deployed:0:9}, but GitHub main (last fetch) is ${remote:0:9}: $(as_admin git --git-dir="$REPO" log --oneline -1 "$remote" 2>/dev/null | cut -c1-80)"; fi
    for f in /home/admin/.autodeploy/refused-* /home/admin/.autodeploy/failed-*; do [ -f "$f" ] && info "auto-deploy marker: $(basename "$f")"; done
    pending_packs=$(find "$REPO/objects" -name 'tmp_*' 2>/dev/null | wc -l)
    [ "$pending_packs" -gt 0 ] && info "$pending_packs unfinished download(s) from GitHub in the repository (an interrupted fetch)"
    echo "---- last lines of /var/log/olymp/deploy.log"
    tail -n 25 /var/log/olymp/deploy.log 2>/dev/null | sed 's/^/    /'
    echo "----"
    for m in /home/admin/problemsets/*.done /home/admin/problemsets/*.failed; do [ -f "$m" ] && info "problem sets: $(basename "$m")"; done

    (cd "$APP" && as_admin venv/bin/python manage.py shell -c "
from datetime import timedelta
from django.utils import timezone
from judge.models import Contest, Judge, Problem, Submission
now = timezone.now()
print('INFO  judges online: ' + ', '.join(Judge.objects.filter(online=True).values_list('name', flat=True)))
print('INFO  problems: %d, public: %d' % (Problem.objects.count(), Problem.objects.filter(is_public=True).count()))
stuck = Submission.objects.filter(status__in=('QU', 'P', 'G'), date__lt=now - timedelta(minutes=10)).count()
print(('WARN  ' if stuck else 'OK    ') + 'submissions waiting longer than 10 min: %d' % stuck)
for c in Contest.objects.filter(start_time__lte=now, end_time__gt=now):
    print('INFO  contest running now: %s (%s .. %s)' % (c.key, c.start_time, c.end_time))
try:
    from judge.models import Quiz
    print('INFO  quizzes: %d' % Quiz.objects.count())
except Exception:
    pass
" 2>&1 | grep -E '^(OK|WARN|INFO)') || bad "Django shell does not start"
    [ "$(cd "$APP" && as_admin venv/bin/python manage.py shell -c "from judge.models import Judge; print(Judge.objects.filter(online=True).count())" 2>/dev/null)" -ge 1 ] 2>/dev/null \
        || bad "no judge is online"
    if [ -x "$APP/scripts/server/sync_system.sh" ] || [ -f "$APP/scripts/server/sync_system.sh" ]; then
        d=$(as_admin bash "$APP/scripts/server/sync_system.sh" --check 2>/dev/null | grep -c '^differs')
        [ "$d" -gt 0 ] && info "$d server setting file(s) differ from git (bash scripts/server/sync_system.sh --check)"
    fi
    info "backups: daily $(ls -1 /var/backups/olymp/daily 2>/dev/null | wc -l) item(s), deploy $(ls -1d /var/backups/olymp/deploy/*/ 2>/dev/null | wc -l), sizes: $(du -sh /var/backups/olymp 2>/dev/null | cut -f1)"
    info "logs /var/log/olymp: $(du -sh /var/log/olymp 2>/dev/null | cut -f1); journal: $(journalctl --disk-usage 2>/dev/null | grep -o '[0-9.]*[KMG]' | head -1)"
fi

if [ "$ROLE" = judge ]; then
    units=$(systemctl list-units --plain --no-legend 'olymp-judge*.service' | awk '{print $1}')
    for u in $units olymp-runner.service; do
        if active "$u"; then ok "service $u is running"; else bad "service $u is NOT running"; fi
    done
    if active olymp-runner-firewall.service; then ok "olymp-runner-firewall is on"; else info "olymp-runner-firewall is not active"; fi
    rh=$(curl -s -m 8 http://127.0.0.1:9910/health)
    echo "$rh" | grep -q '"ok": *true' && ok "code runner: $rh" || bad "code runner does not answer: ${rh:-no answer}"
    if timeout 5 bash -c 'echo > /dev/tcp/10.10.8.226/9999' 2>/dev/null; then ok "judge bridge on the site (10.10.8.226:9999) is reachable"; else bad "cannot reach the judge bridge 10.10.8.226:9999"; fi
    info "judge files version: $(cat /home/admin/.olymp-judge-version 2>/dev/null || echo 'not set yet')"
    info "problem-set builds: $(du -sh /home/admin/problemsets-build 2>/dev/null | cut -f1 || echo none); running builds: $(pgrep -fc 'build.py' 2>/dev/null || echo 0)"
fi
echo "== WARN: $warn"
exit 0
