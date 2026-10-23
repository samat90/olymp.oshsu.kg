# Доработка после StudExpo 2026 (ход работы)

Ветка `improvements-2026-10`, только локально. На сервер и GitHub не выкатывать, Самат обновит сервер из ОшГУ.

## Локальный стенд (WSL Ubuntu-24.04)

- Запуск: `wsl -d Ubuntu-24.04 -u root -- bash /mnt/d/projects/olymp.oshsu.kg/scripts/dev/wsl_start.sh`
- Сайт http://127.0.0.1:8000, настройки `dmoj.dev_wsl_settings`, база — копия с сервера от 21.10 (`D:/olymp-backups/20261021-preolymp`).
- Судья local1 (`/opt/judge/judge.yml`, judge-server в `/opt/judge`), служба запуска кода `runner/server.py` на :9910.
- Тестовые аккаунты и команды: `scripts/dev/README.md`.
- Тесты: `DJANGO_SETTINGS_MODULE=dmoj.dev_wsl_settings /opt/olymp/venv/bin/python manage.py test judge`
- Monaco скачивается `scripts/fetch_vendor.sh` в `resources/vendor/` (не в git).

## Сделано

- [x] IOI/ICPC/AtCoder и LockModel под PostgreSQL + тесты
- [x] Языки JavaScript (Node 22), Go, Kotlin, Free Pascal (миграция 0159)
- [x] Служба запуска кода `runner/server.py`
- [x] Редактор Monaco на странице отправки: запуск, проверка на примерах, настройки
- [x] Песочница: файлы и папки (модель WorkspaceFile, миграция 0160), API, тесты
- [x] Песочница: проверка интерфейса в браузере
- [x] Защита от списывания (вкладки, 3 предупреждения, журнал, вставка извне)
- [x] Итоги сразу: публичный рейтинг после окончания, Excel, университет (организации), «+15 минут»
- [x] Админка: автозаполнение тестов, авто-ID (была ошибка в get_readonly_fields), главная админки, импорт задачи
- [x] Дизайн (resources/modern.css)
- [x] Балансировщик и CI/CD: scripts/deploy.sh, rollback.sh, ci_check.sh, docs/DEPLOY-2026-10.md (выкат отрепетирован в WSL)
- [x] Общая проверка: 150 тестов проходят
- [ ] Выкат на сервер (Самат, из ОшГУ)
- [ ] PascalABC.NET (пока Free Pascal)

## Что важно помнить

- На проде Node нужно ставить 22 (в Node 18 `readFileSync(0)` падает в песочнице DMOJ).
- На проде judge-языки: C, C++17, Java 8, Python 3.14, C# (.NET 10). Новые языки требуют установки на judge.oshsu.kg.
- Коды задач на проде уже шестизначные (DMOJ_NUMERIC_PROBLEM_CODES = True).
