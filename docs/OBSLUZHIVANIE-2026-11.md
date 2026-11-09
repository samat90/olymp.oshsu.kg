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
`problems/`, ежедневные бэкапы, бэкап перед олимпиадой 21.10 и 10 последних бэкапов выката.
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
