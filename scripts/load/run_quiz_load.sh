#!/bin/bash
# Quiz load test on the laptop: the site under gunicorn like on the server, N players in one game.
#   run_quiz_load.sh <label> "<gunicorn args>" [players] [cpus]
# Example: run_quiz_load.sh quiz-sync "-w 4" 1000 0-3
set -e
LABEL=$1
GUNICORN_ARGS=$2
PLAYERS=${3:-1000}
CPUS=${4:-0-3}
SITE=/mnt/d/projects/olymp.oshsu.kg
OUT=/root/load-results
PY=/opt/olymp/venv/bin/python
mkdir -p $OUT
export DJANGO_SETTINGS_MODULE=${SETTINGS:-dmoj.load_settings}

pkill -f 'gunicorn.*:8080' || true
sleep 1
# Old quiz keys (join limits per IP, finished games) must not affect the run.
redis-cli -n 1 --scan --pattern ':1:qz:*' | xargs -r -n 500 redis-cli -n 1 del > /dev/null
cd $SITE
taskset -c $CPUS /opt/olymp/venv/bin/gunicorn $GUNICORN_ARGS -b 127.0.0.1:8080 --backlog 2048 dmoj.wsgi:application \
    > $OUT/$LABEL-gunicorn.log 2>&1 &
sleep 6
curl -s -o /dev/null -w "warmup %{http_code}\n" http://127.0.0.1:8080/quiz/join/

rm -f $OUT/$LABEL.pin
taskset -c ${LOCUST_CPUS:-6-11} $PY scripts/load/quiz_load_driver.py $OUT/$LABEL.pin $PLAYERS ${MODE:-auto} \
    > $OUT/$LABEL-driver.log 2>&1 &
DRIVER=$!
while [ ! -s $OUT/$LABEL.pin ]; do sleep 0.5; done
export QUIZ_PIN=$(cat $OUT/$LABEL.pin)
echo "pin $QUIZ_PIN"

taskset -c ${LOCUST_CPUS:-6-11} /opt/pw/bin/locust -f $SITE/scripts/load/locustfile_quiz.py --host http://127.0.0.1:8080 \
    -u $PLAYERS -r ${SPAWN_RATE:-25} --headless -t ${MINUTES:-8}m --csv $OUT/$LABEL --only-summary --processes 4 \
    > $OUT/$LABEL-locust.log 2>&1 || true

wait $DRIVER || true
pkill -f 'gunicorn.*:8080' || true
cat $OUT/$LABEL-driver.log
python3 - "$OUT/${LABEL}_stats.csv" <<'PY'
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1])))
print('%-12s %8s %6s %8s %8s %8s %8s %8s' % ('name', 'reqs', 'fail', 'rps', 'p50', 'p95', 'p99', 'max'))
for r in rows:
    print('%-12s %8s %6s %8.1f %8s %8s %8s %8.0f' % (r['Name'][:12], r['Request Count'], r['Failure Count'],
          float(r['Requests/s']), r['50%'], r['95%'], r['99%'], float(r['Max Response Time'])))
PY
