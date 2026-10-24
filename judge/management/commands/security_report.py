from django.conf import settings
from django.core.management.base import BaseCommand

KNOWN_KEYS = (
    '5*9f5q57mqmlz2#f$x1h76&jxy#yortjl1v+l*6hd18$d*yx#0',
    'dev-only-secret-key-change-me-in-production-please',
)


class Command(BaseCommand):
    help = 'Warn about unsafe production settings (run on the server after a deploy).'

    def handle(self, *args, **options):
        problems = []
        if settings.DEBUG:
            problems.append('DEBUG = True: error pages show settings and code to anyone. Set DEBUG = False.')
        if settings.SECRET_KEY in KNOWN_KEYS or len(settings.SECRET_KEY) < 40:
            problems.append('SECRET_KEY is a default or short key: sessions can be forged. Generate a new one.')
        if '*' in settings.ALLOWED_HOSTS:
            problems.append("ALLOWED_HOSTS = ['*']: list the real names, e.g. ['olymp.oshsu.kg', '10.10.8.226'].")
        if not getattr(settings, 'DMOJ_RUNNER_SECRET', None) and not getattr(settings, 'DMOJ_RUNNER_SECRET_FILE', None):
            problems.append('The code runner has no shared secret.')
        if not settings.SESSION_COOKIE_HTTPONLY:
            problems.append('SESSION_COOKIE_HTTPONLY is off.')

        for line in problems:
            self.stdout.write('WARNING: ' + line)
        if not problems:
            self.stdout.write('Security settings: OK')
