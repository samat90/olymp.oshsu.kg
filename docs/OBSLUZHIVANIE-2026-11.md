# Обслуживание серверов в ОшГУ (ноябрь 2026)

План на один выезд в сеть университета. Всё делается с ноутбука (D:\projects\olymp.oshsu.kg) по SSH:
сайт `admin@10.10.8.226`, судья `admin@10.10.8.227`. База данных не удаляется и не восстанавливается.
Перед каждым изменением делается бэкап. Если в этот момент идёт олимпиада, этапы 5–7 переносятся.

Время: около 1–1,5 часа, из них сайт недоступен только при перезагрузке, примерно 3–5 минут.

## 0. Перед началом

- Ноутбук в сети ОшГУ и на зарядке.
- `ssh -o ConnectTimeout=10 admin@10.10.8.226 true` и то же для `10.10.8.227` проходят.
- Ни одна олимпиада сейчас не идёт (это покажет этап 1).

## 1. Осмотр, ничего не меняется (5 минут)

```bash
cd /d/projects/olymp.oshsu.kg
D=/d/olymp-maint/$(date +%Y%m%d); mkdir -p $D
ssh admin@10.10.8.226 'sudo bash -s web' < scripts/server/status.sh | tee $D/web-status.txt
ssh admin@10.10.8.227 'sudo bash -s judge' < scripts/server/status.sh | tee $D/judge-status.txt
ssh admin@10.10.8.226 'tail -n 300 /var/log/olymp/deploy.log; ls -la ~/.autodeploy; systemctl status olymp-autodeploy --no-pager; journalctl -u olymp-autodeploy -n 40 --no-pager' > $D/deploy-log.txt
ssh admin@10.10.8.226 'sudo bash -s' < scripts/server/collect_config.sh > $D/web-config.tar
ssh admin@10.10.8.227 'sudo bash -s' < scripts/server/collect_config.sh > $D/judge-config.tar
```

Что ищем:

- почему не выкатился коммит e2f62b919 (50 тематических викторин): в `deploy-log.txt` будет одно из
  «GitHub is not reachable» (загрузка не успевает), «olympiad running» (держит контест),
  «не подписан», «выкат не удался», или запись обрывается на середине выката (служба убита по таймауту 30 минут);
- почему не добавилась 50-я олимпиадная задача «Самые далёкие юрты» (diameter): файл
  `/home/admin/problemsets/olymp2026.diameter.failed` и лог `/home/admin/problemsets-build/olymp2026/build-diameter.log` на judge;
- WARN-строки в отчётах, заполненность дисков, упавшие службы, есть ли у admin `sudo` без пароля.

## 2. Настройки серверов — в git (15 минут)

Распаковать `web-config.tar` и `judge-config.tar` и сравнить с репозиторием:

- живые юниты systemd (`/etc/systemd/system/olymp*`) с `scripts/systemd/`: где сервер новее, переносим правку в git;
- nginx (`/etc/nginx/sites-available/olymp.oshsu.kg`), cron (`/etc/cron.d/olymp-*`, crontab admin/root),
  скрипт ежедневного бэкапа (`/usr/local/bin/olymp-backup.sh` или где он лежит), rsync тестов на judge
  кладём в `server-config/web/<тот же путь>`; для judge — в `server-config/judge/<путь>`;
- секреты (local_settings.py, ключи, токены) в git НЕ кладём, collect_config.sh их и не собирает.

Цель: после этого `sync_system.sh --check` и `sync_judge.sh --check` показывают только задуманные изменения
(новый `TimeoutStartSec=4h` автовыката и logrotate для `/var/log/olymp`).

Если у admin нет `sudo` без пароля для `install`, `systemctl` и `nginx`, один раз добавить
`/etc/sudoers.d/olymp-deploy` (проверить `visudo -cf`), иначе синхронизация настроек будет только сообщать в лог.

## 3. Выкат накопившегося (15–30 минут)

1. Если загрузка с GitHub не успевает: запустить её заранее и посмотреть скорость
   `ssh admin@10.10.8.226 'time git --git-dir=/home/admin/olymp.git fetch https://github.com/samat90/olymp.oshsu.kg.git +refs/heads/main:refs/remotes/origin/main'`.
