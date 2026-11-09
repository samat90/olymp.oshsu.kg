#!/bin/bash
# Brings the judge machine (judge.oshsu.kg) up to date with the files of the deployed code that live there:
#   - the language executors scripts/judge/{CSHARP,FSHARP,SB3}.py -> ~/judge-server/dmoj/executors/;
#   - the judge-side systemd units from scripts/systemd/ (list JUDGE_UNITS below);
#   - every file under server-config/judge/, to the same path from / on the judge.
# Runs on olymp.oshsu.kg as admin at the end of scripts/deploy.sh and in the quiet auto-deploy runs,
# over the same SSH access as sync_runner.sh. By hand:
#
#   bash scripts/server/sync_judge.sh           # update when something changed
#   bash scripts/server/sync_judge.sh --check   # only show what differs, change nothing
#
# The judges are restarted only when no submission is being graded and no olympiad is running;
# otherwise nothing is copied and the next run tries again. Old files go to
# /home/admin/judge-backup/<date>/ on the judge. The code runner is handled by sync_runner.sh.
set -uo pipefail

APP=${OLYMP_APP:-/var/www/olymp.oshsu.kg}
PY=${OLYMP_PY:-$APP/venv/bin/python}
JUDGE=${OLYMP_JUDGE:-admin@10.10.8.227}
SSH=${OLYMP_JUDGE_SSH:-ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new}
JS=${OLYMP_JUDGE_SERVER:-/home/admin/judge-server}
STAMP_FILE=/home/admin/.olymp-judge-version
EXECUTORS="CSHARP.py FSHARP.py SB3.py"
JUDGE_UNITS="olymp-judge.service olymp-judge2.service olymp-runner.service olymp-runner-firewall.service"
CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1

log() { echo "[$(date +%H:%M:%S)] judge: $*"; }

cd "$APP" || exit 1
# Bundle: files/<path on the judge>, the same layout for every kind of file.
bundle=$(mktemp -d)
trap 'rm -rf "$bundle"' EXIT
for f in $EXECUTORS; do
    [ -f "scripts/judge/$f" ] && install -D -m 644 "scripts/judge/$f" "$bundle/files$JS/dmoj/executors/$f"
done
for u in $JUDGE_UNITS; do
    [ -f "scripts/systemd/$u" ] && install -D -m 644 "scripts/systemd/$u" "$bundle/files/etc/systemd/system/$u"
done
if [ -d server-config/judge ]; then
    (cd server-config/judge && find . -type f ! -name README.md -print0 | while IFS= read -r -d '' f; do
        install -D -m 644 "$f" "$bundle/files/${f#./}"
    done)
fi
version=$(cd "$bundle/files" && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum | cut -c1-12)

if ! $SSH "$JUDGE" true 2>/dev/null; then
    log "no SSH access to $JUDGE, skipped (version $version)"
    exit 1
fi
current=$($SSH "$JUDGE" "cat $STAMP_FILE 2>/dev/null")
if [ "$current" = "$version" ] && [ "$CHECK" = 0 ]; then
    exit 0
fi

if [ "$CHECK" = 1 ]; then
    log "version here $version, on the judge ${current:-none}"
    (cd "$bundle/files" && tar cf - .) | $SSH "$JUDGE" "t=\$(mktemp -d); tar xf - -C \$t; cd \$t;
        find . -type f | while read -r f; do p=\${f#.}; if ! cmp -s \"\$f\" \"\$p\" 2>/dev/null; then
            echo \"differs: \$p\"; diff -u \"\$p\" \"\$f\" 2>/dev/null | head -30; fi; done; rm -rf \$t"
    exit 0
fi

busy=$(cd "$APP" && "$PY" manage.py shell -c "
from datetime import timedelta
from django.db.models import F
from django.utils import timezone
from judge.models import Contest, Submission
now = timezone.now()
olympiad = Contest.objects.filter(start_time__lte=now, end_time__gt=now,
                                  end_time__lte=F('start_time') + timedelta(hours=48)).exists()
# Only fresh submissions count: one stuck in the queue for hours must not block the update forever.
grading = Submission.objects.filter(status__in=('QU', 'P', 'G'), date__gt=now - timedelta(minutes=30)).exists()
print('olympiad' if olympiad else 'grading' if grading else '')" 2>/dev/null) || busy=unknown
if [ -n "$busy" ]; then
    log "update $version is waiting ($busy), the next run will try again"
    exit 0
fi

log "installing version $version (was ${current:-none})"
# On the judge: back up what is replaced, install what differs, then reload/restart only what is needed.
if (cd "$bundle/files" && tar cf - .) | $SSH "$JUDGE" "set -u
    b=/home/admin/judge-backup/\$(date +%Y%m%d-%H%M%S); t=\$(mktemp -d); tar xf - -C \$t; cd \$t
    units=0; execs=0; runner=0; fail=0
    for f in \$(find . -type f | sort); do
        p=\${f#.}
        cmp -s \"\$f\" \"\$p\" 2>/dev/null && continue
        if [ -f \"\$p\" ]; then mkdir -p \"\$b\$(dirname \"\$p\")\"; cp -p \"\$p\" \"\$b\$p\" 2>/dev/null || sudo -n cp -p \"\$p\" \"\$b\$p\"; fi
        case \"\$p\" in
            /home/admin/*) install -D -m 644 \"\$f\" \"\$p\" || fail=1 ;;
            *) sudo -n install -D -m 644 \"\$f\" \"\$p\" || fail=1 ;;
        esac
        echo \"    installed \$p\"
        case \"\$p\" in
            */systemd/system/olymp-runner*) units=1; runner=1 ;;
            */systemd/system/*) units=1 ;;
            */dmoj/executors/*) execs=1 ;;
        esac
    done
    rm -rf \$t
    [ \$units = 1 ] && { sudo -n systemctl daemon-reload || fail=1; }
    [ \$runner = 1 ] && { sudo -n systemctl restart olymp-runner || fail=1; }
    if [ \$execs = 1 ]; then
        js=\$(systemctl list-units --plain --no-legend 'olymp-judge*.service' | awk '{print \$1}')
        sudo -n systemctl restart \$js || fail=1
        echo \"    restarted: \"\$js
    fi
    exit \$fail"; then
    $SSH "$JUDGE" "echo $version > $STAMP_FILE"
    sleep 30
    online=$(cd "$APP" && "$PY" manage.py shell -c "
from judge.models import Judge
print(Judge.objects.filter(online=True).count())" 2>/dev/null)
    log "OK: judge files at version $version, judges online: ${online:-?}"
else
    log "some files were not installed on the judge (sudo without a password needed there), see above"
    exit 1
fi
