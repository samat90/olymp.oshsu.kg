# Развёртывание olymp.oshsu.kg

Документ для того, кто будет ставить платформу на сервер. Я буду называть его «ты» — это проще, чем писать «DevOps-инженер» в каждом абзаце.

Код живёт здесь: <https://github.com/samat90/olymp.oshsu.kg>. Ветка `main`. Это форк DMOJ с нашими правками (ребрендинг, три языка интерфейса, авто-активация регистраций, выключенные 2FA/WebAuthn).

Я собрал всё, что тебе понадобится знать. Если найдёшь ошибку в этом документе — поправь его тем же PR'ом.

---

## 1. Зачем нужны две машины

Судья DMOJ исполняет чужой код. Даже с seccomp и ptrace-песочницей есть ненулевой шанс, что кто-то найдёт способ из неё выйти. Если это случится и судья стоит на том же хосте, что и БД — можно потерять всё.

Поэтому **судья живёт отдельно**. Веб-машина и judge-машина общаются по одному TCP-порту, и судье вообще не нужен прямой доступ к БД, Redis или статике.

Минимальный сетап:

- **Web** — Django, PostgreSQL, Redis, Celery, nginx, event-daemon. Один хост.
- **Judge** — только judge-server. Один хост, ставится по инструкции из <https://github.com/DMOJ/judge-server>.

Если ожидается >500 одновременных пользователей, БД можно вынести на отдельный хост, но это не обязательно для старта.

## 2. Железо

Ориентировочно для 100–500 одновременных пользователей:

**Web-сервер:**
- 4 vCPU, 8 GB RAM, 60 GB SSD
- Ubuntu 22.04 или 24.04 LTS (x86_64)
- Публичный IPv4, открытые порты 80/443

**Judge-сервер:**
- 4 vCPU (с поддержкой виртуализации — seccomp/ptrace требуют нормального Linux-ядра), 4 GB RAM, 40 GB SSD
- Ubuntu 22.04/24.04 LTS. **Только Linux**, не BSD и не контейнер без CAP_SYS_ADMIN.
- Только исходящий доступ к web-хосту по TCP/9999. Входящих открытых портов не нужно.

Если у вас уже есть виртуалки, эти цифры — потолок, обычно работает и на половине.

## 3. Сеть

DNS: `olymp.oshsu.kg` → A-запись на IP web-сервера. `www.olymp.oshsu.kg` — CNAME на голый домен (мы с него редиректим).

TLS: Let's Encrypt через certbot с nginx-плагином. Обновление кроном раз в 60 дней, ничего особенного.

Файрволл на web-сервере:

| Порт | Откуда пускать | Зачем |
|------|----------------|-------|
| 80, 443 | весь мир | http/https |
| 22 | только с whitelist-адресов | ssh |
| 9999 | **только с IP judge-сервера** | bridge для судьи |
| 5432, 6379, 9996–9998, 15100 | только localhost | внутренние сервисы |

На judge-сервере открывать извне нечего. SSH — если планируется удалённое администрирование.

Важно: 9999 открытый «всему миру» — это дыра. Ограничь `iptables` или правилом security-group.

## 4. Что ставить на web-сервер

```bash
apt install -y \
  nginx \
  python3.12 python3.12-venv python3-pip \
  postgresql-16 postgresql-contrib \
  redis-server \
  nodejs npm \
  git build-essential libssl-dev libpq-dev \
  certbot python3-certbot-nginx \
  gettext
```

Плюс глобально через npm: `sass`, `postcss-cli`, `autoprefixer` (нужны на этапе сборки стилей, не на рантайме).

## 5. Установка приложения

Я исхожу из того, что deploy-юзер называется `deploy` и код лежит в `/var/www/olymp.oshsu.kg`. Пути в systemd-юнитах ниже соответствуют этим предположениям — если меняешь, поправь и там.

### 5.1 Код и зависимости

```bash
mkdir -p /var/www/olymp.oshsu.kg
chown deploy:deploy /var/www/olymp.oshsu.kg
sudo -u deploy -i

cd /var/www/olymp.oshsu.kg
git clone https://github.com/samat90/olymp.oshsu.kg.git .
git submodule update --init --recursive

python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn
```

