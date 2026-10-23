#!/bin/bash
# Start the local copy of the site inside WSL: web on :8000, judge bridge, one judge, code runner.
# Usage (from Windows): wsl -d Ubuntu-24.04 -u root -- bash /mnt/d/projects/olymp.oshsu.kg/scripts/dev/wsl_start.sh
set -e
SITE=/mnt/d/projects/olymp.oshsu.kg
PY=/opt/olymp/venv/bin/python
LOG=/var/log/olymp-dev
mkdir -p $LOG
export DJANGO_SETTINGS_MODULE=dmoj.dev_wsl_settings

service postgresql start >/dev/null
service redis-server start >/dev/null

pkill -f 'manage.py runserver' || true
pkill -f 'manage.py runbridged' || true
pkill -f 'dmoj -c /opt/judge/judge.yml' || true
pkill -f 'runner/server.py' || true
sleep 1

cd $SITE
nohup $PY manage.py runbridged > $LOG/bridge.log 2>&1 &
nohup $PY manage.py runserver 0.0.0.0:8000 > $LOG/web.log 2>&1 &

if [ -f /opt/judge/judge.yml ]; then
    sleep 3
    nohup sudo -u judge /opt/judge/venv/bin/dmoj -c /opt/judge/judge.yml -p 9999 127.0.0.1 > $LOG/judge.log 2>&1 &
fi

if [ -f $SITE/runner/server.py ]; then
    nohup sudo -u judge /opt/judge/venv/bin/python $SITE/runner/server.py --config /opt/judge/judge.yml \
        --listen 127.0.0.1:9910 --secret-file /opt/judge/runner.secret \
        --allow-origin http://127.0.0.1:8000 --allow-origin http://localhost:8000 > $LOG/runner.log 2>&1 &
fi

echo started