2. Подписанный коммит с ноутбука с этими исправлениями: `git push origin improvements-2026-10:main`.
3. `ssh admin@10.10.8.226 'sudo systemctl start --no-block olymp-autodeploy'` и следить: `tail -f /var/log/olymp/deploy.log`.
4. В конце выката: `sync_system`, `sync_runner`, `sync_judge` пишут, что поставили. Затем
   `ssh admin@10.10.8.226 'cat /var/www/olymp.oshsu.kg/.deployed-revision'` = последний коммит main.
5. Проверка: на сайте на 50 викторин больше, чем было, `/quiz/kosmos/` открывается, картинки видны.

## 4. 50-я олимпиадная задача

По логу сборки: исправить генератор/решение в `problemsets/olymp2026/diameter`, проверить локально,
закоммитить, удалить `/home/admin/problemsets/olymp2026.diameter.failed`. Следующий спокойный запуск
автовыката добавит задачу. Проверка: 50 задач набора на сайте, эталонное решение получает 100.

## 5. Чистка (10 минут)

```bash
ssh admin@10.10.8.226 'sudo bash /var/www/olymp.oshsu.kg/scripts/server/cleanup.sh web' | tee $D/web-cleanup-dry.txt
ssh admin@10.10.8.227 mkdir -p /tmp/olymp && scp scripts/server/cleanup.sh scripts/server/status.sh admin@10.10.8.227:/tmp/olymp/
ssh admin@10.10.8.227 'sudo bash /tmp/olymp/cleanup.sh judge' | tee $D/judge-cleanup-dry.txt
```

Просмотреть списки. Если всё в них лишнее, повторить с `--apply`. Скрипт никогда не трогает базу, `media/`,
`problems/`, ежедневный бэкап, копии, сделанные вручную, и последний бэкап выката (см. «Резервные копии»).
Пакеты из `apt autoremove` скрипт только показывает: убираем руками, если там старые ядра и ничего нужного.

## 6. Перезагрузка (10 минут)

Сначала судья, потом сайт (так посылки не теряются: пока сайт работает, судьи просто переподключаются).

```bash
ssh admin@10.10.8.226 "cd /var/www/olymp.oshsu.kg && venv/bin/python manage.py shell -c \"from judge.models import Submission as S; print(S.objects.filter(status__in=('QU','P','G')).count())\""   # должно быть 0
ssh admin@10.10.8.227 'sudo systemctl reboot'
# 1–2 минуты, затем:
ssh admin@10.10.8.227 'sudo bash /tmp/olymp/status.sh judge'
ssh admin@10.10.8.226 'sudo systemctl reboot'
# 2–3 минуты, затем:
ssh admin@10.10.8.226 'sudo bash /var/www/olymp.oshsu.kg/scripts/server/status.sh web'
```

После обеих перезагрузок все строки OK: службы, таймеры автовыката и публикации задач, судьи онлайн,
компилятор отвечает, нет посылок в очереди.

## 7. Проверка снаружи

- С ноутбука: главная, вход, задача → отправка решения на C++ и Python → «Принято», компилятор
  (ввод с клавиатуры), викторина «Космос» в режиме «С ведущим» с телефона по QR.
- Снаружи университета: телефон на мобильном интернете (не Wi-Fi ОшГУ) открывает сайт, вход работает,
  компилятор запускает Hello World. Вечером, когда ноутбук дома, повторяю проверку с ноутбука.
- Пробный коммит (только документация) с ноутбука выкатывается сам за 5–10 минут: значит, автовыкат жив.

## Большой коммит (больше 5 МБ)

Сервер скачивает с GitHub со скоростью около 10 КБ/с, и загрузка обрывается примерно через 20 минут, поэтому
коммит больше ~10 МБ (например, с картинками) сам не доедет. Так было с 50 викторинами 8–9 ноября.
Такой коммит привозится с ноутбука по сети ОшГУ: на ноутбуке `git bundle create main.bundle <выкаченный коммит>..main`,
файл копируется на сайт в /tmp, затем там
`sudo systemctl stop olymp-autodeploy` и запуск выката из файла:
`sudo systemd-run --uid=admin --unit=olymp-manual-deploy -p TimeoutStartSec=4h /bin/bash -c 'OLYMP_REMOTE=/tmp/main.bundle bash /var/www/olymp.oshsu.kg/scripts/server/autodeploy.sh >> /var/log/olymp/deploy.log 2>&1'`.
Тот же коммит должен быть и в GitHub main, тогда следующие загрузки с GitHub будут маленькими.

