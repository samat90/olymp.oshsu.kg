#!/bin/bash
# Checks the site, the judges and the code runner every few minutes and reports when something
# breaks or comes back. Messages go to /var/log/olymp/health.log and, if configured, to Telegram.
#   /etc/cron.d/olymp-health:
#   */2 * * * * root /var/www/olymp.oshsu.kg/scripts/server/healthcheck.sh
# Telegram (optional) in /etc/olymp-monitor.env:
#   TELEGRAM_TOKEN=123456:ABC...   TELEGRAM_CHAT=123456789
set -u

SITE=${OLYMP_SITE:-http://127.0.0.1:8000/}
RUNNER=${OLYMP_RUNNER:-http://10.10.8.227:9910/health}
DB=${OLYMP_DB:-olymp_oshsu}
MIN_JUDGES=${OLYMP_MIN_JUDGES:-1}
STATE=${OLYMP_HEALTH_STATE:-/var/tmp/olymp-health.state}
LOG=${OLYMP_HEALTH_LOG:-/var/log/olymp/health.log}
[ -f /etc/olymp-monitor.env ] && . /etc/olymp-monitor.env

PSQL=psql
[ "$(id -u)" = 0 ] && PSQL='runuser -u postgres -- psql'

problems=()

code=$(curl -s -o /dev/null -m 15 -w '%{http_code}' -H 'Host: olymp.oshsu.kg' "$SITE" || true)
[ "$code" = 200 ] || problems+=("сайт не отвечает (код $code)")

judges=$($PSQL -At -d "$DB" -c 'select count(*) from judge_judge where online' 2>/dev/null || echo "?")
if [ "$judges" = "?" ]; then problems+=("нет связи с базой")
elif [ "$judges" -lt "$MIN_JUDGES" ]; then problems+=("судей онлайн: $judges")
fi

queued=$($PSQL -At -d "$DB" -c "select count(*) from judge_submission where status in ('QU','P') and date < now() - interval '5 minutes'" 2>/dev/null || echo 0)
[ "${queued:-0}" -gt 0 ] && problems+=("посылок в очереди дольше 5 минут: $queued")

rcode=$(curl -s -o /dev/null -m 10 -w '%{http_code}' "$RUNNER" || true)
[ "$rcode" = 200 ] || problems+=("компилятор не отвечает (код $rcode)")

use=$(df -P / | awk 'NR==2 {gsub("%", "", $5); print $5}')
[ "$use" -ge 90 ] && problems+=("диск заполнен на ${use}%")

now=$(IFS='; '; echo "${problems[*]:-}")
before=$(cat "$STATE" 2>/dev/null || true)
[ "$now" = "$before" ] && exit 0
echo "$now" > "$STATE"

if [ -n "$now" ]; then text="olymp.oshsu.kg: $now"; else text="olymp.oshsu.kg: всё снова работает"; fi
echo "[$(date '+%F %T')] $text" >> "$LOG"
if [ -n "${TELEGRAM_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT:-}" ]; then
    curl -s -m 15 "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        --data-urlencode "chat_id=$TELEGRAM_CHAT" --data-urlencode "text=$text" > /dev/null || true
fi
