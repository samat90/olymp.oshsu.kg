#!/bin/bash
# Before the first deploy: shows files on the server that differ from the snapshot taken on
# 2026-10-21 (branch "snapshot" in /home/admin/olymp.git). Anything listed was changed on the
# server after that day and would be replaced by the deploy (it is still kept in the backup).
set -euo pipefail
APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
REPO=${OLYMP_REPO:-/home/admin/olymp.git}
changed=$(git --git-dir="$REPO" --work-tree="$APP" -c core.autocrlf=true diff --name-only snapshot -- . 2>/dev/null || true)
if [ -z "$changed" ]; then
    echo "OK: the server code is the same as the 2026-10-21 snapshot."
else
    echo "These files were changed on the server after 2026-10-21:"
    echo "$changed" | sed 's/^/  /'
    echo
    echo "Send the list to Claude before deploying, or save copies: tar czf ~/server-changes.tgz -C $APP \$(echo \$changed)"
fi
