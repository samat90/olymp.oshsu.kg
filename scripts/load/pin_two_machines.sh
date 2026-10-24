# Emulate two machines on the laptop: "web" = CPUs 0-4 (gunicorn, postgres, redis), "judge" = CPUs 5-8 (judges, runner)
for p in $(pgrep -f postgres) $(pgrep redis-server); do taskset -a -cp 0-4 $p > /dev/null; done
for p in $(pgrep -f 'dmoj -c') $(pgrep -f 'runner/server.py'); do taskset -a -cp 5-8 $p > /dev/null; done
# abort leftover queue from the previous run
sudo -u postgres psql -d olymp_oshsu -At -c "update judge_submission set status='AB', result='AB' where status in ('QU','P','G')"
pgrep -fa 'dmoj -c' | wc -l
