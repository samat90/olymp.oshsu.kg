#!/bin/bash
# Runs the site under gunicorn the way the server does and loads it with N participants.
#   run_load.sh <label> "<gunicorn args>" [users] [minutes] [cpus]
# Example: run_load.sh baseline "-w 4" 1000 3 0-3
set -e
LABEL=$1
GUNICORN_ARGS=$2
USERS=${3:-1000}
MINUTES=${4:-3}
CPUS=${5:-0-3}
SITE=/mnt/d/projects/olymp.oshsu.kg
OUT=/root/load-results
mkdir -p $OUT
export DJANGO_SETTINGS_MODULE=${SETTINGS:-dmoj.load_settings}

pkill -f 'gunicorn.*:8080' || true
sleep 1
cd $SITE
taskset -c $CPUS /opt/olymp/venv/bin/gunicorn $GUNICORN_ARGS -b 127.0.0.1:8080 dmoj.wsgi:application \
    > $OUT/$LABEL-gunicorn.log 2>&1 &
sleep 6
curl -s -o /dev/null -w "warmup %{http_code}\n" http://127.0.0.1:8080/

taskset -c ${LOCUST_CPUS:-6-11} /opt/pw/bin/locust -f $SITE/scripts/load/locustfile.py --host http://127.0.0.1:8080 \
    -u $USERS -r ${SPAWN_RATE:-25} --headless -t ${MINUTES}m --csv $OUT/$LABEL --only-summary --processes 4 \
    > $OUT/$LABEL-locust.log 2>&1 || true

pkill -f 'gunicorn.*:8080' || true
python3 - "$OUT/${LABEL}_stats.csv" <<'PY'
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1])))
print('%-16s %8s %6s %8s %8s %8s %8s' % ('name', 'reqs', 'fail', 'rps', 'p50', 'p95', 'p99'))
for r in rows:
    print('%-16s %8s %6s %8.1f %8s %8s %8s' % (r['Name'][:16], r['Request Count'], r['Failure Count'],
          float(r['Requests/s']), r['50%'], r['95%'], r['99%']))
PY
