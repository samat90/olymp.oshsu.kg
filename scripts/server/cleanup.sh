#!/bin/bash
# Frees disk space on one machine. By default it only SHOWS what would be removed; --apply removes it.
#
#   sudo bash scripts/server/cleanup.sh web            # olymp.oshsu.kg, dry run
#   sudo bash scripts/server/cleanup.sh web --apply
#   sudo bash /tmp/olymp/cleanup.sh judge --apply      # judge.oshsu.kg
#
# NEVER touched: the database (/var/lib/postgresql), media/ and problems/ (uploads, tests), the daily
# backups (they keep 14 days on their own), the 2026-10-21 pre-olympiad backup, the newest deploy
# backups, the git repository's history, any configuration.
# Removed: old system journal, old rotated logs, package caches, pip caches, stale temporary files,
# deploy backups beyond the policy, leftovers of interrupted git downloads and of problem-set builds.
set -uo pipefail

ROLE=${1:-}
APPLY=0
[ "${2:-}" = "--apply" ] && APPLY=1
case "$ROLE" in web|judge) ;; *) echo "usage: cleanup.sh web|judge [--apply]"; exit 2 ;; esac
[ "$(id -u)" = 0 ] || { echo "run with sudo"; exit 2; }

APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
KEEP_DEPLOY_BACKUPS=${OLYMP_KEEP_DEPLOY_BACKUPS:-10}   # newest deploy backups always kept
KEEP_DEPLOY_DAYS=${OLYMP_KEEP_DEPLOY_DAYS:-14}         # and every deploy backup younger than this
total=0

say() { echo "$*"; }
size_kb() { du -sk "$@" 2>/dev/null | awk '{s += $1} END {print s + 0}'; }
human() { awk -v k="$1" 'BEGIN { if (k > 1048576) printf "%.1f GB", k / 1048576; else if (k > 1024) printf "%.0f MB", k / 1024; else printf "%d KB", k }'; }

