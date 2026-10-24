# C# and UI rollout — 2026-09-28

Updated `olymp.oshsu.kg` (website) and `judge.oshsu.kg` (execution server).

- Microsoft SDK 10.0.112 / runtime 10.0.12, Roslyn C# 14.
- Website migration `0153_modern_csharp` applied; 7 existing Mono-enabled
  problems switched to CSHARP. The 14 historical Mono submissions are preserved.
- End-to-end browser submission [381](https://olymp.oshsu.kg/submission/381):
  **AC, 100/100**, all 5 tests passed, maximum per-test time 0.085 s, 29.98 MiB.
- Eight local Django tests passed, including language migration, fixture reload,
  rollback, preserved submission references, and existing registration tests.
- The Linux executor regression suite passed: modern syntax, Main, libraries,
  Unicode, cached binaries, CE/RTE, TLE/MLE, forbidden reads/writes/network/processes.
- Built both SCSS themes and checked JavaScript syntax. Browser checks covered
  desktop, 1024 px navigation, 390 px mobile layout, themes, C# selection,
  template loading, draft-save feedback, and keyboard menu controls.
- All four production services are active: web, bridge, event, judge.

## Backups

On both servers: `/var/backups/olymp/20260928-csharp-ui/` (root-only).
The website backup contains `database.dump`, `website-files.tgz`, and the
pre-existing uncommitted patch. The judge backup contains its original YAML and
systemd unit. Existing registration changes and the server-only problem-view
patch were retained.

For a rollback, restore website files from the archive, reverse migration 0153
with `manage.py migrate judge 0152`, restore the judge YAML, collect static files,
and restart web/judge. Reversing the migration preserves new C# submissions.
Restoring the whole database dump is only appropriate if newer production data
does not need to be retained.

## Local verification

The previous `venv` points to a removed Python 3.12 installation. A separate
`.venv` was created with the available Python 3.13 and project requirements.
Local UI data is in the ignored `ui-preview.sqlite3`, separate from production.

```powershell
.venv/Scripts/python.exe manage.py check --settings=dmoj.preview_settings
.venv/Scripts/python.exe manage.py test judge.models.tests.test_csharp judge.tests --settings=dmoj.preview_settings
.venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000 --settings=dmoj.preview_settings
```

The Windows preview is for UI/testing. Real sandboxed judging requires Linux.
