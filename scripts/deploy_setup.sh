#!/bin/bash
# Deployment setup script — run on web server as admin (with sudo NOPASSWD).
# Args: SECRET_KEY DB_PASSWORD JUDGE_KEY ADMIN_URL
set -e

SECRET_KEY="$1"
DB_PASSWORD="$2"
JUDGE_KEY="$3"
ADMIN_URL="$4"

if [ -z "$SECRET_KEY" ] || [ -z "$DB_PASSWORD" ] || [ -z "$JUDGE_KEY" ] || [ -z "$ADMIN_URL" ]; then
    echo "Usage: $0 SECRET_KEY DB_PASSWORD JUDGE_KEY ADMIN_URL"
    exit 1
fi

PROJ=/var/www/olymp.oshsu.kg

echo "==> 1. Create directory and clone"
sudo mkdir -p $PROJ /var/log/olymp
sudo chown -R admin:admin $PROJ /var/log/olymp
cd $PROJ
if [ ! -d .git ]; then
    git clone https://github.com/samat90/olymp.oshsu.kg.git .
else
    git pull
fi

echo "==> 2. PostgreSQL"
sudo -u postgres psql -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='olymp') THEN CREATE USER olymp WITH PASSWORD '$DB_PASSWORD'; END IF; END \$\$;"
sudo -u postgres psql -c "ALTER USER olymp WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='olymp_oshsu'" | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE olymp_oshsu OWNER olymp ENCODING 'UTF8' LC_COLLATE 'C.UTF-8' LC_CTYPE 'C.UTF-8' TEMPLATE template0;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE olymp_oshsu TO olymp;"
sudo -u postgres psql -d olymp_oshsu -c "GRANT ALL ON SCHEMA public TO olymp;"

echo "==> 3. Tune postgresql.conf"
PGCONF=/etc/postgresql/16/main/postgresql.conf
if ! grep -q "# OshSU tuning" $PGCONF; then
    sudo tee -a $PGCONF >/dev/null << EOF

# OshSU tuning
max_connections = 500
shared_buffers = 1GB
effective_cache_size = 4GB
work_mem = 16MB
EOF
    sudo systemctl restart postgresql
fi

echo "==> 4. Python venv + deps"
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt gunicorn 2>&1 | tail -3

echo "==> 5. local_settings.py"
cat > $PROJ/dmoj/local_settings.py << EOF
"""Production settings for olymp.oshsu.kg."""
import os

SECRET_KEY = '$SECRET_KEY'
DEBUG = False
ALLOWED_HOSTS = ['olymp.oshsu.kg', 'www.olymp.oshsu.kg', 'localhost', '127.0.0.1', '10.10.8.226']

SECURE_SSL_REDIRECT = False  # nginx handles SSL termination
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
X_FRAME_OPTIONS = 'DENY'
CSRF_TRUSTED_ORIGINS = ['https://olymp.oshsu.kg']

ADMIN_URL_PREFIX = '$ADMIN_URL'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'olymp_oshsu',
        'USER': 'olymp',
        'PASSWORD': '$DB_PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 60,
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
    },
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

STATIC_ROOT = '$PROJ/static'
MEDIA_ROOT = '$PROJ/media'
MEDIA_URL = '/media/'

# Auth
REGISTRATION_OPEN = True
DMOJ_REQUIRE_STAFF_2FA = False
DMOJ_2FA_HARDCORE = False
WEBAUTHN_RP_ID = None
AUTH_PASSWORD_VALIDATORS = []  # OshSU: без ограничений для студентов

# Site
SITE_NAME = 'OshSU Olymp'
SITE_LONG_NAME = 'OshSU Olymp — Олимпиады по программированию ОшГУ'
SITE_ADMIN_EMAIL = 'skarabaev@oshsu.kg'
DEFAULT_FROM_EMAIL = 'OshSU Olymp <noreply@oshsu.kg>'
SERVER_EMAIL = 'noreply@oshsu.kg'
ADMINS = [('OshSU Olymp admin', 'skarabaev@oshsu.kg')]
DMOJ_SCHEME = 'https'
DMOJ_CANONICAL = 'olymp.oshsu.kg'

# Languages
from django.utils.translation import gettext_lazy as _
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Bishkek'
DEFAULT_USER_TIME_ZONE = 'Asia/Bishkek'
LANGUAGES = [
    ('ru', _('Русский')),
    ('en', _('English')),
    ('ky', _('Кыргызча')),
]

# Bridge / event
BRIDGED_JUDGE_ADDRESS = [('0.0.0.0', 9999)]  # accept from external judge
BRIDGED_DJANGO_ADDRESS = [('127.0.0.1', 9998)]
EVENT_DAEMON_USE = True
EVENT_DAEMON_POST = 'ws://127.0.0.1:9997/'
EVENT_DAEMON_GET = 'wss://olymp.oshsu.kg/event/'
EVENT_DAEMON_POLL = 'https://olymp.oshsu.kg/channels/'

# Celery (eager — no separate broker needed for now)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

DMOJ_PROBLEM_DATA_ROOT = '$PROJ/problems'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file_app': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/olymp/django.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django': {'handlers': ['file_app'], 'level': 'INFO'},
        'judge': {'handlers': ['file_app'], 'level': 'INFO'},
    },
}
EOF
chmod 600 $PROJ/dmoj/local_settings.py

echo "==> 6. Migrate + fixtures + superuser"
cd $PROJ
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=dmoj.settings
python manage.py migrate --noinput 2>&1 | tail -3
python manage.py loaddata navbar language_small 2>&1
python -c "
import django; django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='samat1').exists():
    u = User.objects.create_superuser('samat1', 'skarabaev@oshsu.kg', 'UrMaTiK2017')
    from judge.models import Profile, Language
    Profile.objects.get_or_create(user=u, defaults={'language': Language.get_default_language()})
    print('superuser created')
else:
    print('superuser exists')
"

# Create Judge record
python -c "
import django; django.setup()
from judge.models import Judge
j, c = Judge.objects.get_or_create(name='judge1', defaults={'auth_key': '$JUDGE_KEY', 'is_blocked': False, 'online': False})
if not c:
    j.auth_key = '$JUDGE_KEY'; j.save()
print('judge:', j.name)
"

echo "==> 7. Compile translations + collectstatic"
mkdir -p locale/ru/LC_MESSAGES locale/en/LC_MESSAGES locale/ky/LC_MESSAGES
python - << 'PY'
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
import os
for lang in ('ru','en','ky'):
    for po in ('django.po','djangojs.po','dmoj-user.po'):
        p = f'locale/{lang}/LC_MESSAGES/{po}'
        if os.path.isfile(p):
            with open(p,'rb') as f: c = read_po(f)
            with open(p[:-3]+'.mo','wb') as f: write_mo(f, c)
print('translations compiled')
PY

# SCSS via npm sass
sudo npm install -g sass postcss-cli autoprefixer 2>&1 | tail -2 || true
bash make_style.sh 2>&1 | tail -3

python manage.py compilejsi18n 2>&1 | tail -2
python manage.py collectstatic --noinput 2>&1 | tail -2

echo "==> 8. Done"
echo "DB password: $DB_PASSWORD"
echo "Judge key: $JUDGE_KEY"
echo "Admin URL: /$ADMIN_URL/"
