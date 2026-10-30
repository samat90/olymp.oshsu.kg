#!/bin/bash
# Brings the code runner on judge.oshsu.kg up to date with runner/ of the deployed code.
# Runs on the web server as admin at the end of scripts/deploy.sh; can also be run by hand:
#
#   bash scripts/server/sync_runner.sh
#
# Needs SSH without a password from admin@olymp.oshsu.kg to admin@judge.oshsu.kg. Without it,
# nothing is changed and runner/ has to be copied by hand (docs/DEPLOY-2026-10.md, section 5).
# The old files are kept in olymp-runner/backup/<date>; if the new runner does not answer
# its health check, they are put back. Only the runner's .py files are touched.
set -uo pipefail

APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
JUDGE=${OLYMP_JUDGE:-admin@10.10.8.227}
DIR=${OLYMP_RUNNER_DIR:-/home/admin/olymp-runner}
HEALTH=${OLYMP_RUNNER:-http://10.10.8.227:9910/health}
SSH=${OLYMP_JUDGE_SSH:-ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new}
STAMP=$(date +%Y%m%d-%H%M%S)

log() { echo "[$(date +%H:%M:%S)] runner: $*"; }

cd "$APP/runner" || exit 1
FILES=$(ls server.py runner_*.py | LC_ALL=C sort)
version=$(cat $FILES | sha256sum | cut -c1-12)

running_version() {
    curl -s -m 5 "$HEALTH" | python3 -c 'import json, sys; print(json.load(sys.stdin).get("version", ""))' 2>/dev/null
}

if [ "$(running_version)" = "$version" ]; then
    log "up to date ($version)"
    exit 0
fi
if ! $SSH "$JUDGE" true; then
    log "no SSH access to $JUDGE: copy runner/ to $DIR by hand (version $version)"
    exit 1
fi

# The runner is a systemd service of admin with Restart=always: stopping the process restarts it.
# [s] keeps pkill from matching the remote shell that runs it.
RESTART="sudo -n systemctl restart olymp-runner 2>/dev/null || pkill -u \"\$(id -un)\" -f '$DIR/[s]erver.py' || true"

wait_healthy() {
    for _ in $(seq 1 20); do
        sleep 3
        [ "$(running_version)" = "$1" ] && return 0
    done
    return 1
}

log "installing version $version (backup: $DIR/backup/$STAMP)"
if ! tar cf - $FILES | $SSH "$JUDGE" "set -e; cd '$DIR'; mkdir -p 'backup/$STAMP' .new; \
        cp -p server.py runner_*.py 'backup/$STAMP/'; rm -f .new/*; tar xf - -C .new; \
        mv .new/*.py .; rmdir .new; $RESTART"; then
    log "copying failed"
fi
if wait_healthy "$version"; then
    log "OK: running $version"
    exit 0
fi

log "the new runner does not answer, restoring $DIR/backup/$STAMP"
$SSH "$JUDGE" "cd '$DIR' && cp -p 'backup/$STAMP/'*.py . && { $RESTART; }"
sleep 6
log "after restore: $(curl -s -m 5 "$HEALTH")"
exit 1