## Обслуживание 26.11.2026

Обе виртуальные машины: 2 ядра (Intel Xeon Gold 6152, 2,1 ГГц, гипервизор Microsoft), 3,8 ГБ памяти, Ubuntu 24.04.4.

| | сайт olymp | судья judge |
|---|---|---|
| диск | 126 ГБ, занято было 40 ГБ (33%), стало 18 ГБ (16%) | 63 ГБ, занято 14 ГБ (22%) |
| swap | 4 ГБ | 3,8 ГБ |
| средняя загрузка процессора за ночь и утро | около 6% | около 2% |
| память после перезагрузки (занято / доступно) | 1,0 / 2,8 ГБ | 0,5 / 3,3 ГБ |
| ядро после перезагрузки | 6.8.0-149 (ждала libc6) | 6.8.0-151 |

Что изменено:

- PostgreSQL: настройки перенесены в `conf.d/olymp.conf` (shared_buffers 384 МБ вместо 1 ГБ, max_connections 100
  вместо 500, effective_cache_size 2 ГБ вместо 4 ГБ при 3,8 ГБ памяти). База занимает 61 МБ.
- nginx: 4096 соединений на процесс вместо 768, лимит открытых файлов 8192, только TLS 1.2 и 1.3.
- swappiness 10; для Redis включён vm.overcommit_memory; системный журнал не больше 200 МБ.
- Выключены (не удалены) ModemManager, multipathd, fwupd, udisks2, snapd, motd-news, apport:
  `scripts/server/slim_services.sh`.
- Ежедневный бэкап: неизменившийся архив задач хранится один раз (жёсткая ссылка), поэтому `daily` занимает
  2,4 ГБ вместо 22 ГБ, все файлы на месте. Добавлена копия Redis (статистика посещений есть только там).
- Исправлена ротация логов: `health.log` принадлежал root, и logrotate завершался ошибкой.
- Чистка: журналы, кэш пакетов, 14 бэкапов выката старше 14 дней, папка сборки `kg2026/build`
  (все тесты из неё побайтно есть в рабочих архивах задач, остальное есть в `problemsets/kg2026`).
- Бэкап перед работами: `/var/backups/olymp/20261126-premaint`.

### Сертификат

Снаружи университета сайт отдаёт прокси со своим сертификатом Let's Encrypt (действует до 16.02.2027).
Внутри сети ОшГУ имя olymp.oshsu.kg ведёт прямо на сервер, там сертификат действует **до 19.12.2026** и сам не
продлится: прокси отвечает 404 на `/.well-known/acme-challenge/` и не передаёт эти запросы на сервер, поэтому
`certbot.service` завершается ошибкой. Нужно одно из двух от IT-службы:

1. на прокси передавать `http://olymp.oshsu.kg/.well-known/acme-challenge/` и то же для `www` на `10.10.8.226:80`;
2. или настроить внутренний DNS так, чтобы olymp.oshsu.kg вёл на прокси.

Первый вариант лучше: внутри сети остаётся прямое соединение с WebSocket. После изменения проверить на сайте
`sudo certbot renew --dry-run`.

## Резервные копии

На сайте хранится только последняя исправная копия: одна ежедневная и одна перед выкатом.

### Ежедневная копия

`/usr/local/bin/olymp-backup.sh` (в git: `server-config/web/usr/local/bin/olymp-backup.sh`, ставится обычным
выкатом), cron `/etc/cron.d/olymp-backup` в 03:30 UTC (09:30 по Бишкеку), лог `/var/log/olymp-backup.log`.
Копия лежит в `/var/backups/olymp/daily`:

| Файл | Что внутри | Проверка до удаления прежней копии |
|---|---|---|
| `db-ГГГГММДД-ЧЧММ.dump` | вся база PostgreSQL | не меньше 1 МБ, `pg_restore` читает архив целиком, есть таблица пользователей, не меньше половины прежней копии |
| `problems-ГГГГММДД-ЧЧММ.tgz` | `problems/` (тесты задач) | архив читается целиком, файлов не меньше, чем в папке, папка не пустая |
| `media-ГГГГММДД-ЧЧММ.tgz` | `media/` (загруженные через сайт файлы: аватары, картинки викторин, курсов и редактора, работы учеников) | как для задач; пока файлов нет и прежней копии нет, это не ошибка |
| `redis-ГГГГММДД-ЧЧММ.rdb` | Redis (статистика посещений есть только там) | `redis-cli save` ответил OK, `redis-check-rdb` |