### 5.2 База

```bash
sudo -u postgres psql <<SQL
CREATE USER olymp WITH ENCRYPTED PASSWORD '<SECRETOM_IZ_PAROLJ_MANEGERA>';
CREATE DATABASE olymp_oshsu OWNER olymp ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8' TEMPLATE template0;
GRANT ALL PRIVILEGES ON DATABASE olymp_oshsu TO olymp;
SQL
```

Пароль кидай в пароль-менеджер сразу — потом достать неоткуда.

**Настройка PostgreSQL для нагрузки.** Дефолтный `max_connections = 100` маловат при 100+ участниках. В `/etc/postgresql/16/main/postgresql.conf`:

```conf
max_connections = 500
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 16MB
```

После правки: `systemctl restart postgresql`.

### 5.3 Конфиг

```bash
cp dmoj/prod_settings.py.example dmoj/local_settings.py
cp .env.example .env
chmod 600 dmoj/local_settings.py .env
```

В `.env` нужно заполнить:
- `DMOJ_SECRET_KEY` — 50+ случайных символов, `python -c 'import secrets; print(secrets.token_urlsafe(64))'`
- `DMOJ_DB_PASSWORD` — тот же, что выдал PostgreSQL выше
- `DMOJ_SMTP_*` — если есть `noreply@oshsu.kg`. Если нет, оставь пусто — письма сейчас не критичны, в коде уже отключено подтверждение email на регистрации.

Переменные подгружаются в `local_settings.py` через `os.environ[...]`, так что `.env` надо экспортировать в окружение systemd-юнита (`EnvironmentFile=`, см. ниже).

### 5.4 Миграции, статика, переводы

```bash
set -a; source .env; set +a
export DJANGO_SETTINGS_MODULE=dmoj.settings

python manage.py migrate
python manage.py loaddata navbar language_small

# Статика
bash make_style.sh
python manage.py collectstatic --noinput
python manage.py compilejsi18n

# Переводы .po → .mo. В проекте нет GNU gettext, используем Babel:
python - <<'PY'
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
import os
for lang in ('ru', 'en', 'ky'):
    for po in ('django.po', 'djangojs.po', 'dmoj-user.po'):
        p = f'locale/{lang}/LC_MESSAGES/{po}'
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                c = read_po(f)
            with open(p[:-3] + '.mo', 'wb') as f:
                write_mo(f, c)
PY
```

Если `compilemessages` от Django найдёт локальный `msgfmt` — можно использовать его, результат тот же.

### 5.5 Суперюзер

Логин и начальный пароль согласован с Саматом:
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.create_superuser('samat1', 'skarabaev@oshsu.kg', 'UrMaTiK2017')
"
```
**Первым делом после деплоя зайди под этим юзером и смени пароль.** Я не оставляю его в чате навечно — смысл тот, что дефолт надо перебить.

### 5.6 WebSocket daemon

```bash
cd websocket && npm install ws simplesets qu && cd ..
```

Дальше он запустится через systemd (`olymp-event.service`), см. ниже.

## 6. Systemd

Четыре сервиса, все под юзером `deploy`, все с `Restart=always`.

**`/etc/systemd/system/olymp-web.service`**
```ini
[Unit]
Description=OshSU Olymp — Django (gunicorn)
After=network.target postgresql.service redis-server.service

[Service]
User=deploy
Group=deploy
WorkingDirectory=/var/www/olymp.oshsu.kg
EnvironmentFile=/var/www/olymp.oshsu.kg/.env
Environment=DJANGO_SETTINGS_MODULE=dmoj.settings
ExecStart=/var/www/olymp.oshsu.kg/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 --access-logfile - dmoj.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/olymp-bridge.service`** — связь с судьёй:
```ini
[Unit]
Description=OshSU Olymp — Judge Bridge
After=network.target postgresql.service

[Service]
User=deploy
WorkingDirectory=/var/www/olymp.oshsu.kg
EnvironmentFile=/var/www/olymp.oshsu.kg/.env
Environment=DJANGO_SETTINGS_MODULE=dmoj.settings
ExecStart=/var/www/olymp.oshsu.kg/venv/bin/python manage.py runbridged
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/olymp-event.service`** — websocket для live-обновлений:
```ini
[Unit]
Description=OshSU Olymp — Event Daemon (websocket)
After=network.target

