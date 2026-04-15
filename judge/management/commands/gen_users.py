"""Generate N participant accounts with random login/password.
Usage: manage.py gen_users 100 --prefix=olymp --out=credentials.csv
"""
import csv
import secrets
import string

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from judge.models import Profile, Language

SAFE_LETTERS = 'abcdefghjkmnpqrstuvwxyz'      # без i, l, o
SAFE_DIGITS = '23456789'                       # без 0, 1
SAFE_ALPHANUM = SAFE_LETTERS + SAFE_DIGITS


def make_login(prefix: str, serial: int) -> str:
    return f'{prefix}{serial:03d}'


def make_password(length: int = 8) -> str:
    return ''.join(secrets.choice(SAFE_ALPHANUM) for _ in range(length))


class Command(BaseCommand):
    help = 'Создать N участников с рандомными логинами и паролями.'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Количество пользователей для создания')
        parser.add_argument('--prefix', default='user', help='Префикс логина (default: user)')
        parser.add_argument('--password-length', type=int, default=8, help='Длина пароля')
        parser.add_argument('--out', default=None, help='Путь к CSV для записи (login, password)')
        parser.add_argument('--start', type=int, default=1, help='Начальный номер (default: 1)')
        parser.add_argument('--staff', action='store_true', help='Делать ли staff-пользователей')

    def handle(self, count, prefix, password_length, out, start, staff, **opts):
        if count < 1:
            raise CommandError('count должен быть >= 1')

        default_lang = Language.objects.filter(key='PY3').first() or Language.objects.first()

        created = []
        with transaction.atomic():
            serial = start
            while len(created) < count:
                login = make_login(prefix, serial)
                serial += 1
                if User.objects.filter(username=login).exists():
                    continue
                password = make_password(password_length)
                user = User.objects.create_user(
                    username=login,
                    password=password,
                    is_staff=staff,
                    is_active=True,
                )
                Profile.objects.create(
                    user=user,
                    language=default_lang,
                    timezone='Asia/Bishkek',
                )
                created.append((login, password))

        # Report
        self.stdout.write(self.style.SUCCESS(f'Создано {len(created)} пользователей.'))
        if out:
            with open(out, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['login', 'password'])
                for login, password in created:
                    writer.writerow([login, password])
            self.stdout.write(f'Учётные данные сохранены в {out}')
        else:
            self.stdout.write('\nlogin\tpassword')
            for login, password in created:
                self.stdout.write(f'{login}\t{password}')
