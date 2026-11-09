#!/bin/bash
# Installs the server settings that are kept in git, so that they change through GitHub like the code.
# Runs at the end of scripts/deploy.sh on olymp.oshsu.kg (as admin, needs `sudo -n`), or by hand:
#
#   bash scripts/server/sync_system.sh            # install what changed
#   bash scripts/server/sync_system.sh --check    # only show what differs, change nothing
#
# What is installed:
#   - the systemd units of the web machine from scripts/systemd/ (list WEB_UNITS below);
#   - every file under server-config/web/, to the same path from / (for example
#     server-config/web/etc/cron.d/olymp-health -> /etc/cron.d/olymp-health).
# Only files that differ are touched; the old file is kept in /var/backups/olymp/system/<date>/.
# nginx settings are checked with `nginx -t` before the reload; if the check fails, the old files are
# put back and nginx keeps running as before. Secrets (dmoj/local_settings.py, keys) are never in git.
set -uo pipefail

APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
ROOT=${OLYMP_SYSTEM_ROOT:-}            # tests install into a scratch folder instead of /
BACKUP=${OLYMP_SYSTEM_BACKUPS:-$ROOT/var/backups/olymp/system}/$(date +%Y%m%d-%H%M%S)
CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1
WEB_UNITS="olymp-web.service olymp-bridge.service olymp-event.service
           olymp-autodeploy.service olymp-autodeploy.timer olymp-bridge-firewall.service
           olymp-publish-problems.service olymp-publish-problems.timer"

log() { echo "[$(date +%H:%M:%S)] system: $*"; }
if [ -z "$ROOT" ]; then
    SUDO="sudo -n"
    if [ "$CHECK" = 0 ] && ! sudo -n true 2>/dev/null; then
        log "admin has no sudo without a password here: server settings were not updated"
        exit 1
    fi
else
    SUDO=""
fi

# Pairs "source destination".
pairs=()
for unit in $WEB_UNITS; do
    [ -f "$APP/scripts/systemd/$unit" ] && pairs+=("$APP/scripts/systemd/$unit $ROOT/etc/systemd/system/$unit")
done
if [ -d "$APP/server-config/web" ]; then
    while IFS= read -r -d '' f; do
        rel=${f#"$APP/server-config/web"}
        case "$rel" in */README.md) continue ;; esac
        pairs+=("$f $ROOT$rel")
    done < <(find "$APP/server-config/web" -type f -print0 | sort -z)
fi

changed_systemd=0 changed_nginx=0 status=0
installed=()
for pair in "${pairs[@]}"; do
    src=${pair%% *} dst=${pair#* }
    if $SUDO test -f "$dst" && $SUDO cmp -s "$src" "$dst"; then
        continue
    fi
    if [ "$CHECK" = 1 ]; then
        echo "differs: $dst"
        $SUDO test -f "$dst" && $SUDO diff -u "$dst" "$src" | head -40
        continue
    fi
    if $SUDO test -f "$dst"; then
        $SUDO mkdir -p "$BACKUP$(dirname "$dst")"
        $SUDO cp -p "$dst" "$BACKUP$dst"
    fi
    mode=644
    case "$dst" in */bin/*|*.sh) mode=755 ;; esac
    if $SUDO install -D -m "$mode" "$src" "$dst"; then
        log "installed $dst"
        installed+=("$dst")
        case "$dst" in */systemd/system/*) changed_systemd=1 ;; */nginx/*) changed_nginx=1 ;; esac
    else
        log "could not install $dst"; status=1
    fi
done

[ "$CHECK" = 1 ] && exit 0
[ -n "$ROOT" ] && exit $status

if [ "$changed_systemd" = 1 ]; then
    $SUDO systemctl daemon-reload && log "systemd reloaded"
fi
if [ "$changed_nginx" = 1 ]; then
    if $SUDO nginx -t 2>&1 | sed 's/^/    /'; [ "${PIPESTATUS[0]}" = 0 ]; then
        $SUDO systemctl reload nginx && log "nginx reloaded"
    else
        log "nginx rejected the new settings, putting the old ones back"
        for dst in "${installed[@]}"; do
            case "$dst" in */nginx/*)
                if $SUDO test -f "$BACKUP$dst"; then $SUDO cp -p "$BACKUP$dst" "$dst"; else $SUDO rm -f "$dst"; fi ;;
            esac
        done
        $SUDO nginx -t > /dev/null 2>&1 && log "old nginx settings are valid again"
        status=1
    fi
fi
[ ${#installed[@]} = 0 ] && log "nothing to update"
exit $status
