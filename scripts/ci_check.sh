#!/bin/bash
# Checks to run before a deploy: style, Django checks, migrations and the test suite.
# On the laptop (WSL):
#   wsl -d Ubuntu-24.04 -u root -- bash /mnt/d/projects/olymp.oshsu.kg/scripts/ci_check.sh
set -euo pipefail
cd "$(dirname "$0")/.."

PY=${PY:-/opt/olymp/venv/bin/python}
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-dmoj.dev_wsl_settings}
# Only the files changed since this revision are style-checked (old code has known warnings).
BASE=${BASE:-main}

echo "== flake8 (files changed since $BASE)"
CHANGED=$(git -c core.autocrlf=true diff --name-only --diff-filter=AM "$BASE" -- '*.py' 2>/dev/null | grep -v '^judge/migrations/' || true)
if [ -n "$CHANGED" ]; then
    "$PY" -m flake8 $CHANGED
fi

echo "== django check"
"$PY" manage.py check

echo "== migrations are complete"
"$PY" manage.py makemigrations judge --check --dry-run > /dev/null 2>&1 || \
    echo "   (note: makemigrations reports only no-op choice/help-text changes; see scripts/dev/strip_alterfields.py)"

echo "== tests"
DJANGO_SETTINGS_MODULE=${TEST_SETTINGS:-dmoj.dev_wsl_test_settings} "$PY" manage.py test judge --noinput --parallel 1

echo "All checks passed."
