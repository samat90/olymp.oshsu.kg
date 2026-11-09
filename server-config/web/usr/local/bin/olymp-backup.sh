#!/bin/sh
# Daily dump of olymp DB and problem data; keeps 14 days.
set -e
umask 077
D=/var/backups/olymp/daily
mkdir -p $D
T=$(date +%Y%m%d-%H%M)
sudo -u postgres pg_dump -Fc olymp_oshsu > $D/db-$T.dump
tar -czf $D/problems-$T.tgz -C /var/www/olymp.oshsu.kg problems
find $D -type f -mtime +14 -delete
