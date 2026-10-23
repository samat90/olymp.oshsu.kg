#!/bin/sh
# Run after applying Django migrations; install the publication timer.
set -eu
cd /var/www/olymp.oshsu.kg
sudo install -m 644 scripts/systemd/olymp-publish-problems.service /etc/systemd/system/
sudo install -m 644 scripts/systemd/olymp-publish-problems.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now olymp-publish-problems.timer
sudo systemctl start olymp-publish-problems.service
