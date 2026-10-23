# Локальная копия сайта на ноутбуке (WSL)

Запуск (PowerShell или cmd):

```
wsl -d Ubuntu-24.04 -u root -- bash /mnt/d/projects/olymp.oshsu.kg/scripts/dev/wsl_start.sh
```

Сайт: http://127.0.0.1:8000. Запускаются сайт, мост судей, судья `local1` и служба запуска кода.
База — копия с сервера от 21.10.2026 (`D:/olymp-backups/20261021-preolymp/database.dump`), только для проверки.

Тестовые аккаунты (существуют только в локальной базе):

| логин | пароль | роль |
|---|---|---|
| devadmin | devadmin-local-2026 | суперпользователь |
| devstudent | devstudent-local-2026 | участник «Тестовой олимпиады» (`/contest/devtest`) |

Автотесты и проверки перед выкатом:

```
wsl -d Ubuntu-24.04 -u root -- bash /mnt/d/projects/olymp.oshsu.kg/scripts/ci_check.sh
```

Переводы: новые строки добавляются в `scripts/dev/translations.json`, затем
`/opt/olymp/venv/bin/python scripts/dev/add_translations.py scripts/dev/translations.json` (в WSL).
