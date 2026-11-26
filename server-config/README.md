# Server settings kept in git

Files here are installed on the servers by the normal deploy, so they change through GitHub like the code:

- `web/<path>` goes to `/<path>` on olymp.oshsu.kg (`scripts/server/sync_system.sh`, at the end of `scripts/deploy.sh`);
- `judge/<path>` goes to `/<path>` on judge.oshsu.kg (`scripts/server/sync_judge.sh`, over SSH from the site).

Systemd units stay in `scripts/systemd/` (the lists of units for each machine are at the top of those two scripts).
Only files that differ are replaced; the old file is kept in a backup folder (see the scripts). nginx is checked with
`nginx -t` before the reload.

Small-VM tuning kept here: `etc/sysctl.d`, `etc/systemd/journald.conf.d`, `etc/nginx/nginx.conf` and
`etc/postgresql/16/main/conf.d/olymp.conf`. The sync does not restart PostgreSQL, journald or apply sysctl:
they take effect after a reboot. Settings appended to the end of `postgresql.conf` override `conf.d`.
Unused system services are turned off with `scripts/server/slim_services.sh`.

Never put secrets here (passwords, keys, `local_settings.py`): the repository is public.

See what differs from git without changing anything:

    bash scripts/server/sync_system.sh --check
    bash scripts/server/sync_judge.sh --check
