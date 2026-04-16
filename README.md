# OshSU Olymp

Онлайн-платформа для проведения олимпиад и тренировочных соревнований по программированию. Разработана в Ошском государственном университете (ОшГУ) на базе кафедры информационных систем и программирования (ИСП) МФТИТ.

Платформа построена на движке **[DMOJ](https://github.com/DMOJ/site)** (open source). Ребрендинг, дополнительная функциональность, локализация на три языка (ru/en/ky) — OshSU Olymp.

## Возможности

- Автоматическая проверка решений на **C, C++ (11–20), Java 8, Python 3**
- Соревнования в форматах **IOI** (частичные баллы) и **ACM/ICPC** (бинарно + штрафы)
- Живое табло результатов через WebSocket (event-daemon)
- Массовая генерация учётных записей участников (`/admin/generate-users/`)
- Тёмная тема с сохранением выбора пользователя
- Три языка интерфейса: русский, кыргызский, английский
- Адаптивный дизайн (десктоп + мобильные)

## Стек

- **Backend:** Django 4.2 + Python 3.12
- **DB:** PostgreSQL (prod) / SQLite (dev)
- **Cache + Celery broker:** Redis (prod)
- **Бридж судей:** TCP-сокеты (`judge/bridge/`)
- **Event-daemon:** Node.js websocket server (`websocket/daemon.js`)
- **Судья:** [DMOJ judge-server](https://github.com/DMOJ/judge-server) — отдельный процесс (Linux/WSL)
- **Frontend:** Jinja2 + SCSS → CSS (via `sass` + `postcss` + `autoprefixer`)

## Быстрый старт (dev)

```bash
# 1. Python окружение
python3.12 -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt

# 2. Локальные настройки
cp dmoj/prod_settings.py.example dmoj/local_settings.py
# Отредактируй local_settings.py (SECRET_KEY, DB и др.).
# Либо оставь как есть — dev по умолчанию SQLite.

# 3. База
python manage.py migrate
python manage.py loaddata navbar language_small

# 4. Суперпользователь
python manage.py createsuperuser

# 5. Статика
sh make_style.sh          # нужны sass, postcss-cli, autoprefixer глобально (npm i -g)
python manage.py collectstatic --noinput
python manage.py compilejsi18n

# 6. Переводы .po → .mo (без GNU gettext)
pip install Babel
python -c "from babel.messages.mofile import write_mo; from babel.messages.pofile import read_po; import os
for lang in ('ru','en','ky'):
    for po in ('django.po','djangojs.po','dmoj-user.po'):
        p = f'locale/{lang}/LC_MESSAGES/{po}'
        if os.path.isfile(p):
            with open(p,'rb') as f: c = read_po(f)
            with open(p[:-3]+'.mo','wb') as f: write_mo(f, c)"

# 7. Запуск (3 процесса)
python manage.py runbridged                   # окно 1 — bridge судей
python manage.py runserver 127.0.0.1:8000     # окно 2 — web
cd websocket && npm install ws simplesets qu  # разовая установка
node websocket/daemon.js                      # окно 3 — event daemon
```

## Судья (отдельная машина, Linux)

```bash
git clone --recursive https://github.com/DMOJ/judge-server.git
cd judge-server
python3 -m venv venv && source venv/bin/activate
pip install -e .

# Настройте ~/judge-config/judge.yml
# Запуск:
dmoj -c ~/judge-config/judge.yml -p 9999 --skip-self-test <BRIDGE_HOST>
```

## Админ-гайд

Для преподавателей/админов — пошаговая инструкция как провести олимпиаду: https://olymp.oshsu.kg/admin-guide/

## Полезные URL

- `/admin/` — админка
- `/admin/generate-users/` — массовая генерация учёток участников
- `/admin-guide/` — гайд для админов
- `/status/` — статус судей (не в меню, только по прямой ссылке)
- `/contest/<key>/` — страница соревнования
- `/contest/<key>/ranking/` — табло
- `/problems/` — архив задач
- `/problem/<code>/submit` — отправить решение

## Лицензия

DMOJ распространяется под [AGPL-3.0](LICENSE). Наши модификации наследуют ту же лицензию.

## Контакты

- Руководитель: **Карабаев С. Э.**, кафедра ИСП МФТИТ ОшГУ
- Email: <skarabaev@oshsu.kg>
- Сайт университета: [oshsu.kg](https://oshsu.kg)