[Service]
User=deploy
WorkingDirectory=/var/www/olymp.oshsu.kg/websocket
ExecStart=/usr/bin/node daemon.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/olymp-celery.service`** — фоновые задачи:
```ini
[Unit]
Description=OshSU Olymp — Celery worker
After=network.target redis-server.service

[Service]
User=deploy
WorkingDirectory=/var/www/olymp.oshsu.kg
EnvironmentFile=/var/www/olymp.oshsu.kg/.env
Environment=DJANGO_SETTINGS_MODULE=dmoj.settings
ExecStart=/var/www/olymp.oshsu.kg/venv/bin/celery -A dmoj_celery worker -l info --concurrency=2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Активация:
```bash
systemctl daemon-reload
systemctl enable --now olymp-web olymp-bridge olymp-event olymp-celery
systemctl status olymp-*
```

## 7. Nginx

`/etc/nginx/sites-available/olymp.oshsu.kg`:

```nginx
# Лимит на брутфорс логина/регистрации.
limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;

server {
    listen 80;
    listen [::]:80;
    server_name olymp.oshsu.kg www.olymp.oshsu.kg;
    return 301 https://olymp.oshsu.kg$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name olymp.oshsu.kg;

    ssl_certificate     /etc/letsencrypt/live/olymp.oshsu.kg/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/olymp.oshsu.kg/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;

    client_max_body_size 5M;
    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;

    location /static/ {
        alias /var/www/olymp.oshsu.kg/static/;
        expires 30d;
        access_log off;
    }

    location /media/ {
        alias /var/www/olymp.oshsu.kg/media/;
        expires 7d;
        access_log off;
    }

    # WebSocket daemon.
    location /event/ {
        proxy_pass http://127.0.0.1:9996/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 24h;
    }
    location /channels/ {
        proxy_pass http://127.0.0.1:15100/;
        proxy_set_header Host $host;
    }

    # Rate-limit на брутфорс логина и регистрации.
    location ~ ^/(accounts/login|accounts/register)/ {
        limit_req zone=auth burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активация:
```bash
ln -s /etc/nginx/sites-available/olymp.oshsu.kg /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
certbot --nginx -d olymp.oshsu.kg -d www.olymp.oshsu.kg
```

## 8. Судья (вторая машина)

```bash
# На judge-сервере, от sudo-юзера.
apt install -y gcc g++ openjdk-8-jdk-headless python3 python3-dev \
                mono-devel mono-complete \
                libseccomp-dev build-essential git

adduser --disabled-password --gecos '' judge
sudo -u judge -i

git clone --recursive https://github.com/DMOJ/judge-server.git ~/judge-server
cd ~/judge-server
python3 -m venv venv && source venv/bin/activate
pip install -e .

mkdir ~/judge-config
cat > ~/judge-config/judge.yml <<YAML
id: judge1
key: <GENERATE_RANDOM_STRING_AND_PUT_IN_DB_TOO>

runtime:
  gcc: /usr/bin/gcc
  g++: /usr/bin/g++
  g++11: /usr/bin/g++
  g++14: /usr/bin/g++
  g++17: /usr/bin/g++
  g++20: /usr/bin/g++
  python3: /usr/bin/python3
  java8: /usr/lib/jvm/java-8-openjdk-amd64/bin/java
  javac8: /usr/lib/jvm/java-8-openjdk-amd64/bin/javac
  mono-csc: /usr/bin/mono-csc
  mono: /usr/bin/mono
  mcs: /usr/bin/mcs

