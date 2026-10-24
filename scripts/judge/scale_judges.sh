#!/bin/bash
# Runs one judge per CPU core of this machine (or the number given), so grading uses the whole machine.
#
#   sudo bash scale_judges.sh          # judges = number of cores
#   sudo bash scale_judges.sh 6        # exactly 6 judges
#
# judge1 and judge2 keep their old services (olymp-judge, olymp-judge2). Judges 3..N get
# configs judgeN.yml and the service olymp-judge@N. New judges also need a record on the site:
# the script prints the commands to run on olymp.oshsu.kg. Run it again after the machine gets
# more cores; extra judges beyond N are stopped.
set -euo pipefail

CONF=/home/admin/judge-config
BASE=$CONF/judge.yml
COUNT=${1:-$(nproc)}
[ "$COUNT" -ge 2 ] || COUNT=2
[ -f "$BASE" ] || { echo "No $BASE"; exit 1; }

cp "$(dirname "$0")/olymp-judge@.service" /etc/systemd/system/ 2>/dev/null || true
[ -f /etc/systemd/system/olymp-judge@.service ] || { echo "Copy olymp-judge@.service to /etc/systemd/system first"; exit 1; }
systemctl daemon-reload

NEW=()
for i in $(seq 3 "$COUNT"); do
    cfg=$CONF/judge$i.yml
    if [ ! -f "$cfg" ]; then
        key=$(head -c 48 /dev/urandom | base64 -w0 | tr -d '/+=' | head -c 64)
        # Same runtimes and problem folders as judge1, own name and key.
        sed -e "s/^id:.*/id: judge$i/" -e "s/^key:.*/key: $key/" "$BASE" > "$cfg"
        chown admin:admin "$cfg"
        chmod 600 "$cfg"
        NEW+=("judge$i $key")
    fi
    systemctl enable --now "olymp-judge@$i" >/dev/null
done

# Stop judges above COUNT (for example after the machine was made smaller).
for unit in $(systemctl list-units --plain --no-legend 'olymp-judge@*' | awk '{print $1}'); do
    n=${unit#olymp-judge@}; n=${n%.service}
    if [ "$n" -gt "$COUNT" ]; then
        systemctl disable --now "$unit" >/dev/null
        echo "stopped $unit"
    fi
done

echo "Judges on this machine: $COUNT (judge1, judge2 and olymp-judge@3..$COUNT)."
if [ ${#NEW[@]} -gt 0 ]; then
    echo
    echo "Run on olymp.oshsu.kg to register the new judges:"
    for line in "${NEW[@]}"; do
        echo "  cd /var/www/olymp.oshsu.kg && venv/bin/python manage.py addjudge $line"
    done
fi
