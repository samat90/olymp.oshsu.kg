#!/bin/bash
# Security and health check of one machine. Changes nothing, only prints OK / WARN lines.
#   olymp.oshsu.kg:  sudo bash scripts/server/audit.sh web
#   judge.oshsu.kg:  sudo bash /tmp/olymp/audit.sh judge
ROLE=${1:-web}
APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
WEB_IP=${OLYMP_WEB_IP:-10.10.8.226}
warn=0
ok() { echo "OK    $*"; }
bad() { echo "WARN  $*"; warn=$((warn + 1)); }

listening() { ss -Hltn "sport = :$1" 2>/dev/null | awk '{print $4}'; }
only_local() {  # port name
    local addrs
    addrs=$(listening "$1")
    if [ -z "$addrs" ]; then
        ok "$2 (port $1) is not listening"
    elif echo "$addrs" | grep -qvE '^(127\.0\.0\.1|\[::1\]):'; then
        bad "$2 (port $1) listens on all addresses: $addrs. Bind it to 127.0.0.1."
    else
        ok "$2 (port $1) is local only"
    fi
}
firewalled() {  # port name: open to the network, but must be limited by the firewall
    if [ -z "$(listening "$1")" ]; then
        ok "$2 (port $1) is not listening"
    elif iptables -S INPUT 2>/dev/null | grep -qE -- "--dport $1 .*-j (DROP|REJECT)"; then
        ok "$2 (port $1) is closed by iptables except for allowed hosts"
    else
        bad "$2 (port $1) is open to everyone. Allow only $WEB_IP and drop the rest (see DEPLOY-2026-10.md)."
    fi
}

echo "== $ROLE: $(hostname), $(date '+%F %T')"

# --- SSH ---
sshd=$(sshd -T 2>/dev/null)
if echo "$sshd" | grep -q '^permitrootlogin yes'; then bad "SSH allows root login with a password (PermitRootLogin yes)."
else ok "SSH root login"; fi
if echo "$sshd" | grep -q '^passwordauthentication yes'; then
    echo "INFO  SSH accepts passwords. Keys only is safer (PasswordAuthentication no) once everyone has a key."
fi

# --- updates ---
if systemctl is-enabled unattended-upgrades >/dev/null 2>&1; then ok "automatic security updates"
else bad "automatic security updates are off: sudo apt install unattended-upgrades"; fi
pending=$(apt-get -s upgrade 2>/dev/null | grep -c '^Inst .*security' || true)
[ "${pending:-0}" -gt 0 ] && bad "$pending security updates are waiting: sudo apt upgrade" || ok "no pending security updates"

# --- disk and memory ---
use=$(df -P / | awk 'NR==2 {gsub("%", "", $5); print $5}')
[ "$use" -ge 85 ] && bad "disk / is ${use}% full" || ok "disk / is ${use}% full"
avail=$(free -m | awk '/^Mem:/ {print $7}')
[ "$avail" -lt 500 ] && bad "only ${avail} MB of memory available" || ok "${avail} MB of memory available"
swap=$(free -m | awk '/^Swap:/ {print $2}')
[ "$swap" -eq 0 ] && echo "INFO  no swap: under a memory spike processes get killed instead of slowing down"

if [ "$ROLE" = web ]; then
    only_local 5432 PostgreSQL
    only_local 6379 Redis
    only_local 8000 gunicorn
    only_local 9997 "event daemon (post)"
    only_local 9996 "event daemon (listen)"
    only_local 15100 "event daemon (poll)"
    firewalled 9999 "judge bridge"
    only_local 9998 "bridge (site side)"

    for f in "$APP/dmoj/local_settings.py" /home/admin/runner.secret; do
        [ -f "$f" ] || continue
        perm=$(stat -c %a "$f")
        case "$perm" in
            600|640|400|440) ok "$f permissions $perm" ;;
            *) bad "$f is readable by every user ($perm): chmod 640 $f" ;;
        esac
    done
    if [ -x "$APP/venv/bin/python" ]; then
        report=$(cd "$APP" && sudo -u "$(stat -c %U "$APP")" venv/bin/python manage.py security_report 2>/dev/null)
        echo "$report" | sed 's/^WARNING: /WARN  /; s/^Security settings: OK/OK    Django settings/'
        warn=$((warn + $(echo "$report" | grep -c '^WARNING')))
    fi
    last=$(ls -1t /var/backups/olymp/*.dump /var/backups/olymp/*/*.dump* 2>/dev/null | head -1)
    if [ -z "$last" ]; then bad "no database backups found in /var/backups/olymp"
    elif [ -n "$(find "$last" -mmin +1560)" ]; then bad "the newest database backup is older than a day: $last"
    else ok "database backup is fresh: $last"; fi
else
    firewalled 9910 "code runner"
    for s in olymp-judge olymp-judge2 olymp-runner; do
        systemctl is-active --quiet "$s" && ok "$s is running" || bad "$s is not running"
    done
fi

echo "== $warn warning(s)"
