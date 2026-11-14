"""Compiles locale/*/LC_MESSAGES/*.po into .mo with Babel (no GNU gettext needed), as scripts/deploy.sh does.

Run from the repository root:  python scripts/dev/compile_translations.py
"""
import os

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

for lang in ('ru', 'en', 'ky'):
    for name in ('django.po', 'djangojs.po', 'dmoj-user.po'):
        path = os.path.join('locale', lang, 'LC_MESSAGES', name)
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                catalog = read_po(f)
            with open(path[:-3] + '.mo', 'wb') as f:
                write_mo(f, catalog)
