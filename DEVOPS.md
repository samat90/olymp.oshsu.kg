# Спецификация инфраструктуры для olymp.oshsu.kg

Документ для DevOps-команды: что нужно предоставить и настроить для развёртывания платформы OshSU Olymp на поддомене **olymp.oshsu.kg**.

---

## 1. Машины

### Машина #1 — Веб-сервер (обязательно)

| Параметр | Минимум | Рекомендуется |
|---|---|---|
| **CPU** | 2 vCPU | 4 vCPU |
| **RAM** | 4 GB | 8 GB |
| **Диск** | 30 GB SSD | 60 GB SSD |
| **ОС** | Ubuntu 22.04 / 24.04 LTS (x86_64) | Ubuntu 24.04 LTS |
| **Сеть** | публичный IPv4, доступ на 80/443 | + IPv6 |

**Что будет работать:**
- Nginx (reverse proxy + HTTPS + static/media)
- Python 3.12 + Django (Gunicorn/uWSGI, 4 worker)
- PostgreSQL 16 (БД)
- Redis 7 (кэш + Celery broker)
- Node.js 20 (event-daemon — websocket server)
- Celery worker (фоновые задачи Django)
- DMOJ bridge (`manage.py runbridged` — принимает подключения судей по TCP 9999)

---

### Машина #2 — Judge-сервер (обязательно, отдельная!)

Судья должен изолировать выполнение кода участников (сэндбокс seccomp, ptrace). **На одной машине с веб-сервером запускать НЕ рекомендуется** (если user-код вырвется из сэндбокса, он получит доступ к БД и секретам).

| Параметр | Минимум | Рекомендуется |
|---|---|---|
| **CPU** | 4 vCPU (с поддержкой виртуализации) | 8 vCPU |
| **RAM** | 4 GB | 8 GB |
| **Диск** | 20 GB SSD | 40 GB SSD |
| **ОС** | **Ubuntu 22.04/24.04 LTS** (только Linux! Ядро с seccomp/ptrace) | Ubuntu 24.04 LTS |
| **Сеть** | исходящий доступ к веб-серверу по 9999/TCP | — |

