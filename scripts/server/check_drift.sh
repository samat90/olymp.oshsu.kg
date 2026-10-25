#!/bin/bash
# Before the first deploy: shows files on the server that differ from the snapshot taken on
# 2026-10-21 (branch "snapshot" in /home/admin/olymp.git). Anything listed was changed on the
# server after that day and would be replaced by the deploy (it is still kept in the backup).
set -euo pipefail
APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
REPO=${OLYMP_REPO:-/home/admin/olymp.git}
# A separate index, so the check works in a bare repository and does not touch anything.
export GIT_INDEX_FILE=$(mktemp)
trap 'rm -f "$GIT_INDEX_FILE"' EXIT
G="git --git-dir=$REPO --work-tree=$APP -c core.autocrlf=true -c core.fileMode=false"
$G read-tree snapshot
$G update-index -q --refresh > /dev/null 2>&1 || true
changed=$($G diff-files --name-only 2>/dev/null || true)
if [ -z "$changed" ]; then
    echo "OK: the server code is the same as the 2026-10-21 snapshot."
else
    echo "These files were changed on the server after 2026-10-21:"
    echo "$changed" | sed 's/^/  /'
    echo
    echo "Review this list before deploying. The deploy keeps a copy of the old code in its backup."
fi
