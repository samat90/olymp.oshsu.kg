#!/bin/bash
# Writes a tar of this machine's settings to stdout, to compare them with git. Changes nothing.
# Secrets are left out (local_settings.py, judge keys, Telegram token, SSH keys).
#
#   ssh admin@10.10.8.226 'sudo bash -s' < scripts/server/collect_config.sh > web-config.tar
#   ssh admin@10.10.8.227 'sudo bash -s' < scripts/server/collect_config.sh > judge-config.tar
set -u
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
copy() { for p in "$@"; do [ -e "$p" ] && cp -a --parents "$p" "$out/" 2>/dev/null; done; }

copy /etc/nginx/nginx.conf /etc/nginx/sites-available /etc/nginx/sites-enabled /etc/nginx/conf.d
copy /etc/cron.d /etc/logrotate.d /etc/olymp/allowed_signers /etc/apt/apt.conf.d/20auto-upgrades
copy /etc/systemd/system/olymp* /etc/systemd/system/multi-user.target.wants /etc/systemd/system/timers.target.wants
copy /usr/local/bin/olymp* /usr/local/sbin/olymp*
copy /var/spool/cron/crontabs
mkdir -p "$out/info"
{
    echo "## hostname: $(hostname)"; echo "## date: $(date -Is)"
    echo "## sudo of admin:"; sudo -l -U admin 2>&1
    echo "## sudoers.d files:"; ls -la /etc/sudoers.d 2>&1
    echo "## olymp units:"; systemctl list-units --all --plain --no-legend 'olymp*' 2>&1
    echo "## timers:"; systemctl list-timers --all --no-pager 2>&1
    echo "## listening ports:"; ss -Hltnp 2>&1 | awk '{print $4, $6}'
    echo "## /etc/hosts:"; cat /etc/hosts
    echo "## python of the judge / site:"; ls /home/admin 2>&1
} > "$out/info/summary.txt"
# The judge configs without their keys.
for y in /home/admin/judge-config/*.yml; do
    [ -f "$y" ] && sed -E 's/^(key:).*/\1 <hidden>/' "$y" > "$out/info/$(basename "$y")"
done
# The site settings: only the names of the options, never the values.
[ -f /var/www/olymp.oshsu.kg/dmoj/local_settings.py ] && \
    grep -oE '^[A-Z_]+ *[=+]' /var/www/olymp.oshsu.kg/dmoj/local_settings.py | sort -u > "$out/info/local_settings.names"
# Remove anything that looks like a secret, whatever the file.
grep -rlE '(TELEGRAM_TOKEN|SECRET_KEY|PASSWORD|BEGIN [A-Z ]*PRIVATE KEY)' "$out" 2>/dev/null | xargs -r rm -f
tar cf - -C "$out" .