# remove <description> <paths...>: shows the size, removes only with --apply.
remove() {
    local what=$1; shift
    [ $# = 0 ] && return
    local kb
    kb=$(size_kb "$@")
    total=$((total + kb))
    say "  $(human "$kb")  $what ($# item(s))"
    for p in "$@"; do say "        $p"; done | head -12
    [ $# -gt 12 ] && say "        ..."
    [ "$APPLY" = 1 ] && rm -rf -- "$@"
}
# collect <find arguments...>: prints NUL-free list (paths here never contain newlines).
collect() { find "$@" 2>/dev/null; }

say "== $(hostname): disk before"
df -h / | sed 's/^/  /'
[ "$APPLY" = 1 ] || say "  (dry run: nothing is removed, add --apply)"
say

say "== System journal (keeps the last 30 days)"
journalctl --disk-usage 2>/dev/null | sed 's/^/  /'
[ "$APPLY" = 1 ] && journalctl --vacuum-time=30d --vacuum-size=500M 2>&1 | tail -1 | sed 's/^/  /'

say "== Rotated logs older than 30 days"
mapfile -t old_logs < <(collect /var/log -type f \( -name '*.gz' -o -name '*.[0-9]' -o -name '*.old' \) -mtime +30)
remove "old rotated logs in /var/log" "${old_logs[@]}"

say "== Package caches"
apt_kb=$(size_kb /var/cache/apt/archives)
say "  $(human "$apt_kb")  downloaded .deb packages (apt clean)"
total=$((total + apt_kb))
[ "$APPLY" = 1 ] && apt-get clean
say "  packages apt would autoremove (NOT removed automatically, review and run 'apt autoremove --purge' by hand):"
apt-get -s autoremove --purge 2>/dev/null | awk '/^Purg|^Remv/ {print "        " $2}' | head -20

say "== pip / npm caches"
mapfile -t caches < <(collect /root/.cache/pip /home/*/.cache/pip /root/.npm/_cacache /home/*/.npm/_cacache -maxdepth 0)
remove "pip and npm download caches" "${caches[@]}"

say "== Temporary files older than 7 days"
mapfile -t tmp_old < <(collect /tmp /var/tmp -mindepth 1 -maxdepth 1 -mtime +7 \
    ! -name 'systemd-private-*' ! -name '.X*' ! -name '.ICE-unix' ! -name 'snap-private-tmp' ! -name 'olymp-health.state' ! -name 'tmux-*' ! -name 'hsperfdata_*' ! -name '*.lock' ! -name '*.pid' ! -name '*.sock')
remove "old files in /tmp and /var/tmp" "${tmp_old[@]}"

if command -v docker >/dev/null 2>&1; then
    say "== Docker (only stopped containers, dangling images and build cache; volumes are kept)"
    docker system df 2>/dev/null | sed 's/^/  /'
    [ "$APPLY" = 1 ] && docker system prune -f 2>&1 | tail -1 | sed 's/^/  /'
fi

if [ "$ROLE" = web ]; then
    say "== Deploy backups (keeps the newest $KEEP_DEPLOY_BACKUPS and all younger than $KEEP_DEPLOY_DAYS days)"
    if [ -d /var/backups/olymp/deploy ]; then
        mapfile -t all < <(ls -1d /var/backups/olymp/deploy/*/ 2>/dev/null | sort)
        old=()
        n=${#all[@]}
        for ((i = 0; i < n - KEEP_DEPLOY_BACKUPS; i++)); do
            d=${all[$i]%/}
            [ -n "$(find "$d" -maxdepth 0 -mtime +"$KEEP_DEPLOY_DAYS")" ] && old+=("$d")
        done
        say "  $n deploy backup(s), $(human "$(size_kb /var/backups/olymp/deploy)") in all"
        remove "old deploy backups" "${old[@]}"
    fi
    say "  kept as is: /var/backups/olymp/daily ($(human "$(size_kb /var/backups/olymp/daily)")), /var/backups/olymp/20261021-preolymp, /var/backups/olymp/system"

    say "== Git repository of the deploy"
    mapfile -t tmp_packs < <(collect /home/admin/olymp.git/objects -name 'tmp_*' -mmin +120)
    remove "leftovers of interrupted downloads from GitHub" "${tmp_packs[@]}"
    if [ "$APPLY" = 1 ]; then
        runuser -u admin -- git --git-dir=/home/admin/olymp.git gc --quiet 2>&1 | sed 's/^/  /'
        say "  git gc done (history is kept)"
    fi

    say "== Leftovers of problem-set imports (the .done/.failed markers stay)"
    mapfile -t ps < <(collect /home/admin/problemsets -mindepth 1 -maxdepth 1 -type d -mmin +120)
    remove "unpacked problem-set builds" "${ps[@]}"

    say "== Expired logins and database upkeep"
    if [ "$APPLY" = 1 ]; then
        (cd "$APP" && runuser -u admin -- venv/bin/python manage.py clearsessions) && say "  expired sessions removed"
        runuser -u postgres -- psql -q -d olymp_oshsu -c 'VACUUM (ANALYZE);' && say "  database VACUUM ANALYZE done (nothing deleted)"
    else
        say "  with --apply: manage.py clearsessions (expired logins only) and VACUUM ANALYZE of the database"
    fi
fi

if [ "$ROLE" = judge ]; then
    say "== Problem-set builds on the judge (tests are already on the site)"
    mapfile -t jb < <(collect /home/admin/problemsets-build -mindepth 1 -maxdepth 1 -mmin +120)
    remove "test generation folders" "${jb[@]}"
    say "== Old copies of the code runner and judge files (keeps the newest 5 of each)"
    for root in /home/admin/olymp-runner/backup /home/admin/judge-backup; do
        [ -d "$root" ] || continue
        mapfile -t bk < <(ls -1d "$root"/*/ 2>/dev/null | sort | head -n -5)
        remove "old backups in $root" "${bk[@]%/}"
    done
    say "  kept as is: /home/admin/olymp-backups (copies of the database backups, 30 days)"
fi

say
say "== Biggest folders now (for a look, nothing is removed here)"
du -xhd2 / 2>/dev/null | sort -rh | head -15 | sed 's/^/  /'
say
say "== Total: $(human "$total") $([ "$APPLY" = 1 ] && echo freed || echo 'can be freed')"
df -h / | sed 's/^/  /'