Новая копия пишется в файл `*.part` и получает своё имя только после проверки; прежняя копия того же вида
удаляется, когда новая записана на диск (`sync`). Если копия не создалась или не прошла проверку, прежняя
остаётся, в логе появляется строка `ERROR:`, скрипт завершается с кодом 1. Четыре вида копий независимы: сбой одного
не мешает остальным. Неизменившийся архив задач или `media/` не записывается второй раз: новое имя получает тот же
файл на диске.

Удаляются только файлы с именами точно такого вида в `daily`. Папки `20261021-preolymp`, `20261126-premaint` и
другие копии, сделанные вручную, скрипт не трогает.

Защита от пустой копии: если дамп базы, архив задач или архив `media/` стал меньше половины прежнего, либо в Redis стало вдвое
меньше ключей статистики посещений (их число записано в `daily/redis-visit-keys`), хранятся две копии: прежняя
исправная и самая новая, а в логе стоит `ERROR:`. Убедившись, что на сайте всё в порядке и уменьшение настоящее,
запустить `sudo OLYMP_ACCEPT_SHRINK=1 /usr/local/bin/olymp-backup.sh`.

Проверить: `tail -n 20 /var/log/olymp-backup.log; sudo ls -la /var/backups/olymp/daily`.

Код, статика, пакеты Python, внешние библиотеки и кэши в ежедневную копию не входят: код лежит в git, остальное
собирает `scripts/deploy.sh`. Не входит в неё также `dmoj/local_settings.py` (секреты, в git их нет): он есть в копии
перед выкатом.

Копия на судью (`scripts/server/backup_offsite.sh`, если для неё настроен cron) хранится там по своим правилам: 30 дней.

### Копия перед выкатом

`scripts/deploy.sh` перед каждым выкатом пишет в `/var/backups/olymp/deploy/<дата-время>` дамп базы и архив кода
(с `local_settings.py`). Когда сайт после выката отвечает, `scripts/server/prune_deploy_backups.sh` проверяет новую
копию и только потом удаляет более старые папки с именем вида `ГГГГММДД-ЧЧММСС`. Если новый дамп базы меньше
половины прежнего, прежняя копия тоже остаётся. Если выкат не удался или копия не
прошла проверку, не удаляется ничего.

### Восстановление

Перед восстановлением снять копию того, что есть сейчас, в отдельную папку: ежедневный и следующий бэкап выката
заменят прежние. Файлы копий доступны только через `sudo`. Вместо `<файл>` подставить имя из `daily`.

База (всё, что появилось после копии, пропадёт):

```bash
sudo mkdir -p /var/backups/olymp/before-restore
sudo -u postgres pg_dump -Fc olymp_oshsu | sudo tee /var/backups/olymp/before-restore/database.dump > /dev/null
sudo systemctl stop olymp-web olymp-bridge
sudo cat /var/backups/olymp/daily/<файл>.dump | sudo -u postgres pg_restore --clean --if-exists -d olymp_oshsu
sudo systemctl start olymp-web olymp-bridge
```

Тесты задач (файлы из копии заменят одноимённые, остальные останутся; на судью они уедут обычной синхронизацией):

```bash
sudo tar -xzf /var/backups/olymp/daily/problems-<дата>.tgz -C /var/www/olymp.oshsu.kg
```

Одну задачу: в конце той же команды добавить `problems/<код задачи>`.

Загруженные через сайт файлы (так же: файлы из копии заменят одноимённые, остальные останутся; для одного файла
в конце команды добавить его путь, например `media/avatars/<имя>`):

```bash
sudo tar -xzf /var/backups/olymp/daily/media-<дата>.tgz -C /var/www/olymp.oshsu.kg
```

Redis (заменяет всё, что в нём сейчас):

```bash
sudo systemctl stop redis-server
sudo install -o redis -g redis -m 660 /var/backups/olymp/daily/<файл>.rdb /var/lib/redis/dump.rdb
sudo systemctl start redis-server
```

Код после неудачного выката: `bash scripts/rollback.sh /var/backups/olymp/deploy/<дата-время>`; с `--database`
восстанавливается и база (состояние перед этим выкатом).

