#!/bin/bash
# Fails when a model change has no migration. Old code leaves "Alter field" noise (choices/help_text that
# do not change the database, see scripts/dev/strip_alterfields.py), so only other operations
# (new models, added/removed/renamed fields, ...) are an error.
#   DJANGO_SETTINGS_MODULE=dmoj.ci_settings scripts/dev/check_migrations.sh
set -uo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-python}
out=$("$PY" manage.py makemigrations --dry-run 2>&1)
rc=$?
if [ $rc -ne 0 ]; then
    echo "$out"
    exit $rc
fi
echo "$out"
bad=$(echo "$out" | grep -E '^\s+[-+~] ' | grep -vE '^\s+- Alter field ' || true)
if [ -n "$bad" ]; then
    echo "ERROR: models changed without a migration:"
    echo "$bad"
    exit 1
fi
echo "OK: no missing migrations (only no-op Alter field notes, if any)."