**Что будет работать:**
- DMOJ judge-server (`pip install -e` из https://github.com/DMOJ/judge-server)
- Компиляторы: `gcc`, `g++` (13+), `openjdk-8-jdk-headless`, `python3` (dev)
- Sandbox library: `libseccomp-dev`, `build-essential`
- Доступ к проблемным файлам: либо NFS/sshfs mount каталога `/var/www/olymp.oshsu.kg/problems` с веб-машины, либо rsync по расписанию

**Соединение с веб-сервером:** исходящее TCP 9999 на bridge веб-сервера. Никаких входящих портов на judge-машине не требуется.

---

## 2. Домены / DNS

- **`olymp.oshsu.kg`** — A-запись → IP веб-сервера
- **`www.olymp.oshsu.kg`** — CNAME → `olymp.oshsu.kg` (либо A-запись, редиректить на голый домен)

## 3. TLS / HTTPS

- **Let's Encrypt** через `certbot` (nginx plugin) — автоматическое продление раз в 60 дней
- **HSTS** включить: `max-age=31536000; includeSubDomains; preload`
- **Редирект HTTP → HTTPS** на уровне nginx

## 4. Порты

### На веб-сервере
| Порт | Протокол | Назначение | Доступ |
|---|---|---|---|
| 80 | TCP | HTTP (редирект на 443) | публичный |
| 443 | TCP | HTTPS | публичный |
| 22 | TCP | SSH | только с whitelist-адресов |
| 9999 | TCP | Judge bridge | **только с IP judge-сервера** |
| 5432 | TCP | PostgreSQL | только localhost |
| 6379 | TCP | Redis | только localhost |
| 9996-9998, 15100 | TCP | event-daemon + bridge (internal) | только localhost |
| 8000 | TCP | Gunicorn (за nginx) | только localhost |

### На judge-сервере
- Только **исходящее** TCP 9999 к веб-серверу
- SSH 22 для администрирования

---

## 5. Системный софт (веб-сервер)

```bash
# Пакеты (Ubuntu 24.04)
sudo apt install -y \
    nginx python3.12 python3.12-venv python3-pip \
    postgresql-16 postgresql-contrib \
    redis-server \
    nodejs npm \
    git build-essential libssl-dev libpq-dev \
    certbot python3-certbot-nginx \
    gettext libsass0 sass
```

Также глобально через npm: `sass`, `postcss-cli`, `autoprefixer` (для сборки стилей).

## 6. Приложение (веб-сервер) — пошаговый деплой

```bash
# 1. Клон + зависимости
sudo mkdir -p /var/www/olymp.oshsu.kg
sudo chown deploy:deploy /var/www/olymp.oshsu.kg
cd /var/www/olymp.oshsu.kg
git clone https://github.com/samat90/olymp.oshsu.kg.git .
git submodule update --init --recursive

python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# 2. БД
sudo -u postgres psql <<SQL
CREATE USER olymp WITH ENCRYPTED PASSWORD '<STRONG_PASSWORD>';
CREATE DATABASE olymp_oshsu OWNER olymp;
GRANT ALL PRIVILEGES ON DATABASE olymp_oshsu TO olymp;
SQL

# 3. Секретные ключи
cp dmoj/prod_settings.py.example dmoj/local_settings.py
cp .env.example .env
# заполнить .env значениями (DB_PASSWORD, SECRET_KEY, SMTP, …)
chmod 600 .env dmoj/local_settings.py

# 4. Миграции + статика + переводы
set -a; source .env; set +a
python manage.py migrate
python manage.py loaddata navbar language_small
sh make_style.sh
python manage.py collectstatic --noinput
python manage.py compilejsi18n
python -c "from babel.messages.mofile import write_mo; from babel.messages.pofile import read_po; import os
for lang in ('ru','en','ky'):
    for po in ('django.po','djangojs.po','dmoj-user.po'):
        p = f'locale/{lang}/LC_MESSAGES/{po}'
        if os.path.isfile(p):
            with open(p,'rb') as f: c = read_po(f)
            with open(p[:-3]+'.mo','wb') as f: write_mo(f, c)"

# 5. Суперпользователь (логин/пароль см. ниже)
python manage.py shell -c "
from django.contrib.auth.models import User
u = User.objects.create_superuser('samat1', 'olymp@oshsu.kg', 'UrMaTiK2017')
"

# 6. Websocket daemon
cd websocket && npm install ws simplesets qu && cd ..

# 7. Systemd сервисы (см. ниже)
sudo systemctl enable --now olymp-web olymp-bridge olymp-event olymp-celery
```

## 7. Systemd-юниты (на веб-сервере)

### `/etc/systemd/system/olymp-web.service`
```ini
[Unit]
Description=OshSU Olymp Django (gunicorn)
After=network.target postgresql.service

[Service]
User=deploy
WorkingDirectory=/var/www/olymp.oshsu.kg
EnvironmentFile=/var/www/olymp.oshsu.kg/.env
ExecStart=/var/www/olymp.oshsu.kg/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 dmoj.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/olymp-bridge.service`
```ini
[Unit]
Description=OshSU Olymp Judge Bridge
After=network.target postgresql.service

[Service]
User=deploy
WorkingDirectory=/var/www/olymp.oshsu.kg
EnvironmentFile=/var/www/olymp.oshsu.kg/.env
ExecStart=/var/www/olymp.oshsu.kg/venv/bin/python manage.py runbridged
Restart=always

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/olymp-event.service`
```ini
[Unit]
Description=OshSU Olymp Event Daemon (websocket)
After=network.target

[Service]
User=deploy
WorkingDirectory=/var/www/olymp.oshsu.kg/websocket
ExecStart=/usr/bin/node daemon.js
Restart=always

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/olymp-celery.service`
```ini
[Unit]
Description=OshSU Olymp Celery worker
After=network.target redis-server.service

[Service]
User=deploy
WorkingDirectory=/var/www/olymp.oshsu.kg
EnvironmentFile=/var/www/olymp.oshsu.kg/.env
ExecStart=/var/www/olymp.oshsu.kg/venv/bin/celery -A dmoj_celery worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

## 8. Nginx конфиг

`/etc/nginx/sites-available/olymp.oshsu.kg`:
```nginx
server {
    listen 80;
    server_name olymp.oshsu.kg www.olymp.oshsu.kg;
    return 301 https://olymp.oshsu.kg$request_uri;
}

server {
    listen 443 ssl http2;
    server_name olymp.oshsu.kg;

    ssl_certificate     /etc/letsencrypt/live/olymp.oshsu.kg/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/olymp.oshsu.kg/privkey.pem;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    client_max_body_size 5M;

    location /static/ { alias /var/www/olymp.oshsu.kg/static/; expires 30d; access_log off; }
    location /media/  { alias /var/www/olymp.oshsu.kg/media/;  expires 7d;  access_log off; }

    location /event/ {
        proxy_pass http://127.0.0.1:9996/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 24h;
    }

    location /channels/ {
        proxy_pass http://127.0.0.1:15100/;
        proxy_set_header Host $host;
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

## 9. Бэкапы

- **PostgreSQL:** `pg_dump olymp_oshsu > /backup/olymp_$(date +%F).sql.gz` — по крону каждый день
- **Media files** (`/var/www/olymp.oshsu.kg/media/`) — rsync на резервную машину раз в неделю
- **Problems** (`/var/www/olymp.oshsu.kg/problems/`) — то же самое
- Хранить бэкапы минимум 30 дней, с ротацией

## 10. Мониторинг / логи

- **Логи приложения:** `/var/log/olymp/django.log` (RotatingFileHandler в prod_settings.py)
- **Nginx access/error:** `/var/log/nginx/olymp.oshsu.kg.*.log`
- **Systemd:** `journalctl -u olymp-web -f`
- **Uptime-мониторинг:** любой внешний (UptimeRobot, Pingdom) — пинговать HTTPS GET `/`
- **Алерты:** email на `olymp@oshsu.kg` при 5xx ошибках (Django AdminEmailHandler настроен в prod_settings.py)

## 11. Доступы

### Для DevOps
- SSH-доступ на обе машины с публичным ключом (sudo-права)
- Доступ к `deploy` user на веб-машине (владелец `/var/www/olymp.oshsu.kg/`)

### Админ-аккаунт платформы
- URL: https://olymp.oshsu.kg/admin/login/
- Логин: **`samat1`**
- Пароль: **`UrMaTiK2017`**

(Заменить на реальный после первого входа!)

### SMTP (для email регистрации)
Нужен SMTP-аккаунт для отправки писем от `noreply@oshsu.kg`:
- Host / Port / SSL / User / Password — в `.env` как `DMOJ_SMTP_*`

---

## 12. Чек-лист для DevOps

- [ ] Две машины с указанными характеристиками
- [ ] DNS: A-запись `olymp.oshsu.kg` → веб-сервер
- [ ] Firewall на веб-сервере: открыты 80, 443 публично; 9999 только для judge-сервера
- [ ] Firewall на judge: только исходящее 9999
- [ ] SSL-сертификат Let's Encrypt
- [ ] PostgreSQL создан + secure password
- [ ] Приложение установлено по шагам выше
- [ ] 4 systemd-юнита активны (`olymp-web`, `olymp-bridge`, `olymp-event`, `olymp-celery`)
- [ ] Судья запущен на judge-машине и видит bridge (`netstat -an | grep 9999` показывает ESTABLISHED)
- [ ] Проверочный сабмит от `samat1`: задача A+B → AC
- [ ] Бэкапы PostgreSQL по расписанию
- [ ] Uptime-мониторинг настроен
- [ ] Email SMTP настроен, тест-письмо доходит

---

## Сомнения / что спросить у ответственного (Карабаев С. Э.)

1. **SMTP-аккаунт** — есть ли корпоративный `noreply@oshsu.kg`? Или использовать внешний (Yandex / Gmail)?
2. **Ограничение регистрации** — сейчас регистрация открыта всем. Может быть нужен whitelist по домену email (@oshsu.kg)?
3. **Нагрузка** — сколько одновременных участников ожидается на пике? От 100 до 500 — текущие характеристики ОК. От 500+ — нужно увеличить CPU/RAM или masштабировать judge горизонтально.
4. **Резервный судья** — для отказоустойчивости поставить второй judge-сервер и подключить к тому же bridge. Bridge автоматически распределит нагрузку.
5. **Мониторинг уровня Graylog/Grafana/Prometheus** — по желанию, не обязательно для MVP.
