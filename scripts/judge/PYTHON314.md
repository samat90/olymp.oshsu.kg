# CPython 3.14.7 for submissions

Version selected from the official stable release list on 28 September 2026:
https://www.python.org/downloads/release/python-3147/

`install_python314.sh` builds official CPython in `/opt/python/3.14.7`, verifying
the SHA-256 checksum before extraction. It does not replace the system Python or
the virtual environments running Django and the judge service.

Run `test_python314_executor.py` with the judge-server virtual environment before
changing production. It checks the exact interpreter version, template strings
introduced in Python 3.14, standard libraries including Zstandard, Unicode,
compilation/runtime errors, resource limits, and filesystem/network/process isolation.

After the suite passes, merge these entries into the judge YAML while preserving
all other runtime and filesystem entries:

```yaml
runtime:
  python3: /opt/python/3.14.7/bin/python3.14
extra_fs:
  PY3:
    - recursive_dir: /opt/python/3.14.7
```

The filesystem entry grants read access to this interpreter distribution only.
It does not grant writes or access to judge configuration or test data.

Restart `olymp-judge`, verify its PY3 self-test and advertised runtime version,
then apply website migration 0155. The existing `PY3` language identity remains
unchanged; every problem permits it, and existing language permissions remain.
The site receives the actual runtime version from the judge handshake.

For rollback, restore `judge.yml` from
`/var/backups/olymp/20260928-python314/` and restart `olymp-judge`.
Reverse website migration 0155 to restore the old display label. Reversal keeps
Python access enabled and does not delete languages, submissions or results.

## Deployment verification, 28 September 2026

Both servers were updated. All 1035 problems permit PY3 and have an online judge
advertising `python3 3.14.7`. The site displays `Python 3.14` (short label `Py 3.14`).
The sandbox regression suite and Django migration regression test passed.
Submission https://olymp.oshsu.kg/submission/383 asserts the exact Python version
and uses a Python 3.14 template string: **AC, 100/100**. Browser verification
confirmed the live language selector shows the new name and runtime version.