problem_storage_globs:
  - /home/judge/problems/*
YAML

# Проверь self-test:
dmoj -c ~/judge-config/judge.yml --self-test

# Запуск (через systemd тоже можно сделать unit):
dmoj -c ~/judge-config/judge.yml -p 9999 <WEB_HOST_IP>
```

**Задачи** (`/home/judge/problems/*`) синхронизируй с веб-машины. Простой вариант — rsync по cron раз в минуту. Если хочется мгновенно — NFS-mount `/var/www/olymp.oshsu.kg/problems` read-only. Судья не должен писать в этот каталог.

Перед первым запуском в админке веб-платформы создай запись Judge (`/<ADMIN_URL>/judge/judge/add/`) и скопируй auth-key в judge.yml.

## 9. Бэкапы

Минимум что надо бэкапить:

```bash
# БД — ежедневно.
pg_dump -U olymp olymp_oshsu | gzip > /backup/db/olymp_$(date +%F).sql.gz

# Media (аватары, прикреплённые файлы) — еженедельно.
rsync -a /var/www/olymp.oshsu.kg/media/ /backup/media/

# Задачи — еженедельно.
rsync -a /var/www/olymp.oshsu.kg/problems/ /backup/problems/
```

Храни минимум 30 дней, с ротацией. Проверь хотя бы раз, что dump можно восстановить — «бэкап, который ни разу не тестировали, не бэкап».

## 10. Мониторинг

Не обязательно сразу ставить Grafana/Prometheus. Минимум:

- UptimeRobot (или любой внешний пинг) на `https://olymp.oshsu.kg/` — раз в 5 минут.
- `journalctl -u olymp-*` — когда что-то падает.
- Алерт на email `skarabaev@oshsu.kg` при 5xx — это уже настроено в `prod_settings.py` через `AdminEmailHandler`.

Логи nginx: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`. Django: `/var/log/olymp/django.log` (папку не забудь создать и дать права `deploy:deploy`).

## 11. Безопасность — короткий чек

Я уже постарался сделать prod-настройки правильными, но глазами тоже проверь:

- [ ] `DEBUG = False` (в `prod_settings.py`, остаётся)
- [ ] `ALLOWED_HOSTS = ['olymp.oshsu.kg', 'www.olymp.oshsu.kg']` — только прод-домены
- [ ] `SECRET_KEY` в `.env`, не в репозитории
- [ ] HTTPS везде, HSTS на год, cookie с `Secure` — всё в `prod_settings.py`
- [ ] PostgreSQL доступна только с localhost (`pg_hba.conf`)
- [ ] Redis слушает только localhost (дефолт Ubuntu)
- [ ] Порт 9999 только с IP judge-сервера (firewall)
- [ ] `certbot renew --dry-run` проходит
- [ ] На админке `/<ADMIN_URL>/login/` нет дефолтных кредов — после первого логина поменяй пароль `samat1`
- [ ] Nginx rate-limit на `/accounts/login/` и `/accounts/register/` активен (см. конфиг выше)

Пароли участников валидируются только по длине (≥6 символов). Это компромисс: у нас олимпиада, а не банк — сложность отталкивает студентов. Если ситуация изменится — `AUTH_PASSWORD_VALIDATORS` в `prod_settings.py`.

2FA для staff выключена (`DMOJ_REQUIRE_STAFF_2FA = False`). Если захотим включить — надо поднимать отдельный TOTP-setup flow; это не MVP-задача.

## 12. Что передать назад Самату

Когда всё запустится, напиши мне:

1. Публичный IP веб-сервера
2. Статус certbot (есть ли валидный сертификат)
3. IP judge-сервера — чтобы можно было настроить `auth_key` и проверить, что коннект прошёл
4. Доступ к админке — залогинился ли `samat1` и удалось ли создать тестовую посылку

## 13. Открытые вопросы

На эти я не уверен, решим вместе:

1. **SMTP.** Есть ли корпоративный `noreply@oshsu.kg`? Если нет — нужен внешний (Yandex/Gmail app password). Пока SMTP не настроен, регистрация работает без email-подтверждения: это осознанное решение.
2. **Whitelist домена в регистрации.** Сейчас регистрация открыта всем. Если нужно ограничить только `@oshsu.kg` — скажи, добавлю валидатор.
3. **Второй судья.** Для отказоустойчивости можно подключить второй judge-сервер к тому же bridge — нагрузка распределится автоматически. Нужно?
4. **Автоматический deploy.** Сейчас `git pull + systemd restart` руками. Если ожидаются частые правки — можно GitHub Actions + webhook. Думаю, на первое время руками хватит.
